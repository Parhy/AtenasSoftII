from flask import Flask, render_template, request, url_for, redirect, flash, session
from datetime import datetime
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'atenas'
mysql = MySQL(app)

app.secret_key = 'mysecretkey'

sesion = 0    #0 = sin sesión // 1 = cliente // 2 = operario
id_cliente = 0

@app.route("/")
@app.route("/home")
def index():
	global sesion
	global documento
	cur = mysql.connection.cursor()
	cur.execute('SELECT id, nombre FROM municipio')
	municipios = cur.fetchall()
	cur.execute('SELECT p.tipo, p.tamaño, p.peso, m.nombre, e.direccion, p.descripcion FROM envio e JOIN producto p ON e.id_producto = p.id JOIN municipio m ON e.id_municipio = m.id WHERE e.id_cliente = "%s"' % id_cliente)
	envios = cur.fetchall()
	return render_template('vista_menu.html', municipios = municipios, sesion = sesion, envios = envios)

@app.route("/login", methods=['POST'])
def login():
	if request.method == 'POST':
		global sesion
		global id_cliente
		documento = request.form['input-documento']
		cur = mysql.connection.cursor()
		cur.execute('SELECT id FROM cliente WHERE documento = "%s"' % documento)
		data = cur.fetchall()[0]
		try:
			if data[0]:
				flash('Has iniciado sesion')
				id_cliente = data[0]
				sesion = 1
		except:
			flash('Este documento no se encuentra registrado')
	return redirect(url_for('index'))

@app.route("/signup", methods=['POST'])
def signup():
	if request.method == 'POST':
		global sesion
		global id_cliente
		documento = request.form['input-documento']
		cur = mysql.connection.cursor()
		cur.execute('SELECT * FROM cliente WHERE documento = "%s"' % documento)
		data = cur.fetchall()
		try:
			if data[0]:				
				flash('Este documento se encuentra registrado')
				return redirect(url_for('index'))
		except:
			nombre = request.form['input-nombre']
			direccion = request.form['input-direccion']
			telefono = request.form['input-telefono']
			correo = request.form['input-correo']
			cur.execute('INSERT INTO cliente (documento, nombre, direccion, telefono, correo) values ("%s", "%s", "%s", "%s", "%s")' %
					(documento, nombre, direccion, telefono, correo))
			mysql.connection.commit()
		cur = mysql.connection.cursor()
		cur.execute('SELECT id FROM cliente WHERE documento = "%s"' % documento)
		id_cliente = cur.fetchall()[0][0]
		flash('Te has registrado satisfactoriamente')
		sesion = 1
		
	return redirect(url_for('index'))

@app.route("/cotizacion", methods=['POST'])
def cotizacion():
	global id_cliente
	global sesion
	session.pop('Registro de envío exitoso', None)
	session.pop('Has iniciado sesion', None)
	session.pop('Te has registrado satisfactoriamente', None)
	session.pop('Este documento se encuentra registrado', None)
	session.pop('Este documento no se encuentra registrado', None)
	if request.method == 'POST':
		tipo = request.form['select-tipo']
		medida = request.form['input-medida1'] + 'x' + request.form['input-medida2'] + 'x' + request.form['input-medida3']
		peso = request.form['input-peso']
		destino = request.form['select-destino']
		direccion = request.form['input-direccion']
		descripcion = request.form['textarea-descripcion']

		cur = mysql.connection.cursor()
		cur.execute('INSERT INTO producto (tipo, tamaño, peso, descripcion) values ("%s", "%s", "%s", "%s")' %
			(tipo, medida, peso, descripcion))

		cur.execute('SELECT id FROM producto WHERE tipo = "%s" AND tamaño = "%s" AND peso = "%s" AND descripcion = "%s"' %
			(tipo, medida, peso, descripcion))

		id_producto = cur.fetchall()[0][0]

		cur.execute('INSERT INTO envio (direccion, id_producto, id_cliente, id_municipio) values ("%s", "%s", "%s", "%s")' %
			(direccion, id_producto, id_cliente, destino))
		mysql.connection.commit()
		flash('Registro de envío exitoso')
		sesion = 0
	return redirect(url_for('index'))

if __name__ == "__main__":
	app.run(debug=True)