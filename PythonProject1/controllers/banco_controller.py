from operator import truediv

from models.database import Database
from entities.usuario import Usuario


class BancoController:
    def __init__(self):
        self.db = Database()
        self.usuario_actual = None

    def registrar_usuario(self, email, nombre, apellidos, password, confirm_password):
        """Registrar nuevo usuario"""
        if not all([email, nombre, apellidos, password]):
            return False, "Todos los campos son obligatorios"

        if password != confirm_password:
            return False, "Las contraseñas no coinciden"

        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"

        resultados, error = self.db.ejecutar_procedimiento(
            'sp_RegistrarUsuario',
            [email, nombre, apellidos, password]
        )

        if error:
            if "El email ya está registrado" in error:
                return False, "El email ya está registrado"
            else:
                return False, f"Error: {error}"

        return True, "¡Registro exitoso! Ahora puedes iniciar sesión"

    def iniciar_sesion(self, email, password):
        """Iniciar sesión de usuario"""
        if not email or not password:
            return False, "Email y contraseña son obligatorios"

        usuario, error = self.db.verificar_credenciales(email, password)

        if error:
            return False, error

        self.usuario_actual = usuario
        return True, f"¡Bienvenido, {usuario.nombre}!"

    def obtener_cuentas_usuario(self):
        """Obtener todas las cuentas del usuario actual"""
        consulta = """
        SELECT id_cuenta, numero_cuenta, saldo, estado, fecha_creacion 
        FROM Cuentas 
        WHERE id_usuario = %s 
        ORDER BY fecha_creacion DESC
        """
        cuentas, error = self.db.ejecutar_consulta(consulta, [self.usuario_actual.id_usuario])

        if error:
            return [], f"Error al cargar cuentas: {error}"

        return cuentas, None

    def crear_cuenta(self, saldo_inicial):
        """Crear nueva cuenta bancaria"""
        try:
            saldo = float(saldo_inicial)
            if saldo < 0:
                return False, "El saldo inicial no puede ser negativo"
        except ValueError:
            return False, "El saldo debe ser un número válido"

        resultados, error = self.db.ejecutar_procedimiento(
            'sp_AbrirCuenta',
            [self.usuario_actual.id_usuario, saldo]
        )

        if error:
            if "El usuario no existe" in error:
                return False, "Error: Usuario no encontrado"
            elif "El saldo inicial no puede ser negativo" in error:
                return False, "El saldo inicial no puede ser negativo"
            else:
                return False, f"Error: {error}"

        return True, "¡Cuenta creada exitosamente!"

    def realizar_transferencia(self, cuenta_emisora_id, cuenta_receptora_numero, monto, nota):
        """Realizar transferencia entre cuentas"""
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                return False, "El monto debe ser mayor a cero"
        except ValueError:
            return False, "El monto debe ser un número válido"

        resultados, error = self.db.ejecutar_procedimiento(
            'sp_TransferirDinero',
            [cuenta_emisora_id, cuenta_receptora_numero, monto_float, nota]
        )

        if error:
            if "Saldo insuficiente" in error:
                return False, "Saldo insuficiente para realizar la transferencia"
            elif "Cuenta emisora no encontrada" in error:
                return False, "Cuenta emisora no encontrada"
            elif "Cuenta receptora no encontrada" in error:
                return False, "Cuenta receptora no encontrada"
            elif "no está activa" in error:
                return False, "Una de las cuentas no está activa"
            elif "misma cuenta" in error:
                return False, "No se puede transferir a la misma cuenta"
            elif "El monto debe ser mayor a cero" in error:
                return False, "El monto debe ser mayor a cero"
            else:
                return False, f"Error: {error}"

        return True, "¡Transferencia realizada exitosamente!"

    def obtener_movimientos_cuenta(self, cuenta_id):
        """Obtener movimientos de una cuenta específica"""
        # Verificar que la cuenta pertenece al usuario
        consulta_verificacion = "SELECT id_cuenta FROM Cuentas WHERE id_cuenta = %s AND id_usuario = %s"
        verificacion, error = self.db.ejecutar_consulta(consulta_verificacion,
                                                        [cuenta_id, self.usuario_actual.id_usuario])

        if error or not verificacion:
            return [], None, "Cuenta no válida"

        # Obtener movimientos
        consulta_movimientos = """
        SELECT m.fecha_operacion, tm.nombre as tipo_movimiento, m.monto,
               c_emisora.numero_cuenta as cuenta_emisora,
               c_receptora.numero_cuenta as cuenta_receptora,
               m.nota
        FROM Movimientos m
        JOIN TiposMovimiento tm ON m.id_tipo_movimiento = tm.id_tipo_movimiento
        LEFT JOIN Cuentas c_emisora ON m.id_cuenta_emisora = c_emisora.id_cuenta
        LEFT JOIN Cuentas c_receptora ON m.id_cuenta_receptora = c_receptora.id_cuenta
        WHERE m.id_cuenta_emisora = %s OR m.id_cuenta_receptora = %s
        ORDER BY m.fecha_operacion DESC
        LIMIT 50
        """

        movimientos, error = self.db.ejecutar_consulta(consulta_movimientos, [cuenta_id, cuenta_id])

        if error:
            return [], None, f"Error al cargar movimientos: {error}"

        # Obtener información de la cuenta
        consulta_cuenta = "SELECT numero_cuenta, saldo FROM Cuentas WHERE id_cuenta = %s"
        cuenta_info, _ = self.db.ejecutar_consulta(consulta_cuenta, [cuenta_id])

        return movimientos, cuenta_info[0] if cuenta_info else None, None

    def cerrar_sesion(self):
        """Cerrar sesión del usuario"""
        self.usuario_actual = None
        self.db.desconectar()