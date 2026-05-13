import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import sqlite3
import os

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

mail = imaplib.IMAP4_SSL('imap.goope.jp', 993)
mail.login('service@liass.jp', 'liass0777')
mail.select('inbox')

since_date = (datetime.now() - timedelta(days=90)).strftime("%d-%b-%Y")
_, messages = mail.search(None, f'SINCE {since_date}')
mail_ids = messages[0].split()

conn = sqlite3.connect('instance/gyomu.db')
cursor = conn.cursor()
cursor.execute('SELECT management_no FROM "order"')
registered = set(row[0] for row in cursor.fetchall())
conn.close()

print(f"登録済み管理番号数: {len(registered)}")
print(f"メール件数: {len(mail_ids)}")

new_count = 0
skip_count = 0
for mail_id in mail_ids:
    _, msg_data = mail.fetch(mail_id, '(RFC822)')
    msg = email.message_from_bytes(msg_data[0][1])
    for part in msg.walk():
        if part.get_content_type() == 'application/pdf':
            filename = decode_str(part.get_filename() or '')
            management_no = os.path.splitext(filename)[0]
            if management_no in registered:
                skip_count += 1
            else:
                new_count += 1
                print(f"新規: {filename}")

mail.logout()
print(f"\n新規: {new_count}件 / スキップ: {skip_count}件")