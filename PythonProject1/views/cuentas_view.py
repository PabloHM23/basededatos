import tkinter as tk
from tkinter import ttk, messagebox


class CuentasView:
    def __init__(self, parent, controller, on_back, on_crear_cuenta, on_ver_movimientos):
        self.parent = parent
        self.controller = controller
        self.on_back = on_back
        self.on_crear_cuenta = on_crear_cuenta
        self.on_ver_movimientos = on_ver_movimientos

        self.frame = ttk.Frame(parent, padding="20")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.create_widgets()
        self.load_cuentas()

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        title_label = ttk.Label(
            header_frame,
            text="💳 Mis Cuentas Bancarias",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side=tk.LEFT)

        back_button = ttk.Button(header_frame, text="Volver",
                                 command=self.on_back)
        back_button.pack(side=tk.RIGHT)

        # Tabla de cuentas
        self.cuentas_tree = ttk.Treeview(self.frame,
                                         columns=('numero', 'saldo', 'estado', 'fecha'),
                                         show='headings',
                                         height=12)

        self.cuentas_tree.heading('numero', text='Número de Cuenta')
        self.cuentas_tree.heading('saldo', text='Saldo')
        self.cuentas_tree.heading('estado', text='Estado')
        self.cuentas_tree.heading('fecha', text='Fecha Creación')

        self.cuentas_tree.column('numero', width=150)
        self.cuentas_tree.column('saldo', width=120)
        self.cuentas_tree.column('estado', width=100)
        self.cuentas_tree.column('fecha', width=120)

        self.cuentas_tree.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL,
                                  command=self.cuentas_tree.yview)
        self.cuentas_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S))

        # Botones de acciones
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="🔄 Actualizar",
                   command=self.load_cuentas).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🆕 Crear Cuenta",
                   command=self.on_crear_cuenta).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Ver Movimientos",
                   command=self.ver_movimientos_seleccionados).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💰 Realizar Transferencia",
                   command=self.realizar_transferencia).pack(side=tk.LEFT, padx=5)

        # Información de saldo total
        self.saldo_total_label = ttk.Label(self.frame, text="Saldo Total: $0.00",
                                           font=('Arial', 12, 'bold'))
        self.saldo_total_label.grid(row=3, column=0, columnspan=3, pady=10)

        # Configurar grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

        # Bind double click para ver movimientos
        self.cuentas_tree.bind('<Double-1>', lambda e: self.ver_movimientos_seleccionados())

    def load_cuentas(self):
        # Limpiar tabla
        for item in self.cuentas_tree.get_children():
            self.cuentas_tree.delete(item)

        cuentas, error = self.controller.obtener_cuentas_usuario()

        if error:
            messagebox.showerror("Error", error)
            return

        saldo_total = 0
        for cuenta in cuentas:
            self.cuentas_tree.insert('', tk.END,
                                     values=(
                                         cuenta['numero_cuenta'],
                                         f"${cuenta['saldo']:.2f}",
                                         cuenta['estado'].upper(),
                                         cuenta['fecha_creacion'].strftime('%d/%m/%Y')
                                     ),
                                     tags=(cuenta['id_cuenta'],))
            saldo_total += cuenta['saldo']

        # Actualizar saldo total
        self.saldo_total_label.config(text=f"Saldo Total: ${saldo_total:.2f}")

        # Configurar colores para estados
        self.cuentas_tree.tag_configure('activa', background='#e8f5e8')
        self.cuentas_tree.tag_configure('bloqueada', background='#ffe8e8')

    def get_selected_cuenta_id(self):
        selection = self.cuentas_tree.selection()
        if not selection:
            return None

        item = self.cuentas_tree.item(selection[0])
        return item['tags'][0] if item['tags'] else None

    def get_selected_cuenta_info(self):
        selection = self.cuentas_tree.selection()
        if not selection:
            return None

        item = self.cuentas_tree.item(selection[0])
        values = item['values']

        return {
            'id_cuenta': item['tags'][0] if item['tags'] else None,
            'numero_cuenta': values[0],
            'saldo': float(values[1].replace('$', '')),
            'estado': values[2],
            'fecha_creacion': values[3]
        }

    def ver_movimientos_seleccionados(self):
        cuenta_info = self.get_selected_cuenta_info()
        if not cuenta_info:
            messagebox.showerror("Error", "Seleccione una cuenta primero")
            return

        self.on_ver_movimientos(cuenta_info)

    def realizar_transferencia(self):
        cuenta_info = self.get_selected_cuenta_info()
        if not cuenta_info:
            messagebox.showerror("Error", "Seleccione una cuenta de origen primero")
            return

        # Aquí podrías abrir la vista de transferencia pre-seleccionando la cuenta
        from views.trasferencia_view import TransferenciaView
        self.show_transferencia_with_selected(cuenta_info)

    def show_transferencia_with_selected(self, cuenta_info):
        # Esta función necesitaría ser implementada en el main para cambiar de vista
        messagebox.showinfo("Info", f"Redirigiendo a transferencia desde: {cuenta_info['numero_cuenta']}")
        # En una implementación completa, aquí cambiarías a la vista de transferencia
        # con la cuenta pre-seleccionada