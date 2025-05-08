import tkinter as tk
from tkinter import ttk, messagebox
from threading import Timer
from db.db import obtener_datos, ejecutar_query
from ui.styles import AppTheme

class PantallaClientes(ttk.Frame):
    COLUMNAS = {
        'Principal': [
            ('id', 'ID', 60),
            ('nombre', 'Nombre', 200),
            ('tipo', 'Tipo', 150),
            ('direccion', 'Dirección', 200),
            ('estado', 'Estado', 100),
        ]
    }
    
    ESTADOS = {
        'ACTIVO': 'Activo',
        'INACTIVO': 'Inactivo'
    }
    
    CAMPOS_BUSQUEDA = ['id', 'nombre', 'tipo']

    def __init__(self, parent):
        super().__init__(parent)
        self.theme = AppTheme()
        self.datos = []
        self.filtros = {
            'busqueda': '',
            'estado': 'Todos',
            'direccion': 'Todos'
        }
        self.orden = {'columna': None, 'ascendente': True}
        
        self._inicializar_ui()
        self._cargar_datos()

    def _inicializar_ui(self):
        self._crear_controles()
        self._configurar_tabla()
        self._actualizar_boton_estado()

    def _crear_controles(self):
        controles_frame = ttk.Frame(self)
        controles_frame.pack(fill=tk.X, padx=10, pady=10)

        # Búsqueda
        ttk.Label(controles_frame, text="Buscar:").pack(side=tk.LEFT)
        self.entrada_busqueda = ttk.Entry(controles_frame)
        self.entrada_busqueda.pack(side=tk.LEFT, padx=5)
        self.entrada_busqueda.bind("<KeyRelease>", lambda e: self._aplicar_debounce_filtros())

        # Filtro Estado
        ttk.Label(controles_frame, text="Estado:").pack(side=tk.LEFT, padx=(15, 0))
        self.combo_estado = ttk.Combobox(
            controles_frame,
            values=["Todos", self.ESTADOS['ACTIVO'], self.ESTADOS['INACTIVO']],
            state="readonly"
        )
        self.combo_estado.set("Todos")
        self.combo_estado.pack(side=tk.LEFT, padx=5)
        self.combo_estado.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())

        # Filtro Dirección
        ttk.Label(controles_frame, text="Dirección:").pack(side=tk.LEFT, padx=(15, 0))
        self.combo_direccion = ttk.Combobox(controles_frame, state="readonly")
        self.combo_direccion.pack(side=tk.LEFT, padx=5)
        self.combo_direccion.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())

        # Botones
        self.btn_estado = ttk.Button(
            controles_frame,
            text="↺ Activar/Inactivar",
            style="Secondary.TButton",
            command=self._cambiar_estado_cliente,
            state="disabled"
        )
        self.btn_estado.pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            controles_frame,
            text="➕ Nuevo Registro",
            style="Primary.TButton",
            command=self._abrir_dialogo_nuevo
        ).pack(side=tk.RIGHT, padx=5)

    def _configurar_tabla(self):
        self.tabla_frame = ttk.Frame(self)
        self.tabla_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(self.tabla_frame, orient=tk.VERTICAL)
        
        self.tabla = ttk.Treeview(
            self.tabla_frame,
            columns=[col[0] for col in self.COLUMNAS['Principal']],
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        
        for col in self.COLUMNAS['Principal']:
            self.tabla.heading(col[0], text=col[1], 
                            command=lambda c=col[0]: self._ordenar_por_columna(c))
            self.tabla.column(col[0], width=col[2], anchor=tk.CENTER)
        
        scrollbar.config(command=self.tabla.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla.pack(fill=tk.BOTH, expand=True)
        self.tabla.bind("<<TreeviewSelect>>", lambda e: self._actualizar_boton_estado())
        
    def _cargar_datos(self):
        try:
            query = """
                SELECT 
                    id,
                    nombre,
                    tipo,
                    direccion,
                    estado
                FROM clientes
                {where}
                ORDER BY {order_by}
            """.format(
                where=self._construir_where(),
                order_by=self._construir_orden()
            )
            
            parametros = []
            if self.filtros['busqueda']:
                parametros.extend([f"%{self.filtros['busqueda']}%"] * len(self.CAMPOS_BUSQUEDA))
            if self.filtros['estado'] != 'Todos':
                parametros.append(self.filtros['estado'])
            if self.filtros['direccion'] != 'Todos':
                parametros.append(self.filtros['direccion'])
            
            self.datos = obtener_datos(query, parametros, return_dict=True)
            self._actualizar_filtro_direcciones()
            self._actualizar_tabla()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando datos: {str(e)}")

    def _construir_where(self):
        condiciones = []
        if self.filtros['busqueda']:
            condiciones.append(" OR ".join([f"{campo} LIKE ?" for campo in self.CAMPOS_BUSQUEDA]))
        if self.filtros['estado'] != 'Todos':
            condiciones.append("estado = ?")
        if self.filtros['direccion'] != 'Todos':
            condiciones.append("direccion = ?")
            
        return "WHERE " + " AND ".join(condiciones) if condiciones else ""

    def _construir_orden(self):
        if not self.orden['columna']:
            return "id DESC"
        return f"{self.orden['columna']} {'ASC' if self.orden['ascendente'] else 'DESC'}"

    def _actualizar_filtro_direcciones(self):
        direcciones = sorted({cliente['direccion'] for cliente in self.datos})
        self.combo_direccion['values'] = ["Todos"] + direcciones

    def _aplicar_debounce_filtros(self):
        if hasattr(self, '_timer_filtro'):
            self._timer_filtro.cancel()
        self._timer_filtro = Timer(0.3, self._aplicar_filtros)
        self._timer_filtro.start()

    def _aplicar_filtros(self, event=None):
        self.filtros.update({
            'busqueda': self.entrada_busqueda.get().strip(),
            'estado': self.combo_estado.get(),
            'direccion': self.combo_direccion.get()
        })
        self._cargar_datos()

    def _ordenar_por_columna(self, columna):
        if self.orden['columna'] == columna:
            self.orden['ascendente'] = not self.orden['ascendente']
        else:
            self.orden['columna'] = columna
            self.orden['ascendente'] = True
        self._cargar_datos()

    def _actualizar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        for cliente in self.datos:
            tags = ('inactivo',) if cliente['estado'] == self.ESTADOS['INACTIVO'] else ('activo',)
            self.tabla.insert("", tk.END, values=tuple(cliente[col[0]] for col in self.COLUMNAS['Principal']), tags=tags)

    def _actualizar_boton_estado(self):
        seleccion = self.tabla.focus()
        if not seleccion:
            self.btn_estado.config(state="disabled")
            return
            
        cliente = self.tabla.item(seleccion, 'values')
        if not cliente:
            self.btn_estado.config(state="disabled")
            return
            
        nuevo_estado = self.ESTADOS['INACTIVO'] if cliente[4] == self.ESTADOS['ACTIVO'] else self.ESTADOS['ACTIVO']
        self.btn_estado.config(
            text=f"{'🟢' if nuevo_estado == self.ESTADOS['ACTIVO'] else '🔴'} {nuevo_estado}",
            state="normal"
        )

    def _cambiar_estado_cliente(self):
        seleccion = self.tabla.focus()
        if not seleccion:
            return

        cliente = self.tabla.item(seleccion)
        cliente_id = cliente['values'][0]
        nuevo_estado = self.ESTADOS['INACTIVO'] if cliente['values'][4] == self.ESTADOS['ACTIVO'] else self.ESTADOS['ACTIVO']

        if messagebox.askyesno("Confirmar", f"¿Cambiar estado a {nuevo_estado}?"):
            try:
                ejecutar_query(
                    "UPDATE clientes SET estado = ? WHERE id = ?",
                    (nuevo_estado, cliente_id)
                )
                # Actualizar datos localmente sin recargar toda la base de datos
                for c in self.datos:
                    if c['id'] == cliente_id:
                        c['estado'] = nuevo_estado
                self._actualizar_tabla()
            except Exception as e:
                messagebox.showerror("Error", f"Error actualizando estado: {str(e)}")

    def _abrir_dialogo_nuevo(self):
        dialogo = tk.Toplevel(self)
        dialogo.title("Nuevo Cliente")
        
        campos = [
            ('nombre', 'Nombre'),
            ('tipo', 'Tipo'),
            ('direccion', 'Dirección'),
            ('estado', 'Estado')
        ]
        
        entries = {}
        for idx, (campo, label) in enumerate(campos):
            ttk.Label(dialogo, text=label).grid(row=idx, column=0, padx=5, pady=5)
            entry = ttk.Combobox(dialogo) if campo == 'estado' else ttk.Entry(dialogo)
            if campo == 'estado':
                entry['values'] = [self.ESTADOS['ACTIVO'], self.ESTADOS['INACTIVO']]
                entry.set(self.ESTADOS['ACTIVO'])
            entry.grid(row=idx, column=1, padx=5, pady=5)
            entries[campo] = entry

        ttk.Button(
            dialogo,
            text="Guardar",
            command=lambda: self._guardar_nuevo_cliente(entries, dialogo)
        ).grid(row=len(campos), columnspan=2, pady=10)

    def _guardar_nuevo_cliente(self, entries, dialogo):
        datos = {
            'nombre': entries['nombre'].get().strip(),
            'tipo': entries['tipo'].get().strip(),
            'direccion': entries['direccion'].get().strip(),
            'estado': entries['estado'].get()
        }
        
        if not all(datos.values()):
            messagebox.showwarning("Validación", "Todos los campos son requeridos")
            return
            
        try:
            ejecutar_query(
                """INSERT INTO clientes (nombre, tipo, direccion, estado)
                VALUES (?, ?, ?, ?)""",
                tuple(datos.values())
            )
            self._cargar_datos()
            dialogo.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando cliente: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    PantallaClientes(root).pack(fill="both", expand=True)
    root.mainloop()