import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

def crear_widgets(root):
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