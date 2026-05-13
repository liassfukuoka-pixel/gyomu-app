import imaplib
from dotenv import load_dotenv
import os

load_dotenv()

accounts = [
    ('imap.goope.jp', os.getenv('OUTLOOK_ADDRESS'), os.getenv('OUTLOOK_PASSWORD')),
    ('imap.goope.jp', os.getenv('OUTLOOK_ADDRESS2'), os.getenv('OUTLOOK_PASSWORD2')),
]

for server, addr, pwd in accounts:
    print(f"\nテスト: {addr}")
    try:
        mail = imaplib.IMAP4_SSL(server, 993)
        result = mail.login(addr, pwd)
        print(f"✅ ログイン成功: {result}")
        mail.logout()
    except Exception as e:
        print(f"❌ エラー: {e}")