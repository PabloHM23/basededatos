import tkinter as tk
from tkinter import ttk
from controllers.banco_controller import BancoController
from views.login_view import LoginView
from views.register_view import RegisterView
from views.dashboard_view import DashboardView
from views.cuentas_view import CuentasView
from views.trasferencia_view import TransferenciaView
from views.movimientos_view import MovimientosView
import mysql.connector


class BancoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema Bancario")
        self.root.geometry("900x700")

        self.controller = BancoController()
        self.current_view = None

        self.show_login()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()
        self.current_view = LoginView(
            self.root,
            self.controller,
            on_login_success=self.show_dashboard,
            on_go_to_register=self.show_register
        )

    def show_register(self):
        self.clear_window()
        self.current_view = RegisterView(
            self.root,
            self.controller,
            on_register_success=self.show_login,
            on_go_to_login=self.show_login
        )

    def show_dashboard(self):
        self.clear_window()
        self.current_view = DashboardView(
            self.root,
            self.controller,
            on_ver_cuentas=self.show_cuentas,
            on_crear_cuenta=self.show_crear_cuenta,
            on_transferir=self.show_transferencia,
            on_ver_movimientos=self.show_movimientos_from_dashboard,
            on_logout=self.show_login
        )

    def show_cuentas(self):
        self.clear_window()
        self.current_view = CuentasView(
            self.root,
            self.controller,
            on_back=self.show_dashboard,
            on_crear_cuenta=self.show_crear_cuenta,
            on_ver_movimientos=self.show_movimientos_from_cuentas
        )

    def show_crear_cuenta(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Crear Nueva Cuenta")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Saldo inicial:").grid(row=0, column=0, sticky=tk.W, pady=10)
        saldo_entry = ttk.Entry(frame, width=20)
        saldo_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=10)
        saldo_entry.insert(0, "0.00")

        def submit():
            saldo = saldo_entry.get().strip()
            success, message = self.controller.crear_cuenta(saldo)
            if success:
                tk.messagebox.showinfo("Éxito", message)
                dialog.destroy()
                # Recargar la vista actual si es CuentasView
                if hasattr(self.current_view, 'load_cuentas'):
                    self.current_view.load_cuentas()
            else:
                tk.messagebox.showerror("Error", message)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Crear Cuenta", command=submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        frame.columnconfigure(1, weight=1)

    def show_transferencia(self):
        self.clear_window()
        self.current_view = TransferenciaView(
            self.root,
            self.controller,
            on_back=self.show_dashboard
        )

    def show_movimientos_from_dashboard(self):
        if hasattr(self.current_view, 'get_selected_cuenta_info'):
            cuenta_info = self.current_view.get_selected_cuenta_info()
            if not cuenta_info:
                tk.messagebox.showerror("Error", "Seleccione una cuenta primero")
                return
            self.show_movimientos(cuenta_info)
        else:
            tk.messagebox.showerror("Error", "Seleccione una cuenta primero")

    def show_movimientos_from_cuentas(self, cuenta_info):
        self.show_movimientos(cuenta_info)

    def show_movimientos(self, cuenta_info):
        self.clear_window()
        self.current_view = MovimientosView(
            self.root,
            self.controller,
            cuenta_info=cuenta_info,
            on_back=self.show_cuentas
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = BancoApp()
    app.run()