
import re  # Módulo para expresiones regulares
from werkzeug.security import generate_password_hash, check_password_hash  # Para hashear contraseñas
from flask import request, jsonify, redirect, render_template, flash, session, url_for  # Para manejar solicitudes y respuestas JSON


## Metodo que valida que la contraseña con la que se quiere crear el usuario sea robusta
def es_contraseña_valida(contraseña):
    # Requisitos de contraseña: Al menos 8 caracteres, una mayúscula, un dígito y un carácter especial
    patron = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$'    
    return bool(re.match(patron, contraseña))

def crear_usuario(mysql):
    try:
        nuevo_usuario_data = request.json
        usuario = nuevo_usuario_data.get('usuario')
        correo = nuevo_usuario_data.get('correo')
        contraseña = nuevo_usuario_data.get('contraseña')
        is_admin = int(nuevo_usuario_data.get('is_admin', 0))  # Captura el valor de is_admin o usa 0 como predeterminado

        if not usuario or not correo or not contraseña:
            return jsonify({"error": "Campos obligatorios faltantes"}), 400

        if not es_contraseña_valida(contraseña):
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres, una mayúscula, un dígito y un carácter especial"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s OR correo = %s", (usuario, correo))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            cursor.close()
            return jsonify({"error": "El usuario o correo ya existen"}), 409

        contraseña_hasheada = generate_password_hash(contraseña)
        # Agregar is_admin en la inserción
        cursor.execute("INSERT INTO usuarios (usuario, correo, contraseña, is_admin) VALUES (%s, %s, %s, %s)", 
                       (usuario, correo, contraseña_hasheada, is_admin))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Usuario creado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": f"Error al crear el usuario: {str(e)}"}), 500

# Obtener todos los usuarios
def obtener_usuarios(mysql):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()

    return jsonify([{'id': usuario[0], 'usuario': usuario[1], 'correo': usuario[2], 'contraseña': usuario[3], 'is_admin': usuario[4]} for usuario in usuarios]), 200

# Obtener un usuario por ID
def obtener_usuario(indice, mysql):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (indice,))
    usuario = cursor.fetchone()
    cursor.close()

    if usuario:
        return jsonify({'id': usuario[0], 'usuario': usuario[1], 'correo': usuario[2], 'contraseña': usuario[3]}), 200
    return jsonify({"error": "Usuario no encontrado"}), 404



# Actualizar un usuario
def actualizar_usuario(indice, mysql):
    try:
        usuario_actualizado_data = request.get_json()
        if not usuario_actualizado_data:
            return jsonify({"error": "La solicitud debe contener un JSON válido."}), 400
        
        usuario = usuario_actualizado_data.get('usuario')
        correo = usuario_actualizado_data.get('correo')
        nueva_contraseña = usuario_actualizado_data.get('contraseña')

        if not usuario or not correo:
            return jsonify({"error": "Los campos usuario y correo son obligatorios."}), 400

        if nueva_contraseña and not es_contraseña_valida(nueva_contraseña):
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres, incluir una letra mayúscula y un carácter especial."}), 400

        cursor = mysql.connection.cursor()

        if nueva_contraseña:
            contraseña_hasheada = generate_password_hash(nueva_contraseña)
            cursor.execute(
                "UPDATE usuarios SET usuario = %s, correo = %s, contraseña = %s WHERE id = %s",
                (usuario, correo, contraseña_hasheada, indice)
            )
        else:
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

 # Actualizar user on session
def actualizar_usuario_on_session(indice, mysql):
    try:
        usuario_actualizado_data = request.get_json()
        usuario = usuario_actualizado_data.get('usuario')
        correo = usuario_actualizado_data.get('correo')
        nueva_contraseña = usuario_actualizado_data.get('contraseña')

        # Verificar si los campos obligatorios están presentes
        if not usuario or not correo or not nueva_contraseña:
            return jsonify({"error": "Faltan campos obligatorios (usuario, correo, contraseña)"}), 400

        # Validar que la nueva contraseña cumpla con los requisitos de seguridad
        if not es_contraseña_valida(nueva_contraseña):
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres, incluir una letra mayúscula y un carácter especial"}), 400

        cursor = mysql.connection.cursor()

        # Hashear la nueva contraseña antes de actualizar
        contraseña_hasheada = generate_password_hash(nueva_contraseña)

        # Actualizar los datos del usuario en la base de datos
        cursor.execute("UPDATE usuarios SET usuario = %s, correo = %s, contraseña = %s WHERE id = %s", 
                       (usuario, correo, contraseña_hasheada, indice))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"message": "Usuario actualizado correctamente"}), 200

    except Exception as e:
        print(f"Error al actualizar el usuario: {str(e)}")
        return jsonify({"error": f"Error al actualizar el usuario: {str(e)}"}), 500
  
# Eliminar un usuario
def eliminar_usuario(indice, mysql):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (indice,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        return jsonify({"error": "Usuario no encontrado"}), 404

    cursor.execute("DELETE FROM usuarios WHERE id = %s", (indice,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Usuario eliminado correctamente"}), 200

# Verificar la contraseña de un usuario existente
def verificar_contraseña(indice, mysql):
    data = request.get_json()
    contraseña_ingresada = data.get('contraseña')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (indice,))
    usuario = cursor.fetchone()
    cursor.close()

    if usuario and check_password_hash(usuario[3], contraseña_ingresada):
        return jsonify({'id': usuario[0], 'usuario': usuario[1], 'correo': usuario[2], 'contraseña': usuario[3]}), 200
    return jsonify({"error": "Contraseña incorrecta"}), 401


def login_usuario(mysql):
    # Aquí asumo que estás manejando un formulario de login y ya tienes lógica de autenticación
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


##Ver si aqui o app
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
    
    