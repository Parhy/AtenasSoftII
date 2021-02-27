from flask import Flask, render_template, request, url_for, redirect, flash, session
from datetime import datetime
from flask_mysqldb import MySQL

import hashlib

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
	cur = mysql.connection.cursor()
	cur.execute('SELECT id, nombre FROM municipio ORDER BY nombre')
	municipios = cur.fetchall()
	if(sesion == 1):
		cur.execute('SELECT p.tipo, p.tamaño, p.peso, m.nombre, e.direccion, e.fecha, p.descripcion FROM envio e JOIN producto p ON e.id_producto = p.id JOIN municipio m ON e.id_municipio = m.id WHERE e.id_cliente = "%s"' % id_cliente)
	elif(sesion == 2):
		cur.execute('SELECT p.tipo, c.documento, p.tamaño, p.peso, m.nombre, e.direccion, e.fecha, p.descripcion FROM envio e JOIN producto p ON e.id_producto = p.id JOIN municipio m ON e.id_municipio = m.id JOIN cliente c ON e.id_cliente = c.id')
	envios = cur.fetchall()
	return render_template('vista_menu.html', municipios = municipios, sesion = sesion, envios = envios)

@app.route("/login", methods=['POST'])
def login():
	if request.method == 'POST':
		global sesion
		global id_cliente
		documento = request.form['input-documento']
		cur = mysql.connection.cursor()
		print(request.form['select-usuario'])
		if(request.form['select-usuario'] == "0"):
			cur.execute('SELECT id FROM cliente WHERE documento = "%s"' % documento)
			try:
				data = cur.fetchall()[0]
				if data[0]:
					flash('Has iniciado sesion')
					id_cliente = data[0]
					sesion = 1
			except:
				flash('Este documento no se encuentra registrado')
		elif(request.form['select-usuario'] == "1"):
			contraseña = hashlib.md5(hashlib.md5(hashlib.md5(request.form['input-contraseña'].encode("utf-8")).hexdigest().encode("utf-8")).hexdigest().encode("utf-8")).hexdigest()
			cur.execute('SELECT id FROM operario WHERE documento = "%s" AND contraseña = "%s"' % (documento, contraseña))
			try:
				data = cur.fetchall()[0]
				if data[0]:
					flash('Has iniciado sesion')
					sesion = 2
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

@app.route("/logout", methods=['POST'])
def logout():
	global sesion
	global id_cliente
	if request.method == 'POST':
		id_cliente = 0
		sesion = 0
	return redirect(url_for('index'))

@app.route("/solicitar_envio", methods=['POST'])
def enviar():
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
		documento = request.form['input-documento']

		cur = mysql.connection.cursor()
		cur.execute('INSERT INTO producto (tipo, tamaño, peso, descripcion) values ("%s", "%s", "%s", "%s")' %
			(tipo, medida, peso, descripcion))

		cur.execute('SELECT id FROM producto WHERE tipo = "%s" AND tamaño = "%s" AND peso = "%s" AND descripcion = "%s"' %
			(tipo, medida, peso, descripcion))

		id_producto = cur.fetchall()[0][0]

		cur.execute('SELECT id FROM cliente WHERE documento = "%s"' % (documento))

		id_cliente = cur.fetchall()[0][0]

		cur.execute('INSERT INTO envio (direccion, id_producto, id_cliente, id_municipio) values ("%s", "%s", "%s", "%s")' %
			(direccion, id_producto, id_cliente, destino))
		mysql.connection.commit()
		flash('Registro de envío exitoso')
		sesion = 0
	return redirect(url_for('index'))

@app.route("/buscar_envios", methods=['POST'])
def buscar_envios():
	if(request.method == 'POST'):
		documento = request.form['input-documento']
		cur = mysql.connection.cursor()
		cur.execute('SELECT * FROM cliente WHERE documento = "%s"' % documento)

if __name__ == "__main__":
	app.run(debug=True)