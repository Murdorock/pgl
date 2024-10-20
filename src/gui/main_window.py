import tkinter as tk
from tkinter import ttk
from .widgets import crear_widgets, configurar_tabla
from src.logic.plantilla_manager import llenar_plantilla

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PGL")
        self.root.geometry("1200x600")

        self.style = ttk.Style()
        self.style.configure("Treeview", font=("Helvetica", 8))
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        self.frame_izquierda, self.ciclo_var, self.mes_var, self.ciclo_label, self.mes_label, self.cal = crear_widgets(self.root)
        self.tabla = configurar_tabla(self.root)

        self.boton_programar = tk.Button(self.frame_izquierda, text="Programar", command=self.ejecutar_comandos)
        self.boton_programar.pack(pady=20)

    def ejecutar_comandos(self):
        nombre_plantilla = self.update_labels()
        llenar_plantilla(nombre_plantilla, self.ciclo_var, self.mes_var, self.cal, self.tabla, self.root)

    def update_labels(self):
        selected_ciclo = self.ciclo_var.get()
        selected_mes = self.mes_var.get()
        self.ciclo_label.config(text=f"Ciclo seleccionado: {selected_ciclo}")
        self.mes_label.config(text=f"Fecha seleccionada: {selected_mes}")
        return f"Ciclo_{selected_ciclo}_Mes_{selected_mes}"

    def run(self):
        self.root.mainloop()