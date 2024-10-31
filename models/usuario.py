class Usuario:
    def __init__(self, usuario, correo, contraseña, is_admin=0):
        self.usuario = usuario
        self.correo = correo
        self.contraseña = contraseña
        self.is_admin = is_admin  # Campo is_admin, con valor predeterminado de 0
