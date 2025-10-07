class Usuario:
    def __init__(self, id_usuario, email, nombre, apellidos):
        self.id_usuario = id_usuario
        self.email = email
        self.nombre = nombre
        self.apellidos = apellidos

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"