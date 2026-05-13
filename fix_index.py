f = open('templates/index.html', 'rb')
c = f.read()
f.close()

old = b'<a href="/order/{{ o.id }}/edit"'
new = b'<a href="/pdf/{{ o.id }}" target="_blank" class="btn btn-sm btn-outline-info">PDF</a>\n              <a href="/order/{{ o.id }}/edit"'

c = c.replace(old, new)
f = open('templates/index.html', 'wb')
f.write(c)
f.close()
print('OK')