import tkinter as tk
from tkinter import ttk, messagebox
from src.database.db_config import configurar_base_datos
from ttkwidgets.autocomplete import AutocompleteCombobox

class VentanaNovedades:
    def __init__(self, root):
        self.root = root
        self.root.title("Novedades")
        self.root.geometry("1200x600")
        
        self.tipos_novedad = ["INCAPACIDAD", "PERMISO", "AUSENTISMO", "PRACTICA", "COMPENSATORIO", "PATERNIDAD", "VACACIONES", "CALAMIDAD", "REEMPLAZO", "SUSPENDIDO", "CAPACITACION", "RESTRICCION", "VACANTE", "APOYO", "REPARTIDA"]
        
        self.crear_tabla_si_no_existe()
        self.crear_widgets()
        self.cargar_novedades()

    def crear_tabla_si_no_existe(self):
        conexion = configurar_base_datos()
        cursor = conexion.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS Novedades_Global (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                {", ".join([f"{tipo} TEXT" for tipo in self.tipos_novedad])}
            )
        ''')
        conexion.commit()
        conexion.close()

    def crear_widgets(self):
        # Frame principal
        self.frame_principal = ttk.Frame(self.root, padding="10")
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        # Frame izquierdo para controles
        frame_izquierdo = ttk.Frame(self.frame_principal, padding="10", width=300)
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        frame_izquierdo.pack_propagate(False)  # Evita que el frame se encoja

        # Campos de entrada
        ttk.Label(frame_izquierdo, text="Código:").pack(anchor=tk.W, pady=(0, 5))
        self.entrada_codigo = AutocompleteCombobox(frame_izquierdo, completevalues=self.generar_codigos(), width=28)
        self.entrada_codigo.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(frame_izquierdo, text="Tipo de Novedad:").pack(anchor=tk.W, pady=(0, 5))
        self.entrada_tipo = ttk.Combobox(frame_izquierdo, values=self.tipos_novedad, width=28)
        self.entrada_tipo.pack(anchor=tk.W, pady=(0, 10))

        # Botones
        ttk.Button(frame_izquierdo, text="Agregar Novedad", command=self.agregar_novedad, width=30).pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(frame_izquierdo, text="Eliminar Novedad", command=self.eliminar_novedad, width=30).pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(frame_izquierdo, text="Actualizar Tabla", command=self.cargar_novedades, width=30).pack(anchor=tk.W, pady=(0, 10))

        # Campo de búsqueda y botón
        ttk.Label(frame_izquierdo, text="Buscar:").pack(anchor=tk.W, pady=(0, 5))
        self.entrada_busqueda = ttk.Entry(frame_izquierdo, width=30)
        self.entrada_busqueda.pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(frame_izquierdo, text="Buscar", command=self.buscar_novedad, width=30).pack(anchor=tk.W)

        # Frame para la tabla
        frame_tabla = ttk.Frame(self.frame_principal)
        frame_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tabla de novedades
        self.tabla = ttk.Treeview(frame_tabla, columns=("ID", *self.tipos_novedad), show="headings", selectmode="browse")
        self.tabla.heading("ID", text="ID")
        self.tabla.column("ID", width=50, anchor=tk.CENTER)
        for col in self.tipos_novedad:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=80, anchor=tk.CENTER)

        # Configurar cuadrículas para la tabla
        self.tabla.tag_configure('evenrow', background='#f0f0f0')
        self.tabla.tag_configure('oddrow', background='#ffffff')
        
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar para la tabla
        scrollbar_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar_x = ttk.Scrollbar(self.frame_principal, orient=tk.HORIZONTAL, command=self.tabla.xview)
        self.tabla.configure(xscroll=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Agregar evento de selección
        self.tabla.bind("<<TreeviewSelect>>", self.on_select)
        
        # Agregar evento de doble clic para eliminar
        self.tabla.bind("<Double-1>", self.on_double_click)

    def on_select(self, event):
        seleccion = self.tabla.selection()
        if seleccion:
            item = self.tabla.item(seleccion[0])
            print(f"Item seleccionado: {item['values']}")
        else:
            print("Ningún item seleccionado")

    def on_double_click(self, event):
        item = self.tabla.identify('item', event.x, event.y)
        if item:
            print(f"Doble clic en el item: {self.tabla.item(item)['values']}")
            self.eliminar_novedad()
        else:
            print("Doble clic fuera de cualquier item")

    def generar_codigos(self):
        codigos = []
        codigos.extend([f"LEC_{str(i).zfill(3)}" for i in range(1, 371)])
        codigos.extend([f"SUP_{str(i).zfill(3)}" for i in range(1, 19)])
        codigos.extend([f"AUX_{str(i).zfill(3)}" for i in range(1, 5)])
        codigos.append("ADM04")
        return codigos

    def cargar_novedades(self):
        # Limpiar tabla existente
        for i in self.tabla.get_children():
            self.tabla.delete(i)

        # Cargar datos de la base de datos
        conexion = configurar_base_datos()
        cursor = conexion.cursor()
        cursor.execute(f"SELECT ID, {', '.join(self.tipos_novedad)} FROM Novedades_Global")
        for i, novedad in enumerate(cursor.fetchall()):
            id_novedad = novedad[0]
            valores = [valor if valor else "" for valor in novedad[1:]]
            if any(valores):  # Solo insertar si hay al menos un valor no vacío
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tabla.insert("", tk.END, values=(id_novedad, *valores), tags=(tag,))
        conexion.close()

        # Imprimir información de depuración
        # print("Contenido de la tabla después de cargar:")
        # for item in self.tabla.get_children():
        #     print(self.tabla.item(item)['values'])

    def agregar_novedad(self):
        codigos = self.entrada_codigo.get().split()
        tipo = self.entrada_tipo.get()

        if not codigos or not tipo:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        conexion = configurar_base_datos()
        cursor = conexion.cursor()
        try:
            for codigo in codigos:
                # Verificar si el código ya existe en cualquier columna
                cursor.execute(f"SELECT COUNT(*) FROM Novedades_Global WHERE {' OR '.join([f'{t} = ?' for t in self.tipos_novedad])}", (codigo,) * len(self.tipos_novedad))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", f"El código {codigo} ya existe en la tabla")
                    continue

                # Buscar una fila con espacio disponible
                cursor.execute(f"SELECT ID FROM Novedades_Global WHERE {tipo} IS NULL OR {tipo} = '' LIMIT 1")
                fila_disponible = cursor.fetchone()

                if fila_disponible:
                    # Actualizar fila existente
                    cursor.execute(f"UPDATE Novedades_Global SET {tipo} = ? WHERE ID = ?", (codigo, fila_disponible[0]))
                else:
                    # Insertar nueva fila
                    cursor.execute(f"INSERT INTO Novedades_Global ({tipo}) VALUES (?)", (codigo,))

            conexion.commit()
            messagebox.showinfo("Éxito", "Novedad(es) agregada(s) correctamente")
            self.cargar_novedades()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar la novedad: {str(e)}")
        finally:
            conexion.close()

    def eliminar_novedad(self):
        seleccion = self.tabla.selection()
        print(f"Selección en eliminar_novedad: {seleccion}")  # Información de depuración

        if not seleccion:
            messagebox.showerror("Error", "Por favor, seleccione una novedad para eliminar")
            return

        item = self.tabla.item(seleccion[0])
        valores = item['values']
        print(f"Valores del item seleccionado: {valores}")  # Información de depuración

        if not valores:
            messagebox.showerror("Error", "La fila seleccionada no contiene datos")
            return

        id_novedad = valores[0]
        codigo_a_eliminar = None
        tipo_novedad = None

        for i, valor in enumerate(valores[1:], start=1):
            if valor:
                codigo_a_eliminar = valor
                tipo_novedad = self.tipos_novedad[i-1]
                break

        if not codigo_a_eliminar:
            messagebox.showerror("Error", "No se encontró ningún código para eliminar")
            return

        # Preguntar al usuario si está seguro de eliminar
        confirmacion = messagebox.askyesno("Confirmar eliminación", f"¿Está seguro de que desea eliminar el código {codigo_a_eliminar}?")
        if not confirmacion:
            return

        conexion = configurar_base_datos()
        cursor = conexion.cursor()
        try:
            # Imprimir información de depuración
            print(f"Intentando eliminar código: {codigo_a_eliminar} del tipo: {tipo_novedad}")

            # Actualizar la fila, estableciendo el valor a NULL para el tipo de novedad correspondiente
            cursor.execute(f"UPDATE Novedades_Global SET {tipo_novedad} = NULL WHERE ID = ?", (id_novedad,))
            
            if cursor.rowcount == 0:
                messagebox.showwarning("Advertencia", f"No se pudo eliminar el código {codigo_a_eliminar}")
            else:
                conexion.commit()
                messagebox.showinfo("Éxito", f"Código {codigo_a_eliminar} eliminado correctamente")
            
            self.cargar_novedades()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la novedad: {str(e)}")
        finally:
            conexion.close()

    def buscar_novedad(self):
        busqueda = self.entrada_busqueda.get().strip()
        if not busqueda:
            messagebox.showerror("Error", "Por favor, ingrese un término de búsqueda")
            return

        # Limpiar tabla existente
        for i in self.tabla.get_children():
            self.tabla.delete(i)

        # Buscar en la base de datos
        conexion = configurar_base_datos()
        cursor = conexion.cursor()
        try:
            query = f"SELECT ID, {', '.join(self.tipos_novedad)} FROM Novedades_Global WHERE {' OR '.join([f'{tipo} LIKE ?' for tipo in self.tipos_novedad])}"
            cursor.execute(query, tuple(f'%{busqueda}%' for _ in self.tipos_novedad))
            resultados = cursor.fetchall()

            if not resultados:
                messagebox.showinfo("Búsqueda", "No se encontraron resultados")
            else:
                for i, novedad in enumerate(resultados):
                    id_novedad = novedad[0]
                    valores = [valor if valor else "" for valor in novedad[1:]]
                    if any(valores):  # Solo insertar si hay al menos un valor no vacío
                        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                        self.tabla.insert("", tk.END, values=(id_novedad, *valores), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar: {str(e)}")
        finally:
            conexion.close()

def abrir_ventana_novedades(root):
    ventana_novedades = tk.Toplevel(root)
    VentanaNovedades(ventana_novedades)