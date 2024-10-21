import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from src.database.db_config import configurar_base_datos
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

class VentanaProgramaciones:
    def __init__(self, root):
        self.ventana = tk.Toplevel(root)
        self.ventana.title("Programaciones")
        self.ventana.geometry("1200x600")
        
        self.conn = configurar_base_datos()
        self.cursor = self.conn.cursor()
        
        self.crear_widgets()

    def crear_widgets(self):
        # Frame principal
        frame_principal = ttk.Frame(self.ventana, padding="10")
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Frame izquierdo para controles
        frame_izquierdo = ttk.Frame(frame_principal, width=200)
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        frame_izquierdo.pack_propagate(False)

        # Combobox para seleccionar la tabla Ciclo
        ttk.Label(frame_izquierdo, text="Seleccionar Ciclo:").pack(anchor=tk.W, pady=(0, 5))
        self.combo_ciclos = ttk.Combobox(frame_izquierdo, state="readonly", width=25)
        self.combo_ciclos.pack(anchor=tk.W, pady=(0, 10))
        self.cargar_ciclos()

        # Campo de búsqueda
        ttk.Label(frame_izquierdo, text="Buscar:").pack(anchor=tk.W, pady=(0, 5))
        self.entrada_busqueda = ttk.Entry(frame_izquierdo, width=28)
        self.entrada_busqueda.pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(frame_izquierdo, text="Buscar", command=self.buscar).pack(anchor=tk.W, pady=(0, 10))

        # Botón para exportar por zona
        ttk.Button(frame_izquierdo, text="Exportar por Zona", command=self.exportar_por_zona).pack(anchor=tk.W, pady=(0, 10))

        # Frame para la tabla y scrollbars
        frame_tabla = ttk.Frame(frame_principal)
        frame_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tabla de resultados
        self.tabla = ttk.Treeview(frame_tabla, selectmode='extended')
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar vertical
        scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla.configure(yscrollcommand=scrollbar_y.set)

        # Scrollbar horizontal
        scrollbar_x = ttk.Scrollbar(frame_principal, orient="horizontal", command=self.tabla.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tabla.configure(xscrollcommand=scrollbar_x.set)

    def cargar_ciclos(self):
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Ciclo%'")
            ciclos = [row[0] for row in self.cursor.fetchall()]
            self.combo_ciclos['values'] = ciclos
            if ciclos:
                self.combo_ciclos.set(ciclos[0])
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los ciclos: {str(e)}")

    def buscar(self):
        ciclo_seleccionado = self.combo_ciclos.get()
        termino_busqueda = self.entrada_busqueda.get()

        if not ciclo_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un ciclo.")
            return

        # Limpiar tabla
        for i in self.tabla.get_children():
            self.tabla.delete(i)

        try:
            # Obtener todas las columnas de la tabla
            self.cursor.execute(f"PRAGMA table_info({ciclo_seleccionado})")
            columnas = [info[1] for info in self.cursor.fetchall()]

            if not columnas:
                messagebox.showwarning("Advertencia", "No se encontraron columnas en la tabla seleccionada.")
                return

            # Configurar columnas de la tabla
            self.tabla['columns'] = columnas
            self.tabla.column('#0', width=0, stretch=tk.NO)  # Ocultar la primera columna

            # Realizar búsqueda
            query = f"SELECT * FROM {ciclo_seleccionado} WHERE " + " OR ".join([f"{col} LIKE ?" for col in columnas])
            self.cursor.execute(query, tuple(f"%{termino_busqueda}%" for _ in columnas))
            resultados = self.cursor.fetchall()

            if not resultados:
                messagebox.showinfo("Información", "No se encontraron resultados")
                return

            # Calcular el ancho máximo para cada columna
            anchos_maximos = [len(col) for col in columnas]  # Inicializar con el ancho del encabezado
            for resultado in resultados:
                for i, valor in enumerate(resultado):
                    if valor is not None:
                        anchos_maximos[i] = max(anchos_maximos[i], len(str(valor)))

            # Configurar columnas de la tabla con los anchos calculados
            for i, col in enumerate(columnas):
                ancho = min(anchos_maximos[i] * 10, 300)  # Limitar el ancho máximo a 300 píxeles
                self.tabla.heading(col, text=col, anchor=tk.CENTER)
                self.tabla.column(col, anchor=tk.CENTER, width=ancho)

            # Mostrar resultados en la tabla
            for resultado in resultados:
                self.tabla.insert('', tk.END, values=resultado)

        except Exception as e:
            messagebox.showerror("Error", f"Error al realizar la búsqueda: {str(e)}")
            print(f"Error detallado: {e}")  # Para depuración

    def exportar_por_zona(self):
        zona = simpledialog.askstring("Exportar por Zona", "Ingrese la zona a exportar (ej. Z01):")
        if not zona:
            return

        ciclo_seleccionado = self.combo_ciclos.get()
        if not ciclo_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un ciclo.")
            return

        try:
            # Obtener columnas
            self.cursor.execute(f"PRAGMA table_info({ciclo_seleccionado})")
            columnas = [info[1] for info in self.cursor.fetchall()]

            # Realizar búsqueda por zona
            query = f"SELECT * FROM {ciclo_seleccionado} WHERE ZONA = ?"
            self.cursor.execute(query, (zona,))
            resultados = self.cursor.fetchall()

            if not resultados:
                messagebox.showinfo("Información", f"No se encontraron resultados para la zona {zona}")
                return

            # Generar PDF
            ruta_pdf = self.generar_pdf(columnas, resultados)

            if ruta_pdf:
                messagebox.showinfo("Éxito", f"PDF generado exitosamente: {ruta_pdf}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar por zona: {str(e)}")
            print(f"Error detallado: {e}")  # Para depuración

    def generar_pdf(self, columnas, datos):
        try:
            ruta_pdf = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if not ruta_pdf:
                return None

            # Usar orientación horizontal (landscape)
            doc = SimpleDocTemplate(ruta_pdf, pagesize=landscape(letter))
            elementos = []

            datos_tabla = [columnas] + list(datos)
            t = Table(datos_tabla)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 4),  # Reducido el tamaño de fuente
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 4),  # Reducido el tamaño de fuente
                ('TOPPADDING', (0, 1), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elementos.append(t)
            doc.build(elementos)
            return ruta_pdf
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el PDF: {str(e)}")
            return None

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

def abrir_ventana_programaciones(root):
    VentanaProgramaciones(root)