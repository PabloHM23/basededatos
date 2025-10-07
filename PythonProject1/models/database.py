import mysql.connector
from mysql.connector import Error
import hashlib


class Database:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'database': 'banco',
            'user': 'root',
            'password': '12345',
            'port': 3306
        }
        self.conexion = None

    def conectar(self):
        """Establecer conexión con la base de datos"""
        try:
            self.conexion = mysql.connector.connect(**self.config)
            return True
        except Error as e:
            print(f"Error conectando a la base de datos: {e}")
            return False

    def desconectar(self):
        """Cerrar conexión con la base de datos"""
        if self.conexion:
            self.conexion.close()
            self.conexion = None

    def ejecutar_procedimiento(self, nombre_procedimiento, parametros=[]):
        """Ejecutar procedimiento almacenado y manejar errores"""
        if not self.conexion:
            if not self.conectar():
                return None, "Error de conexión a la base de datos"

        cursor = None
        try:
            cursor = self.conexion.cursor()
            cursor.callproc(nombre_procedimiento, parametros)
            self.conexion.commit()

            resultados = []
            for result in cursor.stored_results():
                resultados.extend(result.fetchall())

            return resultados, None

        except Error as e:
            self.conexion.rollback()
            return None, str(e)
        finally:
            if cursor:
                cursor.close()

    def ejecutar_consulta(self, consulta, parametros=[]):
        """Ejecutar consulta SQL directa"""
        if not self.conexion:
            if not self.conectar():
                return None, "Error de conexión a la base de datos"

        cursor = None
        try:
            cursor = self.conexion.cursor(dictionary=True)
            cursor.execute(consulta, parametros)
            resultados = cursor.fetchall()
            return resultados, None

        except Error as e:
            return None, str(e)
        finally:
            if cursor:
                cursor.close()

    def verificar_credenciales(self, email, password):
        """Verificar credenciales de usuario"""
        consulta = "SELECT id_usuario, email, nombre, apellidos, contraseña_hash FROM Usuarios WHERE email = %s"
        resultados, error = self.ejecutar_consulta(consulta, [email])

        if error or not resultados:
            return None, error or "Usuario no encontrado"

        usuario_data = resultados[0]
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if usuario_data['contraseña_hash'] == password_hash:
            from entities.usuario import Usuario
            usuario = Usuario(
                usuario_data['id_usuario'],
                usuario_data['email'],
                usuario_data['nombre'],
                usuario_data['apellidos']
            )
            return usuario, None
        else:
            return None, "Credenciales incorrectas", "Credenciales incorrectas"