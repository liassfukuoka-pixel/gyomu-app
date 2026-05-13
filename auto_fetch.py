# -*- coding: utf-8 -*-
import os, sys, json, imaplib, email, sqlite3
from email.header import decode_header
from datetime import datetime
from dotenv import load_dotenv
import anthropic
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

load_dotenv(override=True)

UPLOAD_FOLDER = 'uploads'
DB_PATH = os.path.join('instance', 'gyomu.db')

def log(msg):
    now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(f"[{now}] {msg}")

def decode_str(s):
    if s is None:
        return ''
    decoded = decode_header(s)
    result = ''
    for part, enc in decoded:
        if isinstance(part, bytes):
            result += part.decode(enc or 'utf-8', errors='ignore')
        else:
            result += part
    return result

def extract_pdf_info(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        ai_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        message = ai_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": "以下の依頼書テキストから情報を抽出してください。必ずJSON形式のみで返答してください。\n{\"request_date\": \"依頼日\", \"work_content\": \"作業内容\", \"amount\": \"金額\", \"tantou\": \"担当者\", \"user_name\": \"ユーザー名\", \"work_place\": \"作業場所\"}\n依頼書テキスト：\n" + text[:3000]
            }]
        )
        text_response = message.content[0].text.strip()
        text_response = text_response.replace('```json', '').replace('```', '').strip()
        return json.loads(text_response)
    except Exception as e:
        log(f"AIエラー: {e}")
        return {"request_date": "", "work_content": "", "amount": "", "tantou": "", "user_name": "", "work_place": ""}

def get_registered_nos():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT management_no FROM "order"')
        nos = set(row[0] for row in cursor.fetchall())
        conn.close()
        return nos
    except:
        return set()

def get_clients():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email_domain FROM client')
        clients = {row[2]: {'id': row[0], 'name': row[1]} for row in cursor.fetchall()}
        conn.close()
        return clients
    except:
        return {}

def register_order(management_no, client_id, filename, info, amount):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO "order" (management_no, client_id, filename, work_content, amount, tantou, request_date, user_name, work_place, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (management_no, client_id, filename, info.get('work_content', ''), amount, info.get('tantou', ''), info.get('request_date', ''), info.get('user_name', ''), info.get('work_place', ''), datetime.now()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log(f"DB登録エラー: {e}")
        return False

def fetch_unseen_pdfs(imap_server, address, password):
    results = []
    try:
        mail = imaplib.IMAP4_SSL(imap_server, 993)
        mail.login(address, password)
        mail.select('inbox')
        _, messages = mail.search(None, 'UNSEEN')
        mail_ids = messages[0].split()
        if not mail_ids:
            mail.logout()
            return []
        log(f"{address}: 未読 {len(mail_ids)}件")
        for mail_id in mail_ids:
            _, msg_data = mail.fetch(mail_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            from_addr = decode_str(msg.get('From', ''))
            domain = from_addr.split('@')[-1].split('>')[0].strip().lower() if '@' in from_addr else ''
            for part in msg.walk():
                if part.get_content_type() == 'application/pdf':
                    filename = decode_str(part.get_filename())
                    if not filename:
                        continue
                    folder = os.path.join(UPLOAD_FOLDER, 'mail_inbox')
                    os.makedirs(folder, exist_ok=True)
                    filepath = os.path.join(folder, filename)
                    with open(filepath, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    results.append({'filepath': filepath, 'filename': filename, 'domain': domain})
                    log(f"PDF取得: {filename}")
        mail.logout()
    except Exception as e:
        log(f"メールエラー ({address}): {e}")
    return results

def main():
    log("=== 自動取込 開始 ===")
    all_files = []
    gmail_addr = os.getenv('GMAIL_ADDRESS', '')
    gmail_pass = os.getenv('GMAIL_APP_PASSWORD', '')
    if gmail_addr and gmail_pass:
        all_files += fetch_unseen_pdfs('imap.gmail.com', gmail_addr, gmail_pass)
    outlook_addr = os.getenv('OUTLOOK_ADDRESS', '')
    outlook_pass = os.getenv('OUTLOOK_PASSWORD', '')
    if outlook_addr and outlook_pass:
        all_files += fetch_unseen_pdfs('imap.goope.jp', outlook_addr, outlook_pass)
    outlook_addr2 = os.getenv('OUTLOOK_ADDRESS2', '')
    outlook_pass2 = os.getenv('OUTLOOK_PASSWORD2', '')
    if outlook_addr2 and outlook_pass2:
        all_files += fetch_unseen_pdfs('imap.goope.jp', outlook_addr2, outlook_pass2)
    if not all_files:
        log("新着PDFなし")
        log("=== 終了 ===")
        return
    registered_nos = get_registered_nos()
    clients = get_clients()
    count = 0
    skip = 0
    for f in all_files:
        client = clients.get(f['domain'])
        if not client:
            log(f"未登録ドメイン: {f['domain']}")
            continue
        management_no = os.path.splitext(f['filename'])[0].split('_')[0].split('.')[0]
        if management_no in registered_nos:
            skip += 1
            continue
        folder = os.path.join(UPLOAD_FOLDER, client['name'])
        os.makedirs(folder, exist_ok=True)
        dest = os.path.join(folder, f['filename'])
        try:
            os.rename(f['filepath'], dest)
        except:
            dest = f['filepath']
        info = extract_pdf_info(dest)
        amount = 0
        try:
            amount = float(str(info.get('amount', '0')).replace(',', '').replace('円', '') or 0)
        except:
            amount = 0
        if register_order(management_no, client['id'], f['filename'], info, amount):
            count += 1
            log(f"登録完了: {management_no} ({client['name']})")
            registered_nos.add(management_no)
    log(f"=== 終了: {count}件登録、{skip}件スキップ ===")

if __name__ == '__main__':
    main()