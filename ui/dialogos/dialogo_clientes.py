import tkinter as tk
from tkinter import ttk, messagebox
from db.db import ejecutar_query

class DialogoCliente(tk.Toplevel):
    def __init__(self, parent, actualizar_callback):
        super().__init__(parent)
        self.actualizar_callback = actualizar_callback
        self.title("Registrar Cliente")
        self._inicializar_ui()

    def _inicializar_ui(self):
        self.campos = [
            ('nombres', 'Nombres:'),
            ('apellido_p', 'Apellido Paterno:'),
            ('apellido_m', 'Apellido Materno:'), 
            ('tipo_persona', 'Tipo Persona (Física/Moral):'),
            ('rfc', 'RFC:'),
            ('correo', 'Correo:'),
            ('telefono', 'Teléfono:'),
            ('estado', 'Estado:')
        ]
        
        self.entries = {}
        for idx, (campo, etiqueta) in enumerate(self.campos):
            ttk.Label(self, text=etiqueta).grid(row=idx, column=0, padx=5, pady=5, sticky="e")
            if campo == 'estado':
                entry = ttk.Combobox(self, values=['Activo', 'Inactivo'], state='readonly')
                entry.set('Activo')
            else:
                entry = ttk.Entry(self)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky="ew")
            self.entries[campo] = entry

        ttk.Button(
            self,
            text="Guardar",
            command=self._guardar_cliente
        ).grid(row=len(self.campos), columnspan=2, pady=10)

    def _guardar_cliente(self):
        datos = {
            'nombres': self.entries['nombres'].get().strip(),
            'apellido_p': self.entries['apellido_p'].get().strip(),
            'apellido_m': self.entries['apellido_m'].get().strip(), 
            'tipo_persona': self.entries['tipo_persona'].get().strip(),
            'rfc': self.entries['rfc'].get().strip().upper(),
            'correo': self.entries['correo'].get().strip(),
            'telefono': self.entries['telefono'].get().strip(),
            'estado': 1 if self.entries['estado'].get() == 'Activo' else 0
        }
        
        if not datos['nombres']:
            messagebox.showwarning("Validación", "El campo Nombres es obligatorio")
            return

        try:
            ejecutar_query(
                """INSERT INTO Clientes 
                (nombres, apellido_p, apellido_m, tipo_persona, rfc, correo, telefono, estado, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",  
                (datos['nombres'], datos['apellido_p'], datos['apellido_m'], datos['tipo_persona'], 
                 datos['rfc'], datos['correo'], datos['telefono'], datos['estado'])
            )
            self.actualizar_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cliente: {str(e)}")