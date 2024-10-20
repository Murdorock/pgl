import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from src.database.db_config import configurar_base_datos
from datetime import datetime
from tkcalendar import DateEntry

class VentanaPersonal:
    def __init__(self, root):
        self.ventana = tk.Toplevel(root)
        self.ventana.title("Gestión de Personal")
        self.ventana.geometry("1000x600")
        
        self.conn = configurar_base_datos()
        self.cursor = self.conn.cursor()
        
        self.crear_widgets()
        self.actualizar_tabla()

    def crear_widgets(self):
        # Frame para botones
        frame_botones = tk.Frame(self.ventana)
        frame_botones.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        # Botones CRUD
        ttk.Button(frame_botones, text="Añadir", command=self.añadir_empleado).pack(pady=5, fill=tk.X)
        ttk.Button(frame_botones, text="Editar", command=self.editar_empleado).pack(pady=5, fill=tk.X)
        ttk.Button(frame_botones, text="Eliminar", command=self.eliminar_empleado).pack(pady=5, fill=tk.X)
        ttk.Button(frame_botones, text="Buscar", command=self.buscar_empleado).pack(pady=5, fill=tk.X)

        # Tabla
        columnas = ("CODIGO", "NOMBRE_COMPLETO", "NUMERO_CEDULA", "CELULAR_CORPORATIVO", "CELULAR", "CARGO", "FECHA", "DIAS", "CORREO")
        self.tabla = ttk.Treeview(self.ventana, columns=columnas, show="headings")
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100)
        self.tabla.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

    def actualizar_tabla(self):
        for i in self.tabla.get_children():
            self.tabla.delete(i)

        self.cursor.execute("SELECT * FROM Personal")
        empleados = self.cursor.fetchall()
        for empleado in empleados:
            self.tabla.insert("", "end", values=empleado)

    def añadir_empleado(self):
        ventana_añadir = tk.Toplevel(self.ventana)
        ventana_añadir.title("Añadir Empleado")

        campos = ["CODIGO", "NOMBRE_COMPLETO", "NUMERO_CEDULA", "CELULAR_CORPORATIVO", "CELULAR", "CARGO", "FECHA", "DIAS", "CORREO"]
        entries = {}

        for i, campo in enumerate(campos):
            tk.Label(ventana_añadir, text=f"{campo}:").grid(row=i, column=0, padx=5, pady=5)
            entries[campo] = tk.Entry(ventana_añadir)
            entries[campo].grid(row=i, column=1, padx=5, pady=5)

        def guardar():
            valores = [entries[campo].get() for campo in campos]
            if all(valores):
                try:
                    self.cursor.execute(f"INSERT INTO Personal ({','.join(campos)}) VALUES ({','.join(['?' for _ in campos])})", valores)
                    self.conn.commit()
                    self.actualizar_tabla()
                    ventana_añadir.destroy()
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Error al añadir empleado: {e}")
            else:
                messagebox.showerror("Error", "Todos los campos son obligatorios")

        ttk.Button(ventana_añadir, text="Guardar", command=guardar).grid(row=len(campos), column=0, columnspan=2, pady=10)

    def editar_empleado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showerror("Error", "Por favor, seleccione un empleado para editar")
            return

        empleado = self.tabla.item(seleccion)['values']
        ventana_editar = tk.Toplevel(self.ventana)
        ventana_editar.title("Editar Empleado")

        campos = ["CODIGO", "NOMBRE_COMPLETO", "NUMERO_CEDULA", "CELULAR_CORPORATIVO", "CELULAR", "CARGO", "FECHA", "DIAS", "CORREO"]
        entries = {}

        for i, campo in enumerate(campos):
            tk.Label(ventana_editar, text=f"{campo}:").grid(row=i, column=0, padx=5, pady=5)
            if campo == "FECHA":
                try:
                    fecha_actual = datetime.strptime(empleado[i], "%m/%d/%Y")
                except ValueError:
                    fecha_actual = datetime.now()
                entries[campo] = DateEntry(ventana_editar, width=12, background='darkblue',
                                           foreground='white', borderwidth=2, date_pattern='mm/dd/yyyy')
                entries[campo].set_date(fecha_actual)
            else:
                entries[campo] = tk.Entry(ventana_editar)
                entries[campo].insert(0, empleado[i])
            entries[campo].grid(row=i, column=1, padx=5, pady=5)

        def actualizar():
            valores = []
            for campo in campos:
                if campo == "FECHA":
                    valores.append(entries[campo].get_date().strftime("%m/%d/%Y"))
                else:
                    valores.append(entries[campo].get())
            
            if all(valores):
                try:
                    self.cursor.execute(f"UPDATE Personal SET {','.join([f'{campo}=?' for campo in campos[1:]])} WHERE CODIGO=?", valores[1:] + [valores[0]])
                    self.conn.commit()
                    self.actualizar_tabla()
                    ventana_editar.destroy()
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Error al actualizar empleado: {e}")
            else:
                messagebox.showerror("Error", "Todos los campos son obligatorios")

        ttk.Button(ventana_editar, text="Actualizar", command=actualizar).grid(row=len(campos), column=0, columnspan=2, pady=10)

    def eliminar_empleado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showerror("Error", "Por favor, seleccione un empleado para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este empleado?"):
            empleado = self.tabla.item(seleccion)['values']
            try:
                self.cursor.execute("DELETE FROM Personal WHERE CODIGO=?", (empleado[0],))
                self.conn.commit()
                self.actualizar_tabla()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al eliminar empleado: {e}")

    def buscar_empleado(self):
        ventana_buscar = tk.Toplevel(self.ventana)
        ventana_buscar.title("Buscar Empleado")

        tk.Label(ventana_buscar, text="Buscar por:").grid(row=0, column=0, padx=5, pady=5)
        campo_busqueda = ttk.Combobox(ventana_buscar, values=["CODIGO", "NOMBRE_COMPLETO", "NUMERO_CEDULA"])
        campo_busqueda.grid(row=0, column=1, padx=5, pady=5)
        campo_busqueda.set("NOMBRE_COMPLETO")

        tk.Label(ventana_buscar, text="Valor:").grid(row=1, column=0, padx=5, pady=5)
        valor_busqueda = tk.Entry(ventana_buscar)
        valor_busqueda.grid(row=1, column=1, padx=5, pady=5)

        def realizar_busqueda():
            campo = campo_busqueda.get()
            valor = valor_busqueda.get()
            if valor:
                try:
                    self.cursor.execute(f"SELECT * FROM Personal WHERE {campo} LIKE ?", (f"%{valor}%",))
                    resultados = self.cursor.fetchall()
                    self.mostrar_resultados(resultados)
                    ventana_buscar.destroy()
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Error al buscar empleado: {e}")
            else:
                messagebox.showerror("Error", "Por favor, ingrese un valor para buscar")

        ttk.Button(ventana_buscar, text="Buscar", command=realizar_busqueda).grid(row=2, column=0, columnspan=2, pady=10)

    def mostrar_resultados(self, resultados):
        for i in self.tabla.get_children():
            self.tabla.delete(i)
        for resultado in resultados:
            self.tabla.insert("", "end", values=resultado)

    def __del__(self):
        self.conn.close()

def abrir_ventana_personal(root):
    VentanaPersonal(root)