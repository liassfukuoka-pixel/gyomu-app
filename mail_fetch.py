import imaplib
import email
import os
import time
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
UPLOAD_FOLDER = 'uploads'

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

def fetch_gmail_pdfs():
    print("Gmailに接続中...")
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        mail.select('inbox')

        _, messages = mail.search(None, 'UNSEEN')
        mail_ids = messages[0].split()

        if not mail_ids:
            print("新着メールはありません")
            mail.logout()
            return []

        saved_files = []
        for mail_id in mail_ids:
            _, msg_data = mail.fetch(mail_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            from_addr = decode_str(msg.get('From', ''))
            domain = ''
            if '@' in from_addr:
                domain = from_addr.split('@')[-1].replace('>', '').strip()

            print(f"送信元: {from_addr} / ドメイン: {domain}")

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

                    print(f"保存: {filepath}")
                    saved_files.append({
                        'filepath': filepath,
                        'filename': filename,
                        'domain': domain
                    })

        mail.logout()
        return saved_files

    except Exception as e:
        print(f"Gmailエラー: {e}")
        return []

def fetch_outlook_pdfs():
    OUTLOOK_ADDRESS = os.getenv('OUTLOOK_ADDRESS', '')
    OUTLOOK_PASSWORD = os.getenv('OUTLOOK_PASSWORD', '')

    if not OUTLOOK_ADDRESS or not OUTLOOK_PASSWORD:
        print("Outlookの設定がありません。スキップします。")
        return []

    print("Outlookに接続中...")
    try:
        mail = imaplib.IMAP4_SSL('outlook.office365.com')
        mail.login(OUTLOOK_ADDRESS, OUTLOOK_PASSWORD)
        mail.select('inbox')

        _, messages = mail.search(None, 'UNSEEN')
        mail_ids = messages[0].split()

        if not mail_ids:
            print("Outlook: 新着メールはありません")
            mail.logout()
            return []

        saved_files = []
        for mail_id in mail_ids:
            _, msg_data = mail.fetch(mail_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            from_addr = decode_str(msg.get('From', ''))
            domain = ''
            if '@' in from_addr:
                domain = from_addr.split('@')[-1].replace('>', '').strip()

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

                    print(f"保存: {filepath}")
                    saved_files.append({
                        'filepath': filepath,
                        'filename': filename,
                        'domain': domain
                    })

        mail.logout()
        return saved_files

    except Exception as e:
        print(f"Outlookエラー: {e}")
        return []

if __name__ == '__main__':
    print("メール取込を開始します...")
    gmail_files = fetch_gmail_pdfs()
    outlook_files = fetch_outlook_pdfs()
    all_files = gmail_files + outlook_files
    print(f"\n合計 {len(all_files)} 件のPDFを取込みました")
    for f in all_files:
        print(f"  - {f['filename']} (ドメイン: {f['domain']})")