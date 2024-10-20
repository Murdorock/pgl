from tkinter import messagebox
import tkinter as tk
from src.database.db_config import configurar_base_datos
from datetime import date, datetime

def llenar_plantilla(nombre_plantilla, ciclo_var, mes_var, cal, tabla, root):
    conexion = configurar_base_datos()
    cursor = conexion.cursor()

    try:
        ciclo_seleccionado = ciclo_var.get()
        mes_seleccionado = mes_var.get()
        fecha = cal.get_date()

        crear_tabla_si_no_existe(cursor, nombre_plantilla)
        insertar_datos_correrias(cursor, nombre_plantilla, ciclo_seleccionado)
        actualizar_fecha_y_mes(cursor, nombre_plantilla, fecha, mes_seleccionado, ciclo_seleccionado)
        actualizar_historicos(cursor, nombre_plantilla, ciclo_seleccionado)
        asignar_lectores(cursor, nombre_plantilla, ciclo_seleccionado)
        actualizar_dias_trabajo(cursor, nombre_plantilla)
        actualizar_detalles_personal(cursor, nombre_plantilla)
        actualizar_diferencias_cantidad(cursor, nombre_plantilla)

        # Limpiar la tabla existente
        for item in tabla.get_children():
            tabla.delete(item)

        # Insertar los nuevos datos en la tabla
        cursor.execute(f"SELECT * FROM {nombre_plantilla}")
        resultados = cursor.fetchall()
        for row in resultados:
            tabla.insert("", tk.END, values=row)

        conexion.commit()
        messagebox.showinfo("Éxito", f"'{nombre_plantilla}' programado exitosamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al llenar la plantilla: {str(e)}")
    finally:
        conexion.close()

def crear_tabla_si_no_existe(cursor, nombre_plantilla):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{nombre_plantilla}';")
    if not cursor.fetchone():
        query = f"""
        CREATE TABLE {nombre_plantilla} (
            FECHA VARCHAR(10),
            CICLO VARCHAR,
            MES VARCHAR(10),
            CORRERIA VARCHAR,
            NOMBRE_CORRERIA VARCHAR(10),
            ZONA VARCHAR(10),
            SUPERVISOR VARCHAR(10),
            TRANSPORTE VARCHAR(10),
            GV VARCHAR(10),
            CALI VARCHAR(10),
            TERRENO VARCHAR(10),
            NOMBRE_ZONA VARCHAR(10),
            HIST2 VARCHAR(10),
            HIST1 VARCHAR(10),
            CODIGO VARCHAR(10),
            DIAS VARCHAR,
            TOTALES VARCHAR,
            NOMBRE_LECTOR VARCHAR(10),
            TELEFONO VARCHAR,
            DIFERENCIA VARCHAR(10),
            CEDULA_FUNCIONARIO VARCHAR
        );
        """
        cursor.execute(query)

def insertar_datos_correrias(cursor, nombre_plantilla, ciclo_seleccionado):
    consulta = "SELECT CICLO, ZONA, CORRERIA, NOMBRE_CORRERIA, TRANSPORTE, GV, CALI, TERRENO, NOMBRE_ZONA, SUPERVISOR, CANTIDAD FROM Correrias_Lectura WHERE CICLO = ?"
    cursor.execute(consulta, (ciclo_seleccionado,))
    datos = cursor.fetchall()

    for fila in datos:
        consulta_insercion = f"INSERT INTO {nombre_plantilla} (CICLO, ZONA, CORRERIA, NOMBRE_CORRERIA, TRANSPORTE, GV, CALI, TERRENO, NOMBRE_ZONA, SUPERVISOR, TOTALES) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
        cursor.execute(consulta_insercion, fila)

def actualizar_fecha_y_mes(cursor, nombre_plantilla, fecha, mes_seleccionado, ciclo_seleccionado):
    cursor.execute(f"UPDATE {nombre_plantilla} SET FECHA = ? WHERE CICLO = ?", (fecha, ciclo_seleccionado))
    cursor.execute(f"UPDATE {nombre_plantilla} SET MES = ? WHERE CICLO = ?", (mes_seleccionado, ciclo_seleccionado))

def actualizar_historicos(cursor, nombre_plantilla, ciclo_seleccionado):
    cursor.execute(f"SELECT CORRERIA FROM {nombre_plantilla} WHERE CICLO = ?", (ciclo_seleccionado,))
    resultado = cursor.fetchall()

    for fila in resultado:
        cursor.execute("SELECT CORRERIA, LECTOR FROM Historicos WHERE CORRERIA = ?", (fila[0],))
        sub_resultado = cursor.fetchall()
        if len(sub_resultado) > 1:
            penultimo_dato = sub_resultado[-2]
            correria, lector = penultimo_dato
            cursor.execute(f"UPDATE {nombre_plantilla} SET HIST2 = ? WHERE CORRERIA = ?", (lector, correria))

        if len(sub_resultado) > 0:
            ultimo_dato = sub_resultado[-1]
            correria, lector = ultimo_dato
            cursor.execute(f"UPDATE {nombre_plantilla} SET HIST1 = ? WHERE CORRERIA = ?", (lector, correria))

def asignar_lectores(cursor, nombre_plantilla, ciclo_seleccionado):
    asignar_lectores_bus_carro(cursor, nombre_plantilla, ciclo_seleccionado)
    asignar_lectores_moto(cursor, nombre_plantilla, ciclo_seleccionado)

def asignar_lectores_bus_carro(cursor, nombre_plantilla, ciclo_seleccionado):
    cursor.execute(f"SELECT CORRERIA, SUPERVISOR, TRANSPORTE, CALI FROM {nombre_plantilla} WHERE CICLO = ? AND TRANSPORTE IN ('BUS', 'CARRO', 'A PIE')", (ciclo_seleccionado,))
    correrias = cursor.fetchall()

    cursor.execute(f"SELECT SUPERVISOR, CODIGO, TRANSPORTE FROM zonas WHERE TRANSPORTE IN ('BUS', 'CARRO', 'A PIE')")
    lectores = cursor.fetchall()

    asignar_lectores_a_correrias(cursor, nombre_plantilla, correrias, lectores)

def asignar_lectores_moto(cursor, nombre_plantilla, ciclo_seleccionado):
    cursor.execute(f"SELECT CORRERIA, SUPERVISOR, TRANSPORTE FROM {nombre_plantilla} WHERE CICLO = ? AND GV = 'MOTO'", (ciclo_seleccionado,))
    correrias = cursor.fetchall()

    cursor.execute("SELECT SUPERVISOR, CODIGO, TRANSPORTE FROM zonas WHERE TRANSPORTE = 'MOTO'")
    lectores = cursor.fetchall()

    asignar_lectores_a_correrias(cursor, nombre_plantilla, correrias, lectores)

def asignar_lectores_a_correrias(cursor, nombre_plantilla, correrias, lectores):
    cursor.execute("SELECT CORRERIA, CEDULA, LECTOR FROM HISTORICOS")
    historicos = cursor.fetchall()

    cursor.execute("SELECT CODIGO, NUMERO_CEDULA FROM PERSONAL")
    personal = cursor.fetchall()
    cedula_lector = {lector: cedula for cedula, lector in personal}

    cursor.execute("SELECT * FROM NOVEDADES")
    novedades = set(filter(None, [item for sublist in cursor.fetchall() for item in sublist]))

    cedulas_historicos = {}
    lectores_historicos = {}
    for correria, cedula, lector in historicos:
        if correria not in cedulas_historicos:
            cedulas_historicos[correria] = set()
        if correria not in lectores_historicos:
            lectores_historicos[correria] = set()
        cedulas_historicos[correria].add(cedula)
        lectores_historicos[correria].add(lector)

    lectores_disponibles = list(lectores)
    lectores_asignados = set()

    # Modificamos esta parte para manejar diferentes longitudes de tuplas
    priorizar_correrias = [c for c in correrias if len(c) > 3 and c[3] in ('M', 'RE')]
    otras_correrias = [c for c in correrias if len(c) <= 3 or c[3] not in ('M', 'RE')]

    for correria in priorizar_correrias + otras_correrias:
        correria_id, supervisor, transporte = correria[:3]
        asignado = False

        for lector in lectores:
            supervisor_lector, lector_id, transporte_lector = lector
            cedula = cedula_lector.get(lector_id)
            if (supervisor == supervisor_lector and 
                lector_id not in lectores_asignados and 
                lector_id not in novedades and 
                (correria_id not in cedulas_historicos or cedula not in cedulas_historicos[correria_id]) and 
                (correria_id not in lectores_historicos or lector_id not in lectores_historicos[correria_id])):
                cursor.execute(f"UPDATE {nombre_plantilla} SET CODIGO = ? WHERE CORRERIA = ?", (lector_id, correria_id))
                lectores_asignados.add(lector_id)
                asignado = True
                break
        
        if not asignado:
            for lector in lectores_disponibles:
                supervisor_lector, lector_id, transporte_lector = lector
                cedula = cedula_lector.get(lector_id)
                if (lector_id not in lectores_asignados and 
                    lector_id not in novedades and 
                    (correria_id not in cedulas_historicos or cedula not in cedulas_historicos[correria_id]) and 
                    (correria_id not in lectores_historicos or lector_id not in lectores_historicos[correria_id])):
                    cursor.execute(f"UPDATE {nombre_plantilla} SET CODIGO = ? WHERE CORRERIA = ?", (lector_id, correria_id))
                    lectores_asignados.add(lector_id)
                    lectores_disponibles.remove(lector)
                    break

def actualizar_dias_trabajo(cursor, nombre_plantilla):
    fecha_hoy = date.today()
    cursor.execute("SELECT CODIGO, FECHA FROM PERSONAL")
    personal = cursor.fetchall()

    dias_diferencias = {}
    for lector_id, fecha_ingreso in personal:
        if fecha_ingreso:
            fecha_ingreso = datetime.strptime(fecha_ingreso, '%m/%d/%Y').date()
            dias_diferencia = (fecha_hoy - fecha_ingreso).days
            dias_diferencias[lector_id] = dias_diferencia

    cursor.execute(f"SELECT CODIGO FROM {nombre_plantilla}")
    ciclo = cursor.fetchall()

    for fila in ciclo:
        lector_id = fila[0]
        if lector_id in dias_diferencias:
            dias_diferencia = dias_diferencias[lector_id]
            cursor.execute(f"UPDATE {nombre_plantilla} SET DIAS = ? WHERE CODIGO = ?", (dias_diferencia, lector_id))

def actualizar_detalles_personal(cursor, nombre_plantilla):
    cursor.execute(f"SELECT CODIGO FROM {nombre_plantilla}")
    ciclo = cursor.fetchall()

    cursor.execute("SELECT CODIGO, NOMBRE_COMPLETO, NUMERO_CEDULA, CELULAR_CORPORATIVO FROM PERSONAL")
    personal = cursor.fetchall()

    datos_personal = {codigo: (nombre, cedula, celular) for codigo, nombre, cedula, celular in personal}

    for fila in ciclo:
        lector_id = fila[0]
        if lector_id in datos_personal:
            nombre, cedula, celular = datos_personal[lector_id]
            cursor.execute(f"""
                UPDATE {nombre_plantilla} 
                SET NOMBRE_LECTOR = ?, CEDULA_FUNCIONARIO = ?, TELEFONO = ? 
                WHERE CODIGO = ?
            """, (nombre, cedula, celular, lector_id))

def actualizar_diferencias_cantidad(cursor, nombre_plantilla):
    cursor.execute(f"SELECT CORRERIA FROM {nombre_plantilla}")
    ciclo = cursor.fetchall()

    cursor.execute("SELECT CORRERIA, CANTIDAD, CANTIDAD_MES_ANTERIOR FROM CORRERIAS_LECTURA")
    correrias_lectura = cursor.fetchall()

    diferencias = {}
    for correria, cantidad, cantidad_mes_anterior in correrias_lectura:
        try:
            diferencia = int(cantidad) - int(cantidad_mes_anterior)
            diferencias[correria] = diferencia
        except ValueError:
            continue

    for fila in ciclo:
        correria_id = fila[0]
        if correria_id in diferencias:
            diferencia = diferencias[correria_id]
            cursor.execute(f"UPDATE {nombre_plantilla} SET DIFERENCIA = ? WHERE CORRERIA = ?", (diferencia, correria_id))
