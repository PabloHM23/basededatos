import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta


class MovimientosView:
    def __init__(self, parent, controller, cuenta_info, on_back):
        self.parent = parent
        self.controller = controller
        self.cuenta_info = cuenta_info
        self.on_back = on_back

        self.frame = ttk.Frame(parent, padding="20")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.create_widgets()
        self.load_movimientos()

    def create_widgets(self):
        # Header con información de la cuenta
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 20))

        title_label = ttk.Label(
            header_frame,
            text=f"📊 Movimientos - {self.cuenta_info['numero_cuenta']}",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side=tk.LEFT)

        back_button = ttk.Button(header_frame, text="Volver a Cuentas",
                                 command=self.on_back)
        back_button.pack(side=tk.RIGHT)

        # Información de la cuenta
        info_frame = ttk.Frame(self.frame)
        info_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(info_frame, text=f"Saldo Actual: ${self.cuenta_info['saldo']:.2f}",
                  font=('Arial', 12, 'bold'), foreground='green').pack(side=tk.LEFT)

        ttk.Label(info_frame, text=f"Estado: {self.cuenta_info['estado']}",
                  font=('Arial', 10)).pack(side=tk.LEFT, padx=20)

        ttk.Label(info_frame, text=f"Creación: {self.cuenta_info['fecha_creacion']}",
                  font=('Arial', 10)).pack(side=tk.LEFT)

        # Filtros
        filter_frame = ttk.Frame(self.frame)
        filter_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(filter_frame, text="Filtrar por:").pack(side=tk.LEFT)

        # Filtro de tipo de movimiento
        ttk.Label(filter_frame, text="Tipo:").pack(side=tk.LEFT, padx=(20, 5))
        self.tipo_filter_var = tk.StringVar(value="Todos")
        tipo_combo = ttk.Combobox(filter_frame, textvariable=self.tipo_filter_var,
                                  values=["Todos", "Apertura", "Transferencia Entrada", "Transferencia Salida"],
                                  state="readonly", width=20)
        tipo_combo.pack(side=tk.LEFT, padx=5)
        tipo_combo.bind('<<ComboboxSelected>>', self.aplicar_filtros)

        # Botón limpiar filtros
        ttk.Button(filter_frame, text="Limpiar Filtros",
                   command=self.limpiar_filtros).pack(side=tk.RIGHT)

        # Tabla de movimientos
        self.movimientos_tree = ttk.Treeview(self.frame,
                                             columns=('fecha', 'tipo', 'monto', 'origen', 'destino', 'nota'),
                                             show='headings',
                                             height=15)

        self.movimientos_tree.heading('fecha', text='Fecha y Hora')
        self.movimientos_tree.heading('tipo', text='Tipo de Movimiento')
        self.movimientos_tree.heading('monto', text='Monto')
        self.movimientos_tree.heading('origen', text='Cuenta Origen')
        self.movimientos_tree.heading('destino', text='Cuenta Destino')
        self.movimientos_tree.heading('nota', text='Nota')

        self.movimientos_tree.column('fecha', width=150)
        self.movimientos_tree.column('tipo', width=150)
        self.movimientos_tree.column('monto', width=100)
        self.movimientos_tree.column('origen', width=120)
        self.movimientos_tree.column('destino', width=120)
        self.movimientos_tree.column('nota', width=200)

        self.movimientos_tree.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL,
                                    command=self.movimientos_tree.yview)
        h_scrollbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL,
                                    command=self.movimientos_tree.xview)
        self.movimientos_tree.configure(yscrollcommand=v_scrollbar.set,
                                        xscrollcommand=h_scrollbar.set)

        v_scrollbar.grid(row=3, column=4, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E))

        # Resumen estadístico
        self.resumen_frame = ttk.Frame(self.frame)
        self.resumen_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)

        self.ingresos_label = ttk.Label(self.resumen_frame, text="Total Ingresos: $0.00",
                                        foreground='green', font=('Arial', 10, 'bold'))
        self.ingresos_label.pack(side=tk.LEFT, padx=20)

        self.egresos_label = ttk.Label(self.resumen_frame, text="Total Egresos: $0.00",
                                       foreground='red', font=('Arial', 10, 'bold'))
        self.egresos_label.pack(side=tk.LEFT, padx=20)

        self.saldo_final_label = ttk.Label(self.resumen_frame, text="Saldo Final: $0.00",
                                           font=('Arial', 10, 'bold'))
        self.saldo_final_label.pack(side=tk.LEFT, padx=20)

        # Configurar grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(3, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

        # Almacenar todos los movimientos para filtrado
        self.todos_movimientos = []

    def load_movimientos(self):
        # Limpiar tabla
        for item in self.movimientos_tree.get_children():
            self.movimientos_tree.delete(item)

        movimientos, _, error = self.controller.obtener_movimientos_cuenta(self.cuenta_info['id_cuenta'])

        if error:
            messagebox.showerror("Error", error)
            return

        self.todos_movimientos = movimientos
        self.mostrar_movimientos(movimientos)
        self.calcular_resumen(movimientos)

    def mostrar_movimientos(self, movimientos):
        total_ingresos = 0
        total_egresos = 0

        for mov in movimientos:
            fecha = mov['fecha_operacion'].strftime('%d/%m/%Y %H:%M')
            tipo = mov['tipo_movimiento'].replace('_', ' ').title()

            # Determinar color y signo del monto
            if mov['tipo_movimiento'] in ['TRANSFERENCIA_ENTRADA', 'APERTURA']:
                monto_str = f"+${mov['monto']:.2f}"
                total_ingresos += mov['monto']
                tag = 'ingreso'
            else:
                monto_str = f"-${mov['monto']:.2f}"
                total_egresos += mov['monto']
                tag = 'egreso'

            # Determinar cuentas involucradas
            cuenta_origen = mov['cuenta_emisora'] or ''
            cuenta_destino = mov['cuenta_receptora'] or ''

            # Para transferencias, ajustar qué cuenta mostrar
            if mov['tipo_movimiento'] == 'TRANSFERENCIA_SALIDA':
                cuenta_origen = self.cuenta_info['numero_cuenta']
                cuenta_destino = mov['cuenta_receptora'] or ''
            elif mov['tipo_movimiento'] == 'TRANSFERENCIA_ENTRADA':
                cuenta_origen = mov['cuenta_emisora'] or ''
                cuenta_destino = self.cuenta_info['numero_cuenta']

            nota = mov['nota'] or ''

            self.movimientos_tree.insert('', tk.END,
                                         values=(fecha, tipo, monto_str, cuenta_origen, cuenta_destino, nota),
                                         tags=(tag,))

        # Configurar colores
        self.movimientos_tree.tag_configure('ingreso', foreground='green')
        self.movimientos_tree.tag_configure('egreso', foreground='red')

    def calcular_resumen(self, movimientos):
        total_ingresos = 0
        total_egresos = 0

        for mov in movimientos:
            if mov['tipo_movimiento'] in ['TRANSFERENCIA_ENTRADA', 'APERTURA']:
                total_ingresos += mov['monto']
            else:
                total_egresos += mov['monto']

        saldo_final = total_ingresos - total_egresos

        self.ingresos_label.config(text=f"Total Ingresos: ${total_ingresos:.2f}")
        self.egresos_label.config(text=f"Total Egresos: ${total_egresos:.2f}")
        self.saldo_final_label.config(text=f"Saldo Final: ${saldo_final:.2f}")

    def aplicar_filtros(self, event=None):
        tipo_filtro = self.tipo_filter_var.get()

        movimientos_filtrados = []

        for mov in self.todos_movimientos:
            tipo_mov = mov['tipo_movimiento'].replace('_', ' ').title()

            # Aplicar filtro de tipo
            if tipo_filtro == "Todos":
                movimientos_filtrados.append(mov)
            elif tipo_filtro == "Apertura" and mov['tipo_movimiento'] == 'APERTURA':
                movimientos_filtrados.append(mov)
            elif tipo_filtro == "Transferencia Entrada" and mov['tipo_movimiento'] == 'TRANSFERENCIA_ENTRADA':
                movimientos_filtrados.append(mov)
            elif tipo_filtro == "Transferencia Salida" and mov['tipo_movimiento'] == 'TRANSFERENCIA_SALIDA':
                movimientos_filtrados.append(mov)

        # Limpiar y mostrar movimientos filtrados
        for item in self.movimientos_tree.get_children():
            self.movimientos_tree.delete(item)

        self.mostrar_movimientos(movimientos_filtrados)
        self.calcular_resumen(movimientos_filtrados)

    def limpiar_filtros(self):
        self.tipo_filter_var.set("Todos")
        self.aplicar_filtros()