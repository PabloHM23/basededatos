import tkinter as tk
from tkinter import ttk, messagebox


class RegisterView:
    def __init__(self, parent, controller, on_register_success, on_go_to_login):
        self.parent = parent
        self.controller = controller
        self.on_register_success = on_register_success
        self.on_go_to_login = on_go_to_login

        self.frame = ttk.Frame(parent, padding="20")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.create_widgets()

    def create_widgets(self):
        # Título
        title_label = ttk.Label(self.frame, text="📝 Registro de Usuario",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Campos del formulario
        fields = [
            ("Email:", "email_entry"),
            ("Nombre:", "nombre_entry"),
            ("Apellidos:", "apellidos_entry"),
            ("Contraseña:", "password_entry"),
            ("Confirmar Contraseña:", "confirm_password_entry")
        ]

        for i, (label, attr_name) in enumerate(fields, 1):
            ttk.Label(self.frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(self.frame, width=30, show="*" if "password" in attr_name else "")
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
            setattr(self, attr_name, entry)

        # Botones
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)

        self.register_button = ttk.Button(button_frame, text="Registrarse",
                                          command=self.register)
        self.register_button.pack(side=tk.LEFT, padx=5)

        self.login_button = ttk.Button(button_frame, text="Volver al Login",
                                       command=self.on_go_to_login)
        self.login_button.pack(side=tk.LEFT, padx=5)

        # Configurar grid weights
        self.frame.columnconfigure(1, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

    def register(self):
        email = self.email_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        apellidos = self.apellidos_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        success, message = self.controller.registrar_usuario(
            email, nombre, apellidos, password, confirm_password
        )

        if success:
            messagebox.showinfo("Éxito", message)
            self.on_register_success()
        else:
            messagebox.showerror("Error", message)

    def clear_fields(self):
        self.email_entry.delete(0, tk.END)
        self.nombre_entry.delete(0, tk.END)
        self.apellidos_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)