f = open('app.py', 'r', encoding='utf-8')
c = f.read()
f.close()

# worker_nameフィールドを追加
c = c.replace(
    "tantou = db.Column(db.String(100))",
    "tantou = db.Column(db.String(100))\n    worker_name = db.Column(db.String(100))"
)

# 検索をユーザー名・管理番号両対応に
c = c.replace(
    "orders = Order.query.filter(Order.management_no.contains(query)).all()",
    "orders = Order.query.filter(db.or_(Order.management_no.contains(query), Order.user_name.contains(query))).all()"
)

f = open('app.py', 'w', encoding='utf-8')
f.write(c)
f.close()
print('OK')