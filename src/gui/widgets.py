import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from src.gui.novedades import abrir_ventana_novedades
from src.gui.personal import abrir_ventana_personal
from src.gui.cambios import abrir_ventana_cambios
from src.gui.historicos import abrir_ventana_historicos
from src.gui.programaciones import abrir_ventana_programaciones

def crear_widgets(root):
    # Crear la barra de menú
    barra_menu = tk.Menu(root)
    root.config(menu=barra_menu)

    # Crear el menú de navegación
    menu_navegacion = tk.Menu(barra_menu, tearoff=0)
    barra_menu.add_cascade(label="Navegación", menu=menu_navegacion)

    # Añadir opciones al menú de navegación
    menu_navegacion.add_command(label="Novedades", command=lambda: abrir_ventana(root, "Novedades"))
    menu_navegacion.add_command(label="Cambios", command=lambda: abrir_ventana(root, "Cambios"))
    menu_navegacion.add_command(label="Personal", command=lambda: abrir_ventana(root, "Personal"))
    menu_navegacion.add_command(label="Históricos", command=lambda: abrir_ventana(root, "Históricos"))
    menu_navegacion.add_command(label="Programaciones", command=lambda: abrir_ventana(root, "Programaciones"))

    frame_izquierda = tk.Frame(root)
    frame_izquierda.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    ciclo_var = tk.StringVar()
    mes_var = tk.StringVar()

    ciclo_label = tk.Label(frame_izquierda, text="Ciclo seleccionado: ")
    ciclo_label.pack(anchor='w')
    ciclo_combobox = ttk.Combobox(frame_izquierda, textvariable=ciclo_var)
    ciclo_combobox['values'] = list(range(1, 21))
    ciclo_combobox.pack(anchor='w')

    mes_label = tk.Label(frame_izquierda, text="Mes seleccionado: ")
    mes_label.pack(anchor='w')
    mes_combobox = ttk.Combobox(frame_izquierda, textvariable=mes_var)
    mes_combobox['values'] = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_combobox.pack(anchor='w')

    cal = DateEntry(frame_izquierda, width=12, year=2024, month=10, day=13, background='darkblue', foreground='white', borderwidth=2)
    cal.pack(pady=3)

    return frame_izquierda, ciclo_var, mes_var, ciclo_label, mes_label, cal

def abrir_ventana(root, nombre_ventana):
    if nombre_ventana == "Novedades":
        abrir_ventana_novedades(root)
    elif nombre_ventana == "Personal":
        abrir_ventana_personal(root)
    elif nombre_ventana == "Cambios":
        abrir_ventana_cambios(root)
    elif nombre_ventana == "Históricos":
        abrir_ventana_historicos(root)
    elif nombre_ventana == "Programaciones":
        abrir_ventana_programaciones(root)
    else:
        # Manejo temporal para otras ventanas
        nueva_ventana = tk.Toplevel(root)
        nueva_ventana.title(nombre_ventana)
        nueva_ventana.geometry("400x300")
        tk.Label(nueva_ventana, text=f"Ventana de {nombre_ventana}").pack(pady=20)

def configurar_tabla(root):
    frame_derecha = tk.Frame(root)
    frame_derecha.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    scrollbar_vertical = ttk.Scrollbar(frame_derecha, orient=tk.VERTICAL)
    scrollbar_horizontal = ttk.Scrollbar(frame_derecha, orient=tk.HORIZONTAL)

    columnas = ["FECHA", "CICLO", "MES", "CORRERIA", "NOMBRE_CORRERIA", "ZONA", "SUPERVISOR", "TRANSPORTE", "GV", "CALI", "TERRENO", "NOMBRE_ZONA", "HIST2", "HIST1", "CODIGO", "DIAS", "TOTALES", "NOMBRE_LECTOR", "TELEFONO", "DIFERENCIA", "CEDULA_FUNCIONARIO"]
    tabla = ttk.Treeview(frame_derecha, columns=columnas, show="headings", yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)
    
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor='w')

    scrollbar_vertical.config(command=tabla.yview)
    scrollbar_horizontal.config(command=tabla.xview)

    scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X)
    tabla.pack(fill=tk.BOTH, expand=True)

    return tabla