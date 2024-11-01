import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash, check_password_hash
from controllers.usuario_controller import (
    crear_usuario, obtener_usuarios, obtener_usuario, actualizar_usuario, eliminar_usuario, es_contraseña_valida, actualizar_usuario_on_session
)
from models.models import get_teams, get_team_details
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
        # Cambia para detectar el valor y asignarlo como 1 o 0
        is_admin = int(request.form.get('is_admin', '0') == '1')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s OR correo = %s", (usuario, correo))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            return render_template('registro.html', error="El usuario o correo ya existen.")
        
        contraseña_hasheada = generate_password_hash(contraseña)
        cursor.execute("INSERT INTO usuarios (usuario, correo, contraseña, is_admin) VALUES (%s, %s, %s, %s)", 
                       (usuario, correo, contraseña_hasheada, is_admin))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))
    
    return render_template('registro.html')


@app.route('/registro', methods=['GET', 'POST'])
def registrocambiar():
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

@app.route('/teams')
def show_teams():
    teams = get_teams()  # Llama a get_teams para obtener la lista de equipos
    return render_template('teams.html', teams=teams)  # Pasa 'teams' a la plantilla

@app.route('/team/<int:team_id>')
def show_team_details(team_id):
    return team_details(team_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, usuario, correo, contraseña, is_admin FROM usuarios WHERE usuario = %s", (usuario,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], contraseña):  # user[3] es la contraseña hasheada
            # Guardar id, usuario, correo, y estado de admin en sesión
            session['usuario_id'] = user[0]  # ID del usuario
            session['usuario'] = user[1]     # Nombre de usuario
            session['correo'] = user[2]      # Correo del usuario
            session['is_admin'] = int(user[4])  # Asegurarse de que sea un entero (1 o 0)

            # Redirigir basado en rol de usuario
            if session['is_admin'] == 1:  # Si es administrador
                return redirect(url_for('admin_dashboard'))
            else:  # Usuario normal
                return redirect(url_for('teams'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos.")

    return render_template('login.html')

# Ruta para el login
@app.route('/login', methods=['GET', 'POST'])
def login1():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, usuario, correo, contraseña, is_admin FROM usuarios WHERE usuario = %s", (usuario,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], contraseña):  # user[3] es la contraseña hasheada
            # Guardar id, usuario y correo en sesión
            session['usuario_id'] = user[0]  # ID del usuario
            session['usuario'] = user[1]     # Nombre de usuario
            session['correo'] = user[2]      # Correo del usuario
            session['is_admin'] = user[4]    # `is_admin` (TRUE o FALSE)

            # Redirigir basado en rol de usuario
            if session['is_admin']:  # Si es administrador
                return redirect(url_for('admin_dashboard'))
            else:  # Usuario normal
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

@app.route('/actualizar_usuario', methods=['POST'])
def actualizar_usuario(indice, mysql):
    try:
        # Intentar obtener los datos en formato JSON
        usuario_actualizado_data = request.get_json()
        if not usuario_actualizado_data:
            return jsonify({"error": "La solicitud debe contener un JSON válido."}), 400

        # Obtener los datos del JSON
        usuario = usuario_actualizado_data.get('usuario')
        correo = usuario_actualizado_data.get('correo')
        nueva_contraseña = usuario_actualizado_data.get('contraseña')

        # Verificar si los campos obligatorios están presentes
        if not usuario or not correo:
            return jsonify({"error": "Los campos usuario y correo son obligatorios."}), 400

        # Validar la nueva contraseña solo si se envía una
        if nueva_contraseña and not es_contraseña_valida(nueva_contraseña):
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres, incluir una letra mayúscula y un carácter especial."}), 400

        cursor = mysql.connection.cursor()

        # Si hay una nueva contraseña, se hashea y actualiza
        if nueva_contraseña:
            contraseña_hasheada = generate_password_hash(nueva_contraseña)
            cursor.execute(
                "UPDATE usuarios SET usuario = %s, correo = %s, contraseña = %s WHERE id = %s",
                (usuario, correo, contraseña_hasheada, indice)
            )
        else:
            # Si no se envía nueva contraseña, actualiza solo usuario y correo
            cursor.execute(
                "UPDATE usuarios SET usuario = %s, correo = %s WHERE id = %s",
                (usuario, correo, indice)
            )

        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"message": "Usuario actualizado correctamente"}), 200

    except Exception as e:
        print(f"Error al actualizar el usuario: {str(e)}")
        return jsonify({"error": f"Error al actualizar el usuario: {str(e)}"}), 500


@app.route('/usuarios/<int:indice>', methods=['PUT'])
def actualizar(indice):
    return actualizar_usuario(indice, mysql)

#ruta para actualizar on session
@app.route('/actualizar_usuario_on_session', methods=['POST'])
def actualizar_usuario_session():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    nuevo_usuario = request.form['usuario']
    nuevo_correo = request.form['correo']
    nueva_contraseña = request.form['contraseña']
    usuario_id = session['usuario_id']

    cursor = mysql.connection.cursor()

    # Actualizar nombre de usuario y correo
    if nuevo_usuario:
        cursor.execute("UPDATE usuarios SET usuario = %s WHERE id = %s", (nuevo_usuario, usuario_id))
        session['usuario'] = nuevo_usuario  # Actualizar en sesión

    if nuevo_correo:
        cursor.execute("UPDATE usuarios SET correo = %s WHERE id = %s", (nuevo_correo, usuario_id))
        session['correo'] = nuevo_correo  # Actualizar en sesión

    # Actualizar contraseña solo si se ha proporcionado una nueva
    if nueva_contraseña:
        contraseña_hasheada = generate_password_hash(nueva_contraseña)
        cursor.execute("UPDATE usuarios SET contraseña = %s WHERE id = %s", (contraseña_hasheada, usuario_id))

    mysql.connection.commit()
    cursor.close()

    flash("Usuario actualizado exitosamente.")
    return redirect(url_for('teams'))

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
    
@app.route('/editar')
def editar_usuario():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('edit_user.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'usuario' not in session or session.get('is_admin') != 1:
        flash("Acceso denegado. No tiene permisos de administrador.")
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, usuario, correo FROM usuarios WHERE is_admin = 1")
    administradores = cursor.fetchall()
    cursor.close()
    
    return render_template('admin_dashboard.html', administradores=administradores)

##Ruta para la Página de Administrador
@app.route('/admin_dashboard')
def admin_dashboard1():
    if 'usuario' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))  # Redirigir si no es admin
    return render_template('admin_dashboard.html')  # Muestra el panel de admin

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)

