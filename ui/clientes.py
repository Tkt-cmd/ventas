import tkinter as tk
from tkinter import ttk, messagebox
from threading import Timer
from db.db import obtener_datos, ejecutar_query
from ui.styles import AppTheme

class PantallaClientes(ttk.Frame):
    COLUMNAS = {
        'Principal': [
            ('id_cliente', 'ID', 60),
            ('nombre_completo', 'Nombre', 250),
            ('tipo_persona', 'Tipo', 150),
            ('direccion_principal', 'Dirección', 200),
            ('estado', 'Estado', 100),
        ]
    }
    
    ESTADOS = {
        1: 'Activo',
        0: 'Inactivo'
    }
    
    CAMPOS_BUSQUEDA = ['nombres', 'apellido_p', 'rfc']

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
        # Crear frame de controles como atributo de clase
        self.controles_frame = ttk.Frame(self)
        self.controles_frame.pack(fill=tk.X, padx=10, pady=10)

        # Búsqueda
        ttk.Label(self.controles_frame, text="Buscar:").pack(side=tk.LEFT)
        self.entrada_busqueda = ttk.Entry(self.controles_frame)
        self.entrada_busqueda.pack(side=tk.LEFT, padx=5)
        self.entrada_busqueda.bind("<KeyRelease>", lambda e: self._aplicar_debounce_filtros())

        # Filtro Estado
        ttk.Label(self.controles_frame, text="Estado:").pack(side=tk.LEFT, padx=(15, 0))
        self.combo_estado = ttk.Combobox(
            self.controles_frame,  # <-- Usar self.controles_frame
            values=["Todos", self.ESTADOS[0], self.ESTADOS[1]],
            state="readonly"
        )
        self.combo_estado.set("Todos")
        self.combo_estado.pack(side=tk.LEFT, padx=5)
        self.combo_estado.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())

        # Filtro Dirección
        ttk.Label(self.controles_frame, text="Dirección:").pack(side=tk.LEFT, padx=(15, 0))
        self.combo_direccion = ttk.Combobox(self.controles_frame, state="readonly")  # <-- Aquí también
        self.combo_direccion.pack(side=tk.LEFT, padx=5)
        self.combo_direccion.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())

        # Botones
        self.btn_estado = ttk.Button(
            self.controles_frame,  # <-- Y aquí
            text="↺ Activar/Inactivar",
            style="Secondary.TButton",
            command=self._cambiar_estado_cliente,
            state="disabled"
        )
        self.btn_estado.pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            self.controles_frame,  # <-- Y aquí
            text="➕ Nuevo Registro",
            style="Primary.TButton",
            command=self._abrir_dialogo_nuevo
        ).pack(side=tk.RIGHT, padx=5)

    def _configurar_tabla(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)

        self.tabla = ttk.Treeview(
            frame,
            columns=[col[0] for col in self.COLUMNAS['Principal']],
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )

        for col in self.COLUMNAS['Principal']:
            self.tabla.heading(col[0], text=col[1], command=lambda c=col[0]: self._ordenar_por_columna(c))
            self.tabla.column(col[0], width=col[2], anchor=tk.CENTER)

        scrollbar.config(command=self.tabla.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla.pack(fill=tk.BOTH, expand=True)
        self.tabla.bind("<<TreeviewSelect>>", lambda e: self._actualizar_boton_estado())

    def _cargar_datos(self):
        try:
            query = """
                SELECT 
                    c.id_cliente,
                    c.nombres || ' ' || COALESCE(c.apellido_p, '') AS nombre_completo,
                    c.tipo_persona,
                    d.calle || ' ' || d.numero_domicilio AS direccion_principal,
                    c.estado
                FROM Clientes c
                LEFT JOIN Direcciones d ON c.id_cliente = d.id_cliente AND d.principal = 1
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
                parametros.append(1 if self.filtros['estado'] == self.ESTADOS[1] else 0)
                
            # Obtener datos SIN return_dict
            self.datos = obtener_datos(query, parametros)
            
            self._actualizar_filtro_direcciones()
            self._actualizar_tabla()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando datos: {str(e)}")

    def _construir_where(self):
        condiciones = []
        if self.filtros['busqueda']:
            condiciones.append(" OR ".join([f"{campo} LIKE ?" for campo in self.CAMPOS_BUSQUEDA]))
        if self.filtros['estado'] != 'Todos':
            condiciones.append("c.estado = ?")
            
        return "WHERE " + " AND ".join(condiciones) if condiciones else ""

    def _construir_orden(self):
        if not self.orden['columna']:
            return "c.id_cliente DESC"  # <-- Especificar tabla
        return f"{self.orden['columna']} {'ASC' if self.orden['ascendente'] else 'DESC'}"

    def _actualizar_filtro_direcciones(self):
        direcciones = set()
        for cliente in self.datos:
            direccion = cliente[3] if cliente[3] else "Sin dirección"
            direcciones.add(direccion)
        
        self.combo_direccion['values'] = ["Todos"] + sorted(direcciones)
    
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
        column_map = {
            'id_cliente': 'c.id_cliente',
            'nombre_completo': 'nombre_completo',
            'tipo_persona': 'c.tipo_persona',
            'direccion_principal': 'direccion_principal',
            'estado': 'c.estado'
        }
        self.orden['columna'] = column_map.get(columna, 'c.id_cliente')
        if self.orden['columna'] == columna:
            self.orden['ascendente'] = not self.orden['ascendente']
        else:
            self.orden['columna'] = columna
            self.orden['ascendente'] = True
        self._cargar_datos()

    def _actualizar_tabla(self):
        """Actualiza la tabla con los datos formateados"""
        self.tabla.delete(*self.tabla.get_children())
        for cliente in self.datos:
            estado = self.ESTADOS[cliente[4]]  # Índice 4 para el estado
            direccion = cliente[3] or "Sin dirección"  # Índice 3 para dirección
            
            self.tabla.insert("", tk.END, values=(
                cliente[0],  # ID (índice 0)
                cliente[1],  # Nombre (índice 1)
                cliente[2],  # Tipo persona (índice 2)
                direccion,
                estado
            ), tags=('inactivo',) if cliente[4] == 0 else ('activo',))

    def _actualizar_boton_estado(self):
        seleccion = self.tabla.focus()
        if not seleccion:
            self.btn_estado.config(state="disabled")
            return
            
        cliente = self.tabla.item(seleccion, 'values')
        if not cliente:
            self.btn_estado.config(state="disabled")
            return

    def _cambiar_estado_cliente(self):
        seleccion = self.tabla.focus()
        if not seleccion:
            return

        cliente = self.tabla.item(seleccion, 'values')
        cliente_id = cliente[0]
        nuevo_estado = 0 if cliente[4] == self.ESTADOS[1] else 1  # Cambiar a 1/0

        if messagebox.askyesno("Confirmar", f"¿Cambiar estado a {self.ESTADOS[nuevo_estado]}?"):
            try:
                ejecutar_query(
                    "UPDATE Clientes SET estado = ? WHERE id_cliente = ?",
                    (nuevo_estado, cliente_id)
                )
                self._cargar_datos()  # Recargar datos completos
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
            'nombres': entries['nombres'].get().strip(),
            'apellido_p': entries['apellido_p'].get().strip(),
            'tipo_persona': entries['tipo_persona'].get(),
            'rfc': entries['rfc'].get().strip(),
            'estado': 1 if entries['estado'].get() == self.ESTADOS[1] else 0
        }
        
        if not datos['nombres']:
            messagebox.showwarning("Validación", "El nombre es requerido")
            return
            
        try:
            ejecutar_query(
                """INSERT INTO Clientes 
                (nombres, apellido_p, tipo_persona, rfc, estado, fecha_registro)
                VALUES (?, ?, ?, ?, ?, datetime('now'))""",
                (datos['nombres'], datos['apellido_p'], datos['tipo_persona'], 
                 datos['rfc'], datos['estado'])
            )
            self._cargar_datos()
            dialogo.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando cliente: {str(e)}")