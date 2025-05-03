from tkinter import ttk
from ui.styles import AppTheme

class PantallaVentas(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.theme = AppTheme()
        
        # Botón Primario (Confirmar)
        btn_confirmar = ttk.Button(
            self,
            text="Confirmar Venta",
            style="Primary.TButton"
        )
        btn_confirmar.pack(pady=20, ipadx=15)
        
        # Botón Secundario (Cancelar)
        btn_cancelar = ttk.Button(
            self,
            text="Cancelar",
            style="Secondary.TButton"
        )
        btn_cancelar.pack(pady=10)
