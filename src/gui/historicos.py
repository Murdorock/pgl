import tkinter as tk
from tkinter import ttk, messagebox
from src.database.db_config import configurar_base_datos

class VentanaHistoricos:
    def __init__(self, root):
        self.ventana = tk.Toplevel(root)
        self.ventana.title("Consulta de Históricos")
        self.ventana.geometry("1200x600")
        
        self.conn = configurar_base_datos()
        self.cursor = self.conn.cursor()
        
        self.crear_widgets()

    def crear_widgets(self):
        # Frame para controles de búsqueda
        frame_busqueda = ttk.Frame(self.ventana, padding="10")
        frame_busqueda.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Búsqueda por Correria
        ttk.Label(frame_busqueda, text="Buscar por Correria:").pack(anchor=tk.W, pady=(0, 5))
        self.entrada_correria = ttk.Entry(frame_busqueda, width=30)
        self.entrada_correria.pack(anchor=tk.W, pady=(0, 10))
        ttk.Button(frame_busqueda, text="Buscar Correria", command=lambda: self.buscar('CORRERIA')).pack(anchor=tk.W, pady=(0, 10))

        # Búsqueda por Cédula
        ttk.Label(frame_busqueda, text="Buscar por Cédula:").pack(anchor=tk.W, pady=(0, 5))
        self.entrada_cedula = ttk.Entry(frame_busqueda, width=30)
        self.entrada_cedula.pack(anchor=tk.W, pady=(0, 10))
        ttk.Button(frame_busqueda, text="Buscar Cédula", command=lambda: self.buscar('CEDULA')).pack(anchor=tk.W, pady=(0, 10))

        # Búsqueda por Código
        ttk.Label(frame_busqueda, text="Buscar por Código:").pack(anchor=tk.W, pady=(0, 5))
        self.entrada_Lector = ttk.Entry(frame_busqueda, width=30)
        self.entrada_Lector.pack(anchor=tk.W, pady=(0, 10))
        ttk.Button(frame_busqueda, text="Buscar Código", command=lambda: self.buscar('Lector')).pack(anchor=tk.W)

        # Tabla de resultados
        self.tabla = ttk.Treeview(self.ventana)
        self.tabla.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configurar columnas de la tabla
        self.tabla['columns'] = ('CORRERIA', 'CEDULA', 'CODIGO', 'FECHA')
        self.tabla.column('#0', width=0, stretch=tk.NO)
        self.tabla.column('CORRERIA', anchor=tk.CENTER, width=150)
        self.tabla.column('CEDULA', anchor=tk.CENTER, width=150)
        self.tabla.column('CODIGO', anchor=tk.CENTER, width=150)
        self.tabla.column('FECHA', anchor=tk.CENTER, width=150)

        self.tabla.heading('#0', text='', anchor=tk.CENTER)
        self.tabla.heading('CORRERIA', text='Correria', anchor=tk.CENTER)
        self.tabla.heading('CEDULA', text='Cédula', anchor=tk.CENTER)
        self.tabla.heading('CODIGO', text='Código', anchor=tk.CENTER)
        self.tabla.heading('FECHA', text='Fecha', anchor=tk.CENTER)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(self.ventana, orient="vertical", command=self.tabla.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla.configure(yscrollcommand=scrollbar.set)

    def buscar(self, tipo_busqueda):
        # Limpiar tabla
        for i in self.tabla.get_children():
            self.tabla.delete(i)

        # Obtener valor de búsqueda
        if tipo_busqueda == 'CORRERIA':
            valor = self.entrada_correria.get()
        elif tipo_busqueda == 'CEDULA':
            valor = self.entrada_cedula.get()
        else:  # Lector
            valor = self.entrada_Lector.get()

        if not valor:
            messagebox.showwarning("Advertencia", f"Por favor, ingrese un valor para buscar por {tipo_busqueda}")
            return

        try:
            # Realizar búsqueda en la base de datos
            query = f"SELECT CORRERIA, CEDULA, Lector, MES FROM Historicos WHERE {tipo_busqueda} LIKE ?"
            self.cursor.execute(query, (f'%{valor}%',))
            resultados = self.cursor.fetchall()

            if not resultados:
                messagebox.showinfo("Información", "No se encontraron resultados")
                return

            # Mostrar resultados en la tabla
            for resultado in resultados:
                correria = resultado[0] if resultado[0] is not None else ""
                cedula = resultado[1] if resultado[1] is not None else ""
                codigo = resultado[2] if resultado[2] is not None else ""  # Lector se guarda como Código
                fecha = resultado[3] if resultado[3] is not None else ""  # MES se guarda como Fecha

                self.tabla.insert('', tk.END, values=(correria, cedula, codigo, fecha))

        except Exception as e:
            messagebox.showerror("Error", f"Error al realizar la búsqueda: {str(e)}")
            print(f"Error detallado: {e}")  # Para depuración

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

def abrir_ventana_historicos(root):
    VentanaHistoricos(root)