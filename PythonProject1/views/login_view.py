import tkinter as tk
from tkinter import ttk, messagebox


class LoginView:
    def __init__(self, parent, controller, on_login_success, on_go_to_register):
        self.parent = parent
        self.controller = controller
        self.on_login_success = on_login_success
        self.on_go_to_register = on_go_to_register

        self.frame = ttk.Frame(parent, padding="20")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.create_widgets()

    def create_widgets(self):
        # Título
        title_label = ttk.Label(self.frame, text="🏦 Iniciar Sesión",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Email
        ttk.Label(self.frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(self.frame, width=30)
        self.email_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Contraseña
        ttk.Label(self.frame, text="Contraseña:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # Botones
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        self.login_button = ttk.Button(button_frame, text="Iniciar Sesión",
                                       command=self.login)
        self.login_button.pack(side=tk.LEFT, padx=5)

        self.register_button = ttk.Button(button_frame, text="Registrarse",
                                          command=self.on_go_to_register)
        self.register_button.pack(side=tk.LEFT, padx=5)

        # Configurar grid weights
        self.frame.columnconfigure(1, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

        # Bind Enter key para login
        self.parent.bind('<Return>', lambda e: self.login())

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return

        success, message = self.controller.iniciar_sesion(email, password)

        if success:
            messagebox.showinfo("Éxito", message)
            self.on_login_success()
        else:
            messagebox.showerror("Error", message)

    def clear_fields(self):
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)