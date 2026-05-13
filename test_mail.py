import imaplib

print("テスト1: SSL ポート993")
try:
    mail = imaplib.IMAP4_SSL('imap.goope.jp', 993)
    print("接続OK")
    result = mail.login('service@liass.jp', 'liass0777')
    print(f"ログインOK: {result}")
    mail.logout()
except Exception as e:
    print(f"失敗: {e}")

print("\nテスト2: 非SSL ポート143")
try:
    mail = imaplib.IMAP4('imap.goope.jp', 143)
    print("接続OK")
    result = mail.login('service@liass.jp', 'liass0777')
    print(f"ログインOK: {result}")
    mail.logout()
except Exception as e:
    print(f"失敗: {e}")

print("\nテスト3: STARTTLSポート143")
try:
    mail = imaplib.IMAP4('imap.goope.jp', 143)
    mail.starttls()
    print("接続OK")
    result = mail.login('service@liass.jp', 'liass0777')
    print(f"ログインOK: {result}")
    mail.logout()
except Exception as e:
    print(f"失敗: {e}")