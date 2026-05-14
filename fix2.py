f = open('app.py', 'r', encoding='utf-8')
c = f.read()
f.close()

# 完了報告ルートを追加
new_routes = '''
@app.route('/order/<int:order_id>/complete', methods=['GET', 'POST'])
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    if request.method == 'POST':
        order.worker_name = request.form.get('worker_name', '')
        order.completed_at = request.form.get('completed_at', '')
        db.session.commit()
        flash('完了報告を保存しました', 'success')
        return redirect(url_for('index'))
    return render_template('complete_order.html', order=order)

@app.route('/completed')
def completed_orders():
    orders = Order.query.filter(Order.completed_at != None).filter(Order.completed_at != '').order_by(Order.completed_at.desc()).all()
    return render_template('completed.html', orders=orders)
'''

# delete_orderの前に追加
c = c.replace(
    "@app.route('/order/<int:order_id>/delete'",
    new_routes + "\n@app.route('/order/<int:order_id>/delete'"
)

f = open('app.py', 'w', encoding='utf-8')
f.write(c)
f.close()
print('OK')