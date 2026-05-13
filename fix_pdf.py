f = open('app.py', 'rb')
c = f.read()
f.close()

old = b"@app.route('/search')"
new = b"""@app.route('/pdf/<int:order_id>')
def view_pdf(order_id):
    order = Order.query.get_or_404(order_id)
    folder = os.path.join(app.config['UPLOAD_FOLDER'], order.client.name)
    filepath = os.path.join(folder, order.filename)
    return send_file(filepath, mimetype='application/pdf')

@app.route('/search')"""

c = c.replace(old, new)
f = open('app.py', 'wb')
f.write(c)
f.close()
print('OK')