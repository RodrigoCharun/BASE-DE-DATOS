from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from datetime import date
import webbrowser

app=Flask(__name__)


#nos conectamos a MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'trabajofinal'
mysql=MySQL(app)

app.secret_key = 'mysecretkey' #permite agregar mensaje

##############################################################################################################################
@app.route('/')  #creamos nuestra primera ruta
def Index():
	cur = mysql.connection.cursor()
	cur.execute('select * from articulos order by nombre')
	data = cur.fetchall()
	return render_template('index.html', articulos = data)
#############################################################################################################################
@app.route('/agregar_dato')
def agregar_dato():
	cur = mysql.connection.cursor()
	cur.execute('select * from articulos order by nombre')
	data = cur.fetchall()
	return render_template('agregar.html', articulos = data)


@app.route('/agregar', methods=['POST'])
def agregar():
	if request.method == 'POST':
		nombre = request.form['nombre']
		precio = request.form['precio']
		cantidad = request.form['cantidad']
		reordenar = request.form['reordenar']
		if nombre =="" or precio=="" or cantidad =="" or reordenar=="":
			flash("recuerda llenar los datos de los campos")
			return redirect(url_for('agregar_dato'))

		hoy=date.today()
		cur = mysql.connection.cursor()
		cur.execute('select * from articulos where (nombre= %s and precio=%s and reordenar=%s)',(nombre,precio,reordenar))
		if cur.fetchone() is None:
			cur.execute('INSERT INTO articulos (nombre,precio,cantidad,reordenar) VALUES (%s,%s,%s,%s)',(nombre,precio,cantidad,reordenar))
		else:
			cur.execute('''
			UPDATE articulos
			SET
				cantidad =(SELECT cantidad FROM articulos where nombre=%s and precio=%s and reordenar=%s)+%s 
			WHERE (nombre= %s and precio=%s and reordenar=%s)
			''',(nombre,precio,reordenar,cantidad,nombre,precio,reordenar))



		cur.execute('select articulo_id from articulos where nombre= %s and precio=%s and reordenar=%s',(nombre,precio,reordenar))
		art_id=cur.fetchall()
		cur.execute('insert into transaccion (fecha, cantidad, tipo, articulo_nombre, articulo_id) VALUES (%s,%s,%s,%s,%s)',(hoy, cantidad, 'ingreso',nombre,art_id[0]))
		mysql.connection.commit()		
		
		return redirect(url_for('agregar_dato'))
##########################################################################################################################################################################

@app.route('/editar_dato/<id>')
def obtener_articulo(id):
	cur = mysql.connection.cursor()
	cur.execute(f'SELECT * FROM articulos WHERE articulo_id={id} ')
	data = cur.fetchall()
	return render_template('editar-articulo.html', articulo = data[0])

@app.route('/actualizacion/<id>', methods = ['POST'])
def actualizar_articulo(id):
	if request.method == 'POST':
		nombre = request.form['nombre']
		precio = request.form['precio']
		cantidad = request.form['cantidad']
		reordenar = request.form['reordenar']
		cur = mysql.connection.cursor()
		cur.execute('''
			UPDATE articulos
			SET nombre = %s,
				precio = %s,
				cantidad = %s,
				reordenar = %s
			WHERE articulo_id = %s 
			''',(nombre, precio, cantidad, reordenar,id))
		mysql.connection.commit()

		return redirect(url_for('Index'))
#########################################################################################################################################################################

@app.route('/eliminar_dato/<string:id>')
def eliminar_dato(id):
	cur = mysql.connection.cursor()
	cur.execute(f'DELETE FROM articulos WHERE articulo_id={id}')
	#cur.execute('INSERT INTO transaccion (fecha,cantidad,tipo) VALUES (%s,%s,"vendido")',(str(hoy),cantidad))#falta el nombre
	mysql.connection.commit()
	flash('Articulo removido satisfactoriamente')
	return redirect(url_for('Index'))

########################################################################################################################################################################
@app.route('/vender_dato')
def vender_dato():
	cur = mysql.connection.cursor()
	cur.execute('select * from articulos where cantidad>0 order by nombre')
	data = cur.fetchall()
	return render_template('vender.html', articulos = data)

@app.route('/vender', methods=['POST'])
def vender():
	if request.method == 'POST':
		nombre = request.form['nombre']
		cantidad = request.form['cantidad']
		hoy=date.today()
		cur = mysql.connection.cursor()
		cur.execute('''
			UPDATE articulos
			SET
				cantidad =(SELECT cantidad FROM articulos where nombre=%s)-%s 
			WHERE nombre = %s 
			''',(nombre,cantidad,nombre))

		cur.execute('select articulo_id from articulos where nombre=%s',[nombre])
		art_id=cur.fetchone()
		cur.execute('insert into transaccion (fecha, cantidad, tipo, articulo_nombre, articulo_id) VALUES (%s,%s,%s,%s,%s)',(hoy, cantidad, 'venta',nombre,art_id[0]))
		mysql.connection.commit()	
		return redirect(url_for('vender_dato'))


#######################################################################################################################################################################

@app.route('/generar_reporte')
def generar_reporte():
	return render_template('reporte.html')



@app.route('/reporte_ventas')
def generar_reporte_ventas():
	cur = mysql.connection.cursor()
	cur.execute('select * from transaccion where tipo="venta"')
	data = cur.fetchall()
	return render_template('reporte_ventas.html', transacciones = data)



@app.route('/reporte_ingresos')
def generar_reporte_ingresos():
	cur = mysql.connection.cursor()
	cur.execute('select * from transaccion where tipo="ingreso"')
	data = cur.fetchall()
	return render_template('reporte_ingresos.html', transacciones = data)


@app.route('/reporte_reordenar')
def generar_reporte_reorden():
	cur = mysql.connection.cursor()
	cur.execute('select * from articulos where cantidad < reordenar order by nombre')
	data = cur.fetchall()
	return render_template('reporte_reorden.html', articulos = data)


@app.route('/reporte_productos')
def generar_reporte_productos():
	cur = mysql.connection.cursor()
	cur.execute('select * from articulos order by nombre')
	data = cur.fetchall()
	return render_template('reporte_productos.html', articulos = data)




###reporte de ventas, de ingresos, de repedidos
###3b6cde801e0f99106149f275612467d908860171


if __name__=='__main__': 
	webbrowser.open_new_tab("http://127.0.0.1:2900/")
	app.run(port = 2900, debug = True) #para poder ejecutar en elpuerto y poder reiniciar el servidor



