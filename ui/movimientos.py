import tkinter as tk
from tkinter import ttk
from db.db import obtener_datos, ejecutar_query
from ui.styles import AppTheme
from utils import helpers

class PantallaMovimientos(ttk.Frame):
    """
    Plantilla base para módulos del sistema
    ------------------------------------------------------------
    Instrucciones de uso:
    1. Reemplazar [Modulo] por el nombre de la pantalla (Clientes, Movimientos, etc.)
    2. Configurar COLUMNAS según los datos a mostrar
    3. Personalizar _cargar_datos() con consulta SQL específica
    4. Implementar métodos específicos de la pantalla
    """
    
    COLUMNAS = {
        'Principal': [
            # (campo_bd, título, ancho)
            ('id', 'ID', 60),
            ('nombre', 'Nombre', 200),
            ('tipo', 'Tipo', 150),
        ]
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.theme = AppTheme()
        self.datos = []
        self.filtros_activos = {}
        
        # Configuración inicial
        self._cargar_datos()
        self._crear_widgets()
        self._actualizar_tabla()

    def _cargar_datos(self):
        """
        Cargar datos desde la base de datos
        ------------------------------------------------------------
        INSTRUCCIONES:
        1. Reemplazar la consulta SQL con la adecuada para el módulo
        2. Mantener el orden de los campos según COLUMNAS
        3. Usar obtener_datos() para ejecutar queries
        """
        self.datos = obtener_datos("""
            SELECT 
                id,
                nombre,
                tipo
            FROM [Tabla]
            ORDER BY id DESC
            """)
            
    def _crear_widgets(self):
        """
        Construir interfaz gráfica
        ------------------------------------------------------------
        COMPONENTES BÁSICOS:
        1. Frame de controles superiores
        2. Botones de acciones principales
        3. Tabla de datos
        4. Filtros de búsqueda
        """
        # Frame para controles superiores
        controles_frame = ttk.Frame(self)
        controles_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Ejemplo: Campo de búsqueda
        ttk.Label(controles_frame, text="Buscar:").pack(side=tk.LEFT)
        self.entrada_busqueda = ttk.Entry(controles_frame)
        self.entrada_busqueda.pack(side=tk.LEFT, padx=5)
        self.entrada_busqueda.bind("<KeyRelease>", self._aplicar_filtros)
        
        # Botón de acción principal
        ttk.Button(
            controles_frame,
            text="➕ Nuevo Registro",
            style="Primary.TButton",
            command=self._abrir_dialogo_nuevo
        ).pack(side=tk.RIGHT, padx=5)

        # Configurar tabla
        self._configurar_tabla()

    def _configurar_tabla(self):
        """Configurar tabla con columnas y estilos"""
        self.tabla_frame = ttk.Frame(self)
        self.tabla_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(self.tabla_frame, orient=tk.VERTICAL)
        
        # Crear tabla
        self.tabla = ttk.Treeview(
            self.tabla_frame,
            columns=[col[0] for col in self.COLUMNAS['Principal']],
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        
        # Configurar columnas
        for col in self.COLUMNAS['Principal']:
            self.tabla.heading(col[0], text=col[1], 
                            command=lambda c=col[0]: self._ordenar_por_columna(c))
            self.tabla.column(col[0], width=col[2], anchor=tk.CENTER)
        
        scrollbar.config(command=self.tabla.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla.pack(fill=tk.BOTH, expand=True)

    def _ordenar_por_columna(self, columna):
        """
        Ordenar datos por columna
        ------------------------------------------------------------
        INSTRUCCIONES:
        1. Implementar lógica de ordenamiento específica si es necesario
        2. Actualizar self.datos con los datos ordenados
        3. Llamar a _actualizar_tabla()
        """
        # Implementar lógica de ordenamiento
        self._actualizar_tabla()

    def _aplicar_filtros(self, event=None):
        """
        Aplicar filtros de búsqueda
        ------------------------------------------------------------
        INSTRUCCIONES:
        1. Obtener valores de los campos de filtro
        2. Filtrar self.datos según criterios
        3. Llamar a _actualizar_tabla() con datos filtrados
        """
        datos_filtrados = self.datos  # Implementar filtrado real
        self._actualizar_tabla(datos_filtrados)

    def _actualizar_tabla(self, datos=None):
        """Actualizar datos en la tabla"""
        self.tabla.delete(*self.tabla.get_children())
        for item in (datos or self.datos):
            self.tabla.insert("", tk.END, values=item)

    def _abrir_dialogo_nuevo(self):
        """
        Abrir diálogo para nuevo registro
        ------------------------------------------------------------
        INSTRUCCIONES:
        1. Crear diálogo específico para el módulo
        2. Implementar lógica de guardado
        3. Actualizar datos después de guardar
        """
        # Ejemplo básico
        dialogo = tk.Toplevel(self)
        # Implementar diálogo real
        # Al guardar: self._cargar_datos() y self._actualizar_tabla()

if __name__ == "__main__":
    root = tk.Tk()
    app = Pantalla[Modulo](root)
    root.mainloop()