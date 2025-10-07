import tkinter as tk
from tkinter import ttk, messagebox


class DashboardView:
    def __init__(self, parent, controller, on_ver_cuentas, on_crear_cuenta,
                 on_transferir, on_ver_movimientos, on_logout):
        self.parent = parent
        self.controller = controller
        self.on_ver_cuentas = on_ver_cuentas
        self.on_crear_cuenta = on_crear_cuenta
        self.on_transferir = on_transferir
        self.on_ver_movimientos = on_ver_movimientos
        self.on_logout = on_logout

        self.frame = ttk.Frame(parent, padding="20")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.create_widgets()
        self.load_cuentas()

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        welcome_label = ttk.Label(
            header_frame,
            text=f"🏦 Bienvenido, {self.controller.usuario_actual.nombre}",
            font=('Arial', 14, 'bold')
        )
        welcome_label.pack(side=tk.LEFT)

        logout_button = ttk.Button(header_frame, text="Cerrar Sesión",
                                   command=self.on_logout)
        logout_button.pack(side=tk.RIGHT)

        # Resumen de cuentas
        ttk.Label(self.frame, text="Mis Cuentas:",
                  font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=10)

        self.cuentas_tree = ttk.Treeview(self.frame, columns=('numero', 'saldo', 'estado'),
                                         show='headings', height=8)
        self.cuentas_tree.heading('numero', text='Número de Cuenta')
        self.cuentas_tree.heading('saldo', text='Saldo')
        self.cuentas_tree.heading('estado', text='Estado')

        self.cuentas_tree.column('numero', width=150)
        self.cuentas_tree.column('saldo', width=100)
        self.cuentas_tree.column('estado', width=80)

        self.cuentas_tree.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL,
                                  command=self.cuentas_tree.yview)
        self.cuentas_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))

        # Botones de acciones
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Actualizar Cuentas",
                   command=self.load_cuentas).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Crear Nueva Cuenta",
                   command=self.on_crear_cuenta).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Realizar Transferencia",
                   command=self.on_transferir).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Ver Movimientos",
                   command=self.on_ver_movimientos).pack(side=tk.LEFT, padx=5)

        # Configurar grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

    def load_cuentas(self):
        # Limpiar tabla
        for item in self.cuentas_tree.get_children():
            self.cuentas_tree.delete(item)

        cuentas, error = self.controller.obtener_cuentas_usuario()

        if error:
            messagebox.showerror("Error", error)
            return

        for cuenta in cuentas:
            self.cuentas_tree.insert('', tk.END, values=(
                cuenta['numero_cuenta'],
                f"${cuenta['saldo']:.2f}",
                cuenta['estado'].upper()
            ))

    def get_selected_cuenta_id(self):
        selection = self.cuentas_tree.selection()
        if not selection:
            return None

        # Obtener el número de cuenta seleccionado
        item = self.cuentas_tree.item(selection[0])
        numero_cuenta = item['values'][0]

        # Buscar el ID de la cuenta
        cuentas, _ = self.controller.obtener_cuentas_usuario()
        for cuenta in cuentas:
            if cuenta['numero_cuenta'] == numero_cuenta:
                return cuenta['id_cuenta']

        return None