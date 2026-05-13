import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta

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

registered = {'araidenki.com', 'iyama-auto.co.jp', 'corolla-hakata.co.jp'}

match = 0
no_match = 0
for mail_id in mail_ids[:20]:
    _, msg_data = mail.fetch(mail_id, '(RFC822)')
    msg = email.message_from_bytes(msg_data[0][1])
    from_addr = decode_str(msg.get('From', ''))
    domain = from_addr.split('@')[-1].split('>')[0].strip().lower() if '@' in from_addr else ''
    has_pdf = any(part.get_content_type() == 'application/pdf' for part in msg.walk())
    if has_pdf:
        if domain in registered:
            match += 1
            print(f"✅ マッチ: {domain}")
        else:
            no_match += 1
            print(f"❌ 不一致: [{domain}]")

mail.logout()
print(f"\nマッチ: {match}件 / 不一致: {no_match}件")