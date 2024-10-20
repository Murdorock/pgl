import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from src.database.db_config import configurar_base_datos
from datetime import datetime

class VentanaCambios:
    def __init__(self, root):
        self.ventana = tk.Toplevel(root)
        self.ventana.title("Gestión de Cambios")
        self.ventana.geometry("1200x600")
        
        self.conn = configurar_base_datos()
        self.cursor = self.conn.cursor()
        
        self.crear_tabla_cambios()
        self.crear_widgets()

    def crear_tabla_cambios(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Cambios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    CELULAR_CORPORATIVO TEXT,
                    CELULAR TEXT,
                    SUPERVISOR TEXT,
                    CODIGO TEXT,
                    REEMPLAZA_A TEXT,
                    CORRERIA TEXT,
                    NOVEDAD TEXT,
                    CALI TEXT,
                    CEDULA TEXT,
                    PEBDUI TEXT,
                    FECHA DATETIME
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al crear la tabla de cambios: {e}")

    def crear_widgets(self):
        # Frame para controles
        frame_controles = tk.Frame(self.ventana)
        frame_controles.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        # Plantilla de lectura
        tk.Label(frame_controles, text="Plantilla de lectura:").pack(anchor="w")
        self.plantilla_lectura = ttk.Combobox(frame_controles, state="readonly")
        self.plantilla_lectura.pack(fill=tk.X, pady=(0, 10))
        self.cargar_plantillas()

        # Lector Asignado
        tk.Label(frame_controles, text="Lector Asignado:").pack(anchor="w")
        self.lector_asignado = ttk.Combobox(frame_controles, state="readonly")
        self.lector_asignado.pack(fill=tk.X)
        self.cargar_lectores(self.lector_asignado)
        ttk.Button(frame_controles, text="Buscar", command=self.buscar_lector).pack(fill=tk.X, pady=(5, 10))

        # Lector que realizará
        tk.Label(frame_controles, text="Lector que realizará:").pack(anchor="w")
        self.lector_realizara = ttk.Combobox(frame_controles, state="readonly")
        self.lector_realizara.pack(fill=tk.X)
        self.cargar_lectores(self.lector_realizara)

        # Novedad
        tk.Label(frame_controles, text="Novedad:").pack(anchor="w")
        self.novedad = ttk.Combobox(frame_controles, state="readonly")
        self.novedad.pack(fill=tk.X)
        self.cargar_novedades()

        ttk.Button(frame_controles, text="Cambiar", command=self.cambiar_lector).pack(fill=tk.X, pady=(5, 10))

        # Tabla de resultados
        columnas = ("CELULAR_CORPORATIVO", "CELULAR", "SUPERVISOR", "CODIGO", "REEMPLAZA_A", "CORRERIA", "NOVEDAD", "CALI", "CEDULA", "PEBDUI")
        self.tabla = ttk.Treeview(self.ventana, columns=columnas, show="headings")
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100)
        self.tabla.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.actualizar_tabla_cambios()

    def cargar_plantillas(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Ciclo%'")
        plantillas = [row[0] for row in self.cursor.fetchall()]
        self.plantilla_lectura['values'] = plantillas

    def cargar_lectores(self, combobox):
        lectores = [f"LEC_{str(i).zfill(3)}" for i in range(1, 371)]
        combobox['values'] = lectores

    def cargar_novedades(self):
        novedades = ["INCAPACIDAD", "PERMISO", "AUSENTISMO", "PRACTICA", "COMPENSATORIO", "PATERNIDAD", "VACACIONES", "CALAMIDAD", "REEMPLAZO", "SUSPENDIDO", "CAPACITACION", "RESTRICCION", "VACANTE", "APOYO", "REPARTIDA"]
        self.novedad['values'] = novedades

    def buscar_lector(self):
        plantilla = self.plantilla_lectura.get()
        lector = self.lector_asignado.get()
        if not plantilla or not lector:
            messagebox.showerror("Error", "Por favor, seleccione una plantilla y un lector.")
            return

        try:
            # Buscar datos en la plantilla de lectura
            self.cursor.execute(f"SELECT CODIGO, SUPERVISOR, CORRERIA, CALI FROM {plantilla} WHERE CODIGO = ?", (lector,))
            datos_plantilla = self.cursor.fetchone()
            if not datos_plantilla:
                messagebox.showinfo("Información", f"No se encontró el lector {lector} en la plantilla {plantilla}")
                return

            # Buscar datos en la tabla Personal
            self.cursor.execute("SELECT CELULAR_CORPORATIVO, CELULAR, NUMERO_CEDULA FROM Personal WHERE CODIGO = ?", (lector,))
            datos_personal = self.cursor.fetchone()
            if not datos_personal:
                messagebox.showinfo("Información", f"No se encontraron datos personales para el lector {lector}")
                return

            # Combinar los datos en el orden correcto
            datos_completos = (
                datos_personal[0],  # CELULAR_CORPORATIVO
                datos_personal[1],  # CELULAR
                datos_plantilla[1],  # SUPERVISOR
                datos_plantilla[0],  # CODIGO
                "",                 # REEMPLAZA_A (vacío)
                datos_plantilla[2],  # CORRERIA
                "",                 # NOVEDAD (vacío)
                datos_plantilla[3],  # CALI
                datos_personal[2],  # CEDULA
                ""                  # PEBDUI (vacío)
            )
            self.actualizar_tabla([datos_completos])

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al buscar el lector: {e}")

    def cambiar_lector(self):
        plantilla = self.plantilla_lectura.get()
        lector_actual = self.lector_asignado.get()
        lector_nuevo = self.lector_realizara.get()
        novedad = self.novedad.get()
        if not plantilla or not lector_actual or not lector_nuevo or not novedad:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return

        try:
            # Obtener datos del lector actual
            self.cursor.execute(f"SELECT SUPERVISOR, CORRERIA, CALI FROM {plantilla} WHERE CODIGO = ?", (lector_actual,))
            datos_plantilla = self.cursor.fetchone()
            if not datos_plantilla:
                messagebox.showerror("Error", f"No se encontró el lector {lector_actual} en la plantilla {plantilla}")
                return

            # Obtener datos del nuevo lector
            self.cursor.execute("SELECT CELULAR_CORPORATIVO, CELULAR, NUMERO_CEDULA FROM Personal WHERE CODIGO = ?", (lector_nuevo,))
            datos_personal = self.cursor.fetchone()
            if not datos_personal:
                messagebox.showerror("Error", f"No se encontraron datos personales para el lector {lector_nuevo}")
                return

            # Realizar el cambio en la plantilla de lectura
            self.cursor.execute(f"UPDATE {plantilla} SET CODIGO = ? WHERE CODIGO = ?", (lector_nuevo, lector_actual))

            # Registrar el cambio en la tabla Cambios
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                INSERT INTO Cambios (CELULAR_CORPORATIVO, CELULAR, SUPERVISOR, CODIGO, REEMPLAZA_A, CORRERIA, NOVEDAD, CALI, CEDULA, PEBDUI, FECHA)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (datos_personal[0], datos_personal[1], datos_plantilla[0], lector_nuevo, lector_actual, datos_plantilla[1], novedad, datos_plantilla[2], datos_personal[2], "", fecha_actual))

            # Actualizar la tabla Novedades
            self.cursor.execute(f'''
                UPDATE Novedades 
                SET {novedad} = CASE
                    WHEN {novedad} IS NULL OR {novedad} = '' THEN ?
                    ELSE {novedad} || ', ' || ?
                END
                WHERE ID = (
                    SELECT ID FROM Novedades
                    WHERE (
                        {novedad} IS NULL OR {novedad} = ''
                        OR {novedad} NOT LIKE '%' || ? || '%'
                    )
                    LIMIT 1
                )
            ''', (lector_actual, lector_actual, lector_actual))

            self.conn.commit()

            messagebox.showinfo("Éxito", f"El lector {lector_actual} ha sido reemplazado por {lector_nuevo} y registrado en Novedades.")
            self.actualizar_tabla_cambios()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cambiar el lector: {e}")

    def actualizar_tabla(self, resultados):
        for i in self.tabla.get_children():
            self.tabla.delete(i)
        for resultado in resultados:
            self.tabla.insert("", "end", values=resultado)

    def actualizar_tabla_cambios(self):
        try:
            self.cursor.execute("SELECT CELULAR_CORPORATIVO, CELULAR, SUPERVISOR, CODIGO, REEMPLAZA_A, CORRERIA, NOVEDAD, CALI, CEDULA, PEBDUI FROM Cambios ORDER BY FECHA DESC")
            cambios = self.cursor.fetchall()
            self.actualizar_tabla(cambios)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar la tabla de cambios: {e}")

    def __del__(self):
        self.conn.close()

def abrir_ventana_cambios(root):
    VentanaCambios(root)