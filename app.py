import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash, check_password_hash
from controllers.usuario_controller import (
    crear_usuario, obtener_usuarios, obtener_usuario, actualizar_usuario, eliminar_usuario
)
from controllers.team_controller import index, team_details

# Inicializar la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'autorack.proxy.rlwy.net')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'KEGNQbtxmMSxvECbpRWDcYteAAqlXKrT')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'railway')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 12469))
app.secret_key = os.getenv('SECRET_KEY', 'tu_clave_secreta')

# Inicializar MySQL
mysql = MySQL(app)

# Ruta principal después del login, que muestra 'teams.html'
@app.route('/teams')
def teams():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Redirigir si no está en sesión
    return index()  # Llamar al controlador que maneja la lógica de mostrar los equipos

# Rutas del equipo
@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Si no está logueado, mostrar login.html
    return redirect(url_for('teams'))  # Si está logueado, redirigir a la página de equipos

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s OR correo = %s", (usuario, correo))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            return render_template('registro.html', error="El usuario o correo ya existen.")
        
        contraseña_hasheada = generate_password_hash(contraseña)
        cursor.execute("INSERT INTO usuarios (usuario, correo, contraseña) VALUES (%s, %s, %s)", 
                       (usuario, correo, contraseña_hasheada))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))  # Redirigir al login después de crear la cuenta
    
    return render_template('registro.html')


@app.route('/team/<int:team_id>')
def show_team_details(team_id):
    return team_details(team_id)

# Ruta para el login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        cur.execute("SELECT usuario, correo, contraseña FROM usuarios WHERE usuario = %s", (usuario,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], contraseña):  # `user[2]` es la contraseña hasheada
            session['usuario'] = user[0]  # Nombre de usuario
            session['correo'] = user[1]   # Correo del usuario
            return redirect(url_for('teams'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos.")
    
    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# Rutas CRUD de usuarios
@app.route('/usuarios', methods=['GET'])
def usuarios():
    return obtener_usuarios(mysql)

@app.route('/usuarios', methods=['POST'])
def crear():
    return crear_usuario(mysql)

@app.route('/usuarios/<int:indice>', methods=['GET'])
def obtener_indice(indice):
    return obtener_usuario(indice, mysql)

## Ruta que me dirige a editar el usuario
@app.route('/editar')
def editar():
    return render_template('edit_user.html')


@app.route('/usuarios/<int:indice>', methods=['PUT'])
def actualizar(indice):
    return actualizar_usuario(indice, mysql)

@app.route('/usuarios/<int:indice>', methods=['DELETE'])
def eliminar(indice):
    return eliminar_usuario(indice, mysql)

##Ver si aqui o controller
def login_usuario(mysql):
    usuario_data = request.form
    usuario = usuario_data.get('usuario')
    contraseña = usuario_data.get('contraseña')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT usuario, correo, contraseña FROM usuarios WHERE usuario = %s", (usuario,))
    datos_usuario = cursor.fetchone()
    cursor.close()

    if datos_usuario and check_password_hash(datos_usuario[2], contraseña):
        # Almacena usuario y correo en la sesión
        session['usuario'] = datos_usuario[0]
        session['correo'] = datos_usuario[1]
        return redirect(url_for('teams'))
    else:
        flash("Usuario o contraseña incorrecta")
        return redirect(url_for('login'))

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)