import tkinter as tk
from tkinter import ttk, messagebox


class TransferenciaView:
    def __init__(self, parent, controller, on_back):
        self.parent = parent
        self.controller = controller
        self.on_back = on_back

        self.frame = ttk.Frame(parent, padding="20")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.cuentas = []
        self.load_cuentas()
        self.create_widgets()

    def load_cuentas(self):
        self.cuentas, _ = self.controller.obtener_cuentas_usuario()

    def create_widgets(self):
        # Título
        title_label = ttk.Label(self.frame, text="💸 Realizar Transferencia",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Cuenta emisora
        ttk.Label(self.frame, text="Cuenta de Origen:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cuenta_emisora_var = tk.StringVar()
        self.cuenta_emisora_combo = ttk.Combobox(self.frame, textvariable=self.cuenta_emisora_var,
                                                 state="readonly", width=30)
        self.cuenta_emisora_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Cargar cuentas en el combobox
        cuentas_display = [f"{c['numero_cuenta']} - Saldo: ${c['saldo']:.2f}" for c in self.cuentas]
        self.cuenta_emisora_combo['values'] = cuentas_display

        # Cuenta receptora
        ttk.Label(self.frame, text="Cuenta Destino:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.cuenta_receptora_entry = ttk.Entry(self.frame, width=30)
        self.cuenta_receptora_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(self.frame, text="Ej: CTA000123456",
                  font=('Arial', 8)).grid(row=2, column=2, sticky=tk.W, padx=5)

        # Monto
        ttk.Label(self.frame, text="Monto:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.monto_entry = ttk.Entry(self.frame, width=30)
        self.monto_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        # Nota
        ttk.Label(self.frame, text="Nota (opcional):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.nota_entry = ttk.Entry(self.frame, width=30)
        self.nota_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

        # Botones
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Realizar Transferencia",
                   command=self.realizar_transferencia).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar",
                   command=self.on_back).pack(side=tk.LEFT, padx=5)

        # Configurar grid weights
        self.frame.columnconfigure(1, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

    def realizar_transferencia(self):
        if not self.cuenta_emisora_var.get():
            messagebox.showerror("Error", "Seleccione una cuenta de origen")
            return

        cuenta_receptora = self.cuenta_receptora_entry.get().strip()
        monto = self.monto_entry.get().strip()
        nota = self.nota_entry.get().strip()

        if not cuenta_receptora or not monto:
            messagebox.showerror("Error", "Complete todos los campos obligatorios")
            return

        # Obtener ID de la cuenta emisora
        selected_index = self.cuenta_emisora_combo.current()
        if selected_index == -1:
            messagebox.showerror("Error", "Seleccione una cuenta válida")
            return

        cuenta_emisora_id = self.cuentas[selected_index]['id_cuenta']

        success, message = self.controller.realizar_transferencia(
            cuenta_emisora_id, cuenta_receptora, monto, nota
        )

        if success:
            messagebox.showinfo("Éxito", message)
            self.clear_fields()
            self.on_back()
        else:
            messagebox.showerror("Error", message)

    def clear_fields(self):
        self.cuenta_emisora_var.set('')
        self.cuenta_receptora_entry.delete(0, tk.END)
        self.monto_entry.delete(0, tk.END)
        self.nota_entry.delete(0, tk.END)