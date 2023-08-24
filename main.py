import tkinter as tk
from conexion import *
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime

# FUNCIONES #
def center_window(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.update_idletasks()
    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"+{x}+{y}")
    
def actualizar():
    entry_fecha.delete(0, tk.END)
    selected_usuario.set("Seleccionar")
    
    combobox_bancos["state"] = "disabled"
    combobox_bancos.set("Seleccionar")
    
    combobox_nro_tarjeta["state"] = "disabled"
    combobox_nro_tarjeta.set("Seleccionar")
    
    combobox_establecimientos.set("Seleccionar")
    
    
    entry_detalle.delete(0, tk.END)
    entry_monto.delete(0, tk.END)
    
    treeview.delete(*treeview.get_children())
    
    reporte_gastos()
    reporte_usuarios()
    reporte_bancos()
    reporte_establecimientos()
    
    consulta = """
        SELECT
            G.ID "ID",
            U.NOMBRE_USUARIO "USUARIO",
            G.FECHA "FECHA",
            E.NOMBRE_EST "ESTABLECIMIENTO",
            G.DETALLE "DETALLE",
            B.NOMBRE_BANCO "BANCO",
            T.NRO_TARJETA "NRO TARJETA",
            T.TIPO "TIPO",
            CASE 
                WHEN CAST(strftime('%d', "FECHA") AS INTEGER) <= T.CIERRE THEN
                    CASE 
                        WHEN CAST(strftime('%m', "FECHA") AS INTEGER) = 12 THEN
                            date(printf('%04d-%02d-%02d', CAST(strftime('%Y', "FECHA") AS INTEGER)+1, CAST(strftime('%m', "FECHA") AS INTEGER)-11, T.VENCIMIENTO))
                    ELSE
                        date(printf('%04d-%02d-%02d', CAST(strftime('%Y', "FECHA") AS INTEGER), CAST(strftime('%m', "FECHA") AS INTEGER)+1, T.VENCIMIENTO))
                    END
            ELSE
                CASE 
                    WHEN CAST(strftime('%d', "FECHA") AS INTEGER) >= T.CIERRE+1 THEN
                        CASE 
                            WHEN CAST(strftime('%m', "FECHA") AS INTEGER) = 12 THEN
                                date(printf('%04d-%02d-%02d', CAST(strftime('%Y', "FECHA") AS INTEGER)+1, CAST(strftime('%m', "FECHA") AS INTEGER)-10, T.VENCIMIENTO))
                        ELSE
                            date(printf('%04d-%02d-%02d', CAST(strftime('%Y', "FECHA") AS INTEGER), CAST(strftime('%m', "FECHA") AS INTEGER)+2, T.VENCIMIENTO))
                        END
                END
            END "FECHA PAGO",
            G.MONTO "MONTO"
        FROM GASTOS G
        JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
        JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
        JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
        JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
        ORDER BY "FECHA" DESC
        """
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(consulta)
            datos = cursor.fetchall()
            cursor.close()
            for fila in datos:
                fila = list(fila)
                fecha_original = fila[2]
                fecha_obj = datetime.strptime(fecha_original, "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d-%m-%y")
                fila[2] = fecha_formateada

                fecha_original = fila[8]
                fecha_obj = datetime.strptime(fecha_original, "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d-%m-%y")
                fila[8] = fecha_formateada

                treeview.insert("", "end", values=fila)
                
            entry_inicio["state"] = "normal"
            entry_inicio.delete(0, "end")
            entry_inicio.insert(0, "01-01-2000")
            entry_inicio["state"] = "disable"

            entry_cierre["state"] = "normal"
            entry_cierre.delete(0, "end")
            entry_cierre.insert(0, "01-01-2000")
            entry_cierre["state"] = "disable"

            entry_pago["state"] = "normal"
            entry_pago.delete(0, "end")
            entry_pago.insert(0, "01-01-2000")
            entry_pago["state"] = "disable"
            
            entry_total["state"] = "normal"
            entry_total.delete(0, "end")
            entry_total.insert(0, "0.0")
            entry_total["state"] = "disable"
            
            entry_promedio["state"] = "normal"
            entry_promedio.delete(0, "end")
            entry_promedio.insert(0, "0.0")
            entry_promedio["state"] = "disable"
            
        except Exception as ex:
            print("Error al ejecutar la consulta:", ex)
            
def switch_callback():
    global treeview
    if switch.instate(["selected"]):
        style.theme_use("forest-dark")
        root.configure(bg = "#313131")
        if treeview:
            treeview.destroy()
        tree()
        actualizar()
    else:
        style.theme_use("forest-light")
        root.configure(bg = "#ffffff")
        if treeview:
            treeview.destroy()
        tree()
        actualizar()
        
def obtener_fecha(event):
    fecha_seleccionada = entry_fecha.get_date()
    entry_fecha["state"] = "readonly"
    entry_fecha.delete(0, "end")
    entry_fecha.insert("end", fecha_seleccionada)
    entry_fecha["state"] = "readonly"

def generar_id_gasto():
    consulta = """ SELECT MAX(ID) FROM GASTOS"""
    result = ejecutar_query(conectar_bd(), consulta)
    if result[0][0] is None:
        return 1
    else:
        return result[0][0] + 1
    
def generar_id_usuario():
    consulta = """ SELECT MAX(USUARIO) FROM USUARIOS"""
    result = ejecutar_query(conectar_bd(), consulta)
    if result[0][0] is None:
        return 1
    else:
        return result[0][0] + 1
    
def generar_id_banco():
    consulta = """ SELECT MAX(BANCO) FROM BANCOS"""
    result = ejecutar_query(conectar_bd(), consulta)
    if result[0][0] is None:
        return 1
    else:
        return result[0][0] + 1
    
def generar_id_establecimiento():
    consulta = """ SELECT MAX(ESTABLECIMIENTO) FROM ESTABLECIMIENTOS"""
    result = ejecutar_query(conectar_bd(), consulta)
    if result[0][0] is None:
        return 1
    else:
        return result[0][0] + 1
    
def obtener_usuario_id():
    usuario = combobox_usuarios.get()
    consulta = """
        SELECT 
            USUARIO
        FROM USUARIOS
        WHERE NOMBRE_USUARIO = :usuario
        """
    parametros = {"usuario": usuario}
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(consulta, parametros)
            result = cursor.fetchall()
            cursor.close()
            return result[0][0]

        except Exception as ex:
            print("Error al ejecutar la consulta:", ex)
            
def obtener_establecimiento_id():
    establecimiento = combobox_establecimientos.get()
    consulta = """
        SELECT 
            ESTABLECIMIENTO
        FROM ESTABLECIMIENTOS
        WHERE NOMBRE_EST = :establecimiento
        """
    parametros = {"establecimiento": establecimiento}
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(consulta, parametros)
            result = cursor.fetchall()
            cursor.close()
            return result[0][0]

        except Exception as ex:
            print("Error al ejecutar la consulta:", ex)
            
def registrar_gasto():
    usuario = combobox_usuarios.get()
    establecimiento = combobox_establecimientos.get()
    detalle = str(entry_detalle.get())
    monto = entry_monto.get()
    tarjetas_nro_tarjeta = str(combobox_nro_tarjeta.get())
    banco = combobox_bancos.get()
    
    fecha = entry_fecha.get()
    if usuario == "Seleccionar" or establecimiento == "Seleccionar" or monto == "" or tarjetas_nro_tarjeta == "Seleccionar" or banco == "Seleccionar":
        messagebox.showwarning("Error de registro", "ERROR: FALTAN COMPLETAR ESPACIOS OBLIGATORIOS.")
        return
    elif float(monto) <= 0:
        messagebox.showwarning("Error de registro", "ERROR: El monto debe ser mayor a  0.0.")
        return
    
    else:
        id = generar_id_gasto()
        usuarios_usuario = obtener_usuario_id()
        establecimientos_establecimiento = obtener_establecimiento_id()
        monto = float(entry_monto.get())
        fecha_obj = datetime.strptime(fecha, "%d-%m-%Y")
        fecha_formateada = fecha_obj.strftime("%Y-%m-%d")
    
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    INSERT INTO gastos (
                        id,
                        fecha,
                        detalle,
                        monto,
                        usuarios_usuario,
                        tarjetas_nro_tarjeta,
                        establecimientos_establecimiento) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, 
                    (
                        id, 
                        fecha_formateada, 
                        detalle, 
                        monto, 
                        usuarios_usuario, 
                        tarjetas_nro_tarjeta,
                        establecimientos_establecimiento
                    )
                )
                conexion.commit()
                cursor.close()
                cerrar_bd(conexion)
                messagebox.showinfo("Datos Registrados", "El gasto se registro correctamente.")
                actualizar()

            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al insertar datos: " + str(ex))
                
def seleccion(event):
    seleccion = treeview.selection()
    combobox_bancos["state"] = "disabled"
    combobox_nro_tarjeta["state"] = "disabled"

    if seleccion:
        item = seleccion[0]
        gasto = treeview.item(item, "values")

        selected_usuario
        if gasto[1] in combobox_usuarios["values"]:
            selected_usuario.set(gasto[1])
            index = combobox_usuarios["values"].index(gasto[1])
            combobox_usuarios.current(index)
        
        fecha_original = gasto[2]
        fecha_obj = datetime.strptime(fecha_original, "%d-%m-%y")
        fecha_formateada = fecha_obj.strftime("%d-%m-%Y")
        
        entry_fecha.set_date(fecha_formateada)
        
        selected_establecimiento.set(gasto[3])
        entry_detalle.delete(0, tk.END)
        entry_detalle.insert(0, gasto[4])
        selected_banco.set(gasto[5])
        selected_nro_tarjeta.set(gasto[6])
        entry_monto.delete(0, tk.END)
        entry_monto.insert(0, gasto[9])
        
def editar_gasto():
    seleccion = treeview.selection()
    if len(seleccion) == 0:
        messagebox.showwarning("Sin Selección", "ERROR: SE DEBE SELECCIONAR UNA FILA.")
        return
    respuesta = messagebox.askyesno("Confirmar Edición", "Vas a modificar un gasto. ¿Deseas continuar?")
    if respuesta:
        editar_gasto_seleccionado(seleccion)
        
def editar_gasto_seleccionado(seleccion):
    item_values = treeview.item(seleccion, "values")
    id = item_values[0]
    fecha = entry_fecha.get()
    fecha_obj = datetime.strptime(fecha, "%d-%m-%Y")
    fecha_formateada = fecha_obj.strftime("%Y-%m-%d")
    
    detalle = str(entry_detalle.get())
    monto = float(entry_monto.get())
    usuarios_usuario = obtener_usuario_id()
    tarjetas_nro_tarjeta = str(selected_nro_tarjeta.get())
    establecimientos_establecimiento = obtener_establecimiento_id()
    
    if str(monto) == "" or tarjetas_nro_tarjeta == "Seleccionar" :
        messagebox.showwarning("Error de registro", "ERROR: FALTAN COMPLETAR ESPACIOS OBLIGATORIOS.")
        return
    elif monto <= 0:
        messagebox.showwarning("Error de registro", "ERROR: El monto debe ser mayor a  0.0.")
        return
    
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                UPDATE gastos
                SET 
                    fecha = ?,
                    detalle = ?,
                    monto = ?,
                    usuarios_usuario = ?,
                    tarjetas_nro_tarjeta = ?,
                    establecimientos_establecimiento = ?
                WHERE id = ?
                """,
                (
                    fecha_formateada, 
                    detalle, monto, 
                    usuarios_usuario, 
                    tarjetas_nro_tarjeta, 
                    establecimientos_establecimiento, 
                    id
                )
            )
            conexion.commit()
            cursor.close()
            cerrar_bd(conexion)
            messagebox.showinfo("Cambios Guardados", "La fila seleccionada modificó correctamente.",)
            actualizar()

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al modificar gasto: " + str(ex))
            
def eliminar_gasto():
    seleccion = treeview.selection()
    if len(seleccion) == 0:
        messagebox.showwarning("Sin selección", "ERROR: SE DEBE SELECCIONAR UNA FILA.")
        return
    respuesta = messagebox.askyesno("Confirmar Eliminación", "Vas a eliminar un gasto. ¿Deseas continuar?")
    if respuesta:
        eliminar_gasto_seleccionado(seleccion)
        
def eliminar_gasto_seleccionado(seleccion):
    item_values = treeview.item(seleccion, "values")
    id = item_values[0]

    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM gastos WHERE id = ?", (id,))
            conexion.commit()
            cursor.close()
            cerrar_bd(conexion)

            treeview.delete(seleccion)
            messagebox.showinfo("Eliminación Confirmada", "La fila seleccionada se eliminó correctamente.",)
            actualizar()

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al eliminar gasto: " + str(ex))
            
def filtrar_datos():
    selected_usuario_filtro = combobox_usuarios_filtro.get()
    selected_banco_filtro = combobox_bancos_filtro.get()
    selected_nro_tarjeta_filtro = combobox_nro_tarjeta_filtro.get()
        
    if selected_usuario_filtro == "Seleccionar" or selected_banco_filtro == "Seleccionar" or selected_nro_tarjeta_filtro == "Seleccionar":
        messagebox.showwarning("Error de registro", "ERROR: FALTAN DATOS DE FILTRO.")
        return
    else:
        treeview.delete(*treeview.get_children())
        dia = int(entry_dia.get())
        mes = int(combobox_mes.get())
        año = int(combobox_año.get())

        # Calcular la fecha de inicio (dos meses atrás)
        mes_inicio = mes - 2
        año_inicio = año
        if mes_inicio <= 0:
            mes_inicio += 12
            año_inicio -= 1

        # Calcular la fecha de fin (mes siguiente)
        mes_cierre = mes - 1
        año_cierre = año
        if mes_cierre == 0:
            mes_cierre += 12
            año_cierre -= 1
            
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    SELECT
                        G.ID "ID",
                        U.NOMBRE_USUARIO "USUARIO",
                        G.FECHA "FECHA",
                        E.NOMBRE_EST "ESTABLECIMIENTO",
                        G.DETALLE "DETALLE",
                        B.NOMBRE_BANCO "BANCO",
                        T.NRO_TARJETA "NRO TARJETA",
                        T.TIPO "TIPO",
                        CASE 
                            WHEN CAST(strftime('%d', "FECHA") AS INTEGER) <= T.CIERRE THEN
                                CASE 
                                    WHEN CAST(strftime('%m', "FECHA") AS INTEGER) = 12 THEN
                                        date(printf('%04d-%02d-%02d', CAST(strftime('%Y', "FECHA") AS INTEGER)+1, CAST(strftime('%m', "FECHA") AS INTEGER)-11, T.VENCIMIENTO))
                                ELSE
                                    date(printf('%04d-%02d-%02d', CAST(strftime('%Y', "FECHA") AS INTEGER), CAST(strftime('%m', "FECHA") AS INTEGER)+1, T.VENCIMIENTO))
                                END
                        ELSE
                            CASE 
                                WHEN CAST(strftime('%d', "FECHA") AS INTEGER) >= T.CIERRE+1 THEN
                                    CASE 
                                        WHEN CAST(strftime('%m', "FECHA") AS INTEGER) = 12 THEN
                                            date(printf('%04d-%02d-%02d', CAST(strftime('%Y', "FECHA") AS INTEGER)+1, CAST(strftime('%m', "FECHA") AS INTEGER)-10, T.VENCIMIENTO))
                                    ELSE
                                        date(printf('%04d-%02d-%02d', CAST(strftime('%Y', "FECHA") AS INTEGER), CAST(strftime('%m', "FECHA") AS INTEGER)+2, T.VENCIMIENTO))
                                    END
                            END
                        END "FECHA PAGO",
                        G.MONTO "MONTO"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
                    JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                    JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                    WHERE U.NOMBRE_USUARIO = :selected_usuario_filtro AND B.NOMBRE_BANCO = :selected_banco_filtro AND T.NRO_TARJETA = :selected_nro_tarjeta_filtro AND "FECHA" >= date(printf('%04d-%02d-%02d', :año_inicio, :mes_inicio, T.CIERRE+1)) AND "FECHA" <= date(printf('%04d-%02d-%02d', :año_cierre, :mes_cierre, T.CIERRE))
                    ORDER BY "FECHA" DESC
                    """,
                    (
                        selected_usuario_filtro,
                        selected_banco_filtro,
                        selected_nro_tarjeta_filtro,
                        año_inicio,
                        mes_inicio,
                        año_cierre,
                        mes_cierre
                    ),
                )
                datos = cursor.fetchall()
                cursor.close()
                
                total = 0
                for fila in datos:
                    fila = list(fila)
                    fecha_original = fila[2]
                    fecha_obj = datetime.strptime(fecha_original, "%Y-%m-%d")
                    fecha_formateada = fecha_obj.strftime("%d-%m-%y")
                    fila[2] = fecha_formateada

                    fecha_original = fila[8]
                    fecha_obj = datetime.strptime(fecha_original, "%Y-%m-%d")
                    fecha_formateada = fecha_obj.strftime("%d-%m-%y")
                    fila[8] = fecha_formateada
                    
                    total += fila[9]

                    treeview.insert("", "end", values=fila)
                    
            except Exception as ex:
                print("Error al ejecutar la consulta:", ex)
    
        ### Promedio ###
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()  
                cursor.execute(
                    """
                    SELECT
                        T.CIERRE,
                        CASE 
                            WHEN CAST(strftime('%d', G.fecha) AS INTEGER) <= T.CIERRE THEN
                                CASE 
                                    WHEN CAST(strftime('%m', G.fecha) AS INTEGER) = 12 THEN
                                        date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER)+1, CAST(strftime('%m', G.fecha) AS INTEGER)-11, T.VENCIMIENTO))
                                ELSE
                                    date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER), CAST(strftime('%m', G.fecha) AS INTEGER)+1, T.VENCIMIENTO))
                                END
                        ELSE
                            CASE 
                                WHEN CAST(strftime('%d', G.fecha) AS INTEGER) >= T.CIERRE+1 THEN
                                    CASE 
                                        WHEN CAST(strftime('%m', G.fecha) AS INTEGER) = 12 THEN
                                            date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER)+1, CAST(strftime('%m', G.fecha) AS INTEGER)-10, T.VENCIMIENTO))
                                    ELSE
                                        date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER), CAST(strftime('%m', G.fecha) AS INTEGER)+2, T.VENCIMIENTO))
                                    END
                            END
                        END "FECHA PAGO",
                        SUM(G.MONTO)
                    FROM GASTOS G
                    JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                    WHERE U.NOMBRE_USUARIO = :selected_usuario_filtro AND B.NOMBRE_BANCO = :selected_banco_filtro AND T.NRO_TARJETA = :selected_nro_tarjeta_filtro
                    GROUP BY "FECHA PAGO"
                    ORDER BY "FECHA PAGO" DESC
                    """,
                    (
                        selected_usuario_filtro, 
                        selected_banco_filtro, 
                        selected_nro_tarjeta_filtro
                    ),
                )
                datos_1 = cursor.fetchall()
                cursor.close()
                suma_total = 0
                cantidad = 0
                for fila in datos_1:
                    suma_total += fila[2]
                    cantidad += 1
                promedio = suma_total/cantidad
                
            except Exception as ex:
                print("Error al ejecutar la consulta:", ex)
        
        if datos == []:
            pass
        else:
            dia_inicio = datos_1[0][0]+1
            dia_cierre = datos_1[0][0]
            
            fecha_inicio = datetime(año_inicio, mes_inicio, dia_inicio).strftime('%d-%m-%Y')
            fecha_cierre = datetime(año_cierre, mes_cierre, dia_cierre).strftime('%d-%m-%Y')
            
            entry_inicio["state"] = "normal"
            entry_inicio.delete(0, "end")
            entry_inicio.insert(0, fecha_inicio)
            entry_inicio["state"] = "readonly"
            
            entry_cierre["state"] = "normal"
            entry_cierre.delete(0, "end")
            entry_cierre.insert(0, fecha_cierre)
            entry_cierre["state"] = "readonly"
            
            fecha_pago = datetime(año, mes, dia).strftime('%d-%m-%Y')
            entry_pago["state"] = "normal"
            entry_pago.delete(0, "end")
            entry_pago.insert(0, fecha_pago)
            entry_pago["state"] = "readonly"
            
            entry_total["state"] = "normal"
            entry_total.delete(0, "end")
            entry_total.insert(0, "S/. " + str(round(total, 2)))
            entry_total["state"] = "readonly"
            
            entry_promedio["state"] = "normal"
            entry_promedio.delete(0, "end")
            entry_promedio.insert(0, "S/. " + str(round(promedio, 2)))
            entry_promedio["state"] = "readonly"
          
            
root = tk.Tk()
style = ttk.Style(root)
root.title("GESTIÓN DE GASTOS")
#root.resizable(0, 0)

# IMPORTAR TCL
root.tk.call("source", "themes/forest-dark.tcl")
root.tk.call("source", "themes/forest-light.tcl")
style.theme_use("forest-light")

# FRAMES #
frame = ttk.Frame(root)
frame.pack()

# FRAME DATOS #
frames_datos = ttk.LabelFrame(frame, text="Datos")
frames_datos.grid(row=0, column=0, columnspan=3, padx=(5, 5), pady=(0, 0), sticky="nsew")

frames_datos.grid_rowconfigure(2, minsize=30)
frames_datos.grid_rowconfigure(5, minsize=15)
frames_datos.grid_columnconfigure(0, minsize=200)
frames_datos.grid_columnconfigure(1, minsize=200)
frames_datos.grid_columnconfigure(2, minsize=200)
frames_datos.grid_columnconfigure(3, minsize=120)

label_fecha = ttk.Label(frames_datos, text="Fecha:")
label_fecha.grid(row=0, column=0, padx=(15, 0), sticky="w")
entry_fecha = DateEntry(frames_datos, date_pattern="dd-mm-yyyy", width=20)
entry_fecha.grid(row=1, column=0, padx=(15, 0), sticky="w")
entry_fecha["state"] = "readonly"
entry_fecha.delete(0, "end")
entry_fecha.bind("<<DateEntrySelected>>", obtener_fecha)

label_usuario = ttk.Label(frames_datos, text="Usuario:")
label_usuario.grid(row=0, column=1, padx=(15, 0), sticky="w")
selected_usuario = tk.StringVar(frames_datos)
selected_usuario.set("Seleccionar")
combobox_usuarios = ttk.Combobox(
    frames_datos,
    textvariable=selected_usuario,
    state="readonly",
    width=20,
)
combobox_usuarios.grid(row=1, column=1, padx=(15, 0), sticky="w")

label_banco = ttk.Label(frames_datos, text="Banco:")
label_banco.grid(row=0, column=2, padx=(15, 0), sticky="w")
selected_banco = tk.StringVar(frames_datos)
selected_banco.set("Seleccionar")
combobox_bancos = ttk.Combobox(
    frames_datos,
    textvariable=selected_banco,
    state="disabled",
    width=20,
)
combobox_bancos.grid(row=1, column=2, padx=(15, 0), sticky="w")

label_nro_tarjeta = ttk.Label(frames_datos, text="Nro. Tarjeta:")
label_nro_tarjeta.grid(row=0, column=3, padx=(15, 0), sticky="w")
selected_nro_tarjeta = tk.StringVar(frames_datos)
selected_nro_tarjeta.set("Seleccionar")
combobox_nro_tarjeta = ttk.Combobox(
    frames_datos,
    textvariable=selected_nro_tarjeta,
    state="disabled",
    width=8,
)
combobox_nro_tarjeta.grid(row=1, column=3, padx=(15, 0), sticky="w")

def actualizar_usuarios():
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT 
                    USUARIO
                ,NOMBRE_USUARIO 
                FROM USUARIOS
                """
            )
            nombres_usuarios = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)

            opciones_usuarios = [nombre[1] for nombre in nombres_usuarios]
            combobox_usuarios["values"] = opciones_usuarios
            combobox_usuarios.set("Seleccionar")

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
actualizar_usuarios()

def actualizar_bancos(event):
    selected_usuario = combobox_usuarios.get()

    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT 
                    B.BANCO
                    ,B.NOMBRE_BANCO
                FROM BANCOS B
                JOIN TARJETAS T ON T.BANCOS_BANCO = B.BANCO
                JOIN USUARIOS U ON U.USUARIO = T.USUARIOS_USUARIO
                WHERE U.NOMBRE_USUARIO = :nombre
                GROUP BY B.BANCO
                """,
                (selected_usuario,),
            )
            nombres_bancos = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)

            opciones_bancos = [nombre[1] for nombre in nombres_bancos]
            combobox_bancos["values"] = opciones_bancos
            combobox_bancos.set("Seleccionar")
            combobox_nro_tarjeta.set("Seleccionar")

            if selected_usuario:
                combobox_bancos["state"] = "readonly"
                combobox_bancos.set("Seleccionar")
                combobox_nro_tarjeta["state"] = "disabled"
                combobox_nro_tarjeta.set("Seleccionar")
            else:
                combobox_bancos["state"] = "disabled"
                combobox_bancos.set("Seleccionar")

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
            
def actualizar_nros_tarjeta(event):
    selected_usuario = combobox_usuarios.get()
    selected_banco = combobox_bancos.get()

    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT 
                    B.BANCO
                    ,T.NRO_TARJETA
                FROM BANCOS B
                JOIN TARJETAS T ON T.BANCOS_BANCO = B.BANCO
                JOIN USUARIOS U ON U.USUARIO = T.USUARIOS_USUARIO
                WHERE U.NOMBRE_USUARIO = :nombre AND B.NOMBRE_BANCO = :banco
                """,
                (
                    selected_usuario,
                    selected_banco,
                ),
            )
            nro_tarjeta = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)

            opciones_nro_tarjeta = [nombre[1] for nombre in nro_tarjeta]
            combobox_nro_tarjeta["values"] = opciones_nro_tarjeta
            combobox_nro_tarjeta.set("Seleccionar")

            if selected_banco and selected_usuario:
                combobox_nro_tarjeta["state"] = "readonly"
                combobox_nro_tarjeta.set("Seleccionar")
            else:
                combobox_nro_tarjeta["state"] = "disabled"
                combobox_nro_tarjeta.set("Seleccionar")

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
            
# Asociar las funciones a los eventos de cambio en los combobox
combobox_usuarios.bind("<<ComboboxSelected>>", actualizar_bancos)
combobox_bancos.bind("<<ComboboxSelected>>", actualizar_nros_tarjeta)

label_establecimiento = ttk.Label(frames_datos, text="Establecimiento:")
label_establecimiento.grid(row=2, column=0, padx=(15, 0), pady=(15, 0), sticky="w")
selected_establecimiento = tk.StringVar(frames_datos)
selected_establecimiento.set("Seleccionar")
combobox_establecimientos = ttk.Combobox(
    frames_datos,
    textvariable=selected_establecimiento,
    state="readonly",
    width=20,
)
combobox_establecimientos.grid(row=3, column=0, padx=(15, 0), sticky="w")

def actualizar_establecimientos():
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT 
                    ESTABLECIMIENTO
                    ,NOMBRE_EST
                FROM ESTABLECIMIENTOS
                """
            )
            nombres_establecimientos = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)

            opciones_establecimientos = [nombre[1] for nombre in nombres_establecimientos]
            combobox_establecimientos["values"] = opciones_establecimientos
            combobox_establecimientos.set("Seleccionar")

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
actualizar_establecimientos()

label_detalle = ttk.Label(frames_datos, text="Detalle:")
label_detalle.grid(row=2, column=1, columnspan=2, padx=(15, 0), pady=(15, 0), sticky="w")
entry_detalle = ttk.Entry(frames_datos, width=52)
entry_detalle.grid(row=3, column=1, columnspan=2, padx=(15, 0), sticky="w")

label_monto = ttk.Label(frames_datos, text="Monto:")
label_monto.grid(row=2, column=3, padx=(15, 0), pady=(15, 0), sticky="w")
entry_monto = ttk.Entry(frames_datos, width=11)
entry_monto.grid(row=3, column=3, padx=(15, 0), sticky="w")

separador = ttk.Separator(frames_datos)
separador.grid(row=0, column=4, rowspan=6, padx=(10, 10), pady=(0, 10), sticky="nsew")

boton_registrar = ttk.Button(frames_datos, text="Registrar Gasto", width=20, command=registrar_gasto)
boton_registrar.grid(row=1, column=5, columnspan=2, padx=(15, 15), pady=(0, 0), sticky="nw")

boton_editar = ttk.Button(frames_datos, text="Editar", width=8, command=editar_gasto)
boton_editar.grid(row=3, column=5, padx=(15, 0), pady=(0, 0), sticky="nw")

boton_eliminar = ttk.Button(frames_datos, text="Eliminar", width=8, command=eliminar_gasto)
boton_eliminar.grid(row=3, column=6, padx=(5, 15), pady=(0, 0), sticky="nw")

# FRAME TABLA #
def tree():
    frame_tabla = ttk.Frame(frame)
    frame_tabla.grid(
        row=1, column=0, columnspan=2, padx=(5, 0), pady=(8, 0), sticky="nsew"
    )
    scroll_tabla = ttk.Scrollbar(frame_tabla)
    scroll_tabla.pack(side="right", fill="y")
    encabezados = (
        "Id",
        "Usuario",
        "Fecha",
        "Lugar",
        "Detalle",
        "Banco",
        "Nro",
        "Tipo",
        "Fecha Pago",
        "Monto",
    )
    global treeview
    treeview = ttk.Treeview(
        frame_tabla,
        show="headings",
        yscrollcommand=scroll_tabla.set,
        columns=encabezados,
        height=13,
    )
    treeview.column("Id", width=5)
    treeview.column("Usuario", width=40)
    treeview.column("Fecha", width=65)
    treeview.column("Lugar", width=90)
    treeview.column("Detalle", width=130)
    treeview.column("Banco", width=110)
    treeview.column("Nro", width=35)
    treeview.column("Tipo", width=60)
    treeview.column("Fecha Pago", width=65)
    treeview.column("Monto", width=55)

    for encabezado in encabezados:
        treeview.heading(encabezado, text=encabezado)

    treeview.pack()
    treeview.configure()
    scroll_tabla.configure(command=treeview.yview)
    treeview.bind("<ButtonRelease-1>", seleccion)
tree()

# FRAME FILTROS #
frame_filtros = ttk.LabelFrame(frame, text="Filtrar datos")
frame_filtros.grid(row=1, column=2, padx=(5, 5), pady=(0, 0), sticky="nsew")

label_usuario_filtro = ttk.Label(frame_filtros, text="Usuario:")
label_usuario_filtro.grid(row=0, column=0, columnspan=3, padx=(15, 0), pady=(5, 0), sticky="w")
selected_usuario_filtro = tk.StringVar(frame_filtros)
selected_usuario_filtro.set("Seleccionar")
combobox_usuarios_filtro = ttk.Combobox(
    frame_filtros,
    textvariable=selected_usuario_filtro,
    state="readonly",
    width=18,
)
combobox_usuarios_filtro.grid(row=1, column=0, columnspan=3, padx=(15, 15), pady=(0, 0), sticky="w")

label_banco_filtro = ttk.Label(frame_filtros, text="Banco:")
label_banco_filtro.grid(row=2, column=0, columnspan=3, padx=(15, 0), pady=(12, 0), sticky="w")
selected_banco_filtro = tk.StringVar(frame_filtros)
selected_banco_filtro.set("Seleccionar")
combobox_bancos_filtro = ttk.Combobox(
    frame_filtros,
    textvariable=selected_banco_filtro,
    state="disabled",
    width=18,
)
combobox_bancos_filtro.grid(row=3, column=0, columnspan=3, padx=(15, 15), sticky="w")
        
label_nro_tarjeta_filtro = ttk.Label(frame_filtros, text="Nro. Tarjeta:")
label_nro_tarjeta_filtro.grid(row=4, column=0, columnspan=3, padx=(15, 0), pady=(12, 0), sticky="w")

selected_nro_tarjeta_filtro = tk.StringVar(frame_filtros)
selected_nro_tarjeta_filtro.set("Seleccionar")
combobox_nro_tarjeta_filtro = ttk.Combobox(
    frame_filtros,
    textvariable=selected_nro_tarjeta_filtro,
    state="disabled",
    width=18,
)
combobox_nro_tarjeta_filtro.grid(row=5, column=0, columnspan=3, padx=(15, 15), pady=(0, 12), sticky="w")

def actualizar_usuarios_filtro():
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT 
                    USUARIO
                    ,NOMBRE_USUARIO 
                FROM USUARIOS
                """
            )
            nombres_usuarios = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)

            opciones_usuarios = [nombre[1] for nombre in nombres_usuarios]
            combobox_usuarios_filtro["values"] = opciones_usuarios
            combobox_usuarios_filtro.set("Seleccionar")

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
actualizar_usuarios_filtro()

def actualizar_bancos_filtro(event):
    selected_usuario_filtro = combobox_usuarios_filtro.get()

    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT 
                    B.BANCO
                    ,B.NOMBRE_BANCO
                FROM BANCOS B
                JOIN TARJETAS T ON T.BANCOS_BANCO = B.BANCO
                JOIN USUARIOS U ON U.USUARIO = T.USUARIOS_USUARIO
                WHERE U.NOMBRE_USUARIO = :nombre
                GROUP BY B.BANCO
                """,
                (selected_usuario_filtro,),
            )
            nombres_bancos = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)

            opciones_bancos = [nombre[1] for nombre in nombres_bancos]
            combobox_bancos_filtro["values"] = opciones_bancos
            combobox_bancos_filtro.set("Seleccionar")
            combobox_nro_tarjeta_filtro.set("Seleccionar")
            
            entry_dia["state"] = "normal"
            entry_dia.delete(0, "end")
            entry_dia.insert(0, "01")
            entry_dia["state"] = "disabled"

            combobox_mes["state"] = "normal"
            combobox_mes.delete(0, "end")
            combobox_mes.insert(0, "01")
            combobox_mes["state"] = "disabled"

            combobox_año["state"] = "normal"
            combobox_año.delete(0, "end")
            combobox_año.insert(0, "2000")
            combobox_año["state"] = "disabled"

            if selected_usuario_filtro:
                combobox_bancos_filtro["state"] = "readonly"
                combobox_bancos_filtro.set("Seleccionar")
                combobox_nro_tarjeta_filtro["state"] = "disabled"
                combobox_nro_tarjeta_filtro.set("Seleccionar")
            else:
                combobox_bancos_filtro["state"] = "disabled"
                combobox_bancos_filtro.set("Seleccionar")

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
            
def actualizar_nros_tarjeta_filtro(event):
    selected_usuario_filtro = combobox_usuarios_filtro.get()
    selected_banco_filtro = combobox_bancos_filtro.get()

    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT 
                    B.BANCO
                    ,T.NRO_TARJETA
                FROM BANCOS B
                JOIN TARJETAS T ON T.BANCOS_BANCO = B.BANCO
                JOIN USUARIOS U ON U.USUARIO = T.USUARIOS_USUARIO
                WHERE U.NOMBRE_USUARIO = :nombre AND B.NOMBRE_BANCO = :banco
                """,
                (
                    selected_usuario_filtro,
                    selected_banco_filtro,
                ),
            )
            nro_tarjeta = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)

            opciones_nro_tarjeta = [nombre[1] for nombre in nro_tarjeta]
            combobox_nro_tarjeta_filtro["values"] = opciones_nro_tarjeta
            combobox_nro_tarjeta_filtro.set("Seleccionar")
            
            entry_dia["state"] = "normal"
            entry_dia.delete(0, "end")
            entry_dia.insert(0, "01")
            entry_dia["state"] = "disabled"

            combobox_mes["state"] = "normal"
            combobox_mes.delete(0, "end")
            combobox_mes.insert(0, "01")
            combobox_mes["state"] = "disabled"

            combobox_año["state"] = "normal"
            combobox_año.delete(0, "end")
            combobox_año.insert(0, "2000")
            combobox_año["state"] = "disabled"

            if selected_banco_filtro and selected_usuario_filtro:
                combobox_nro_tarjeta_filtro["state"] = "readonly"
                combobox_nro_tarjeta_filtro.set("Seleccionar")
            else:
                combobox_nro_tarjeta_filtro["state"] = "disabled"
                combobox_nro_tarjeta_filtro.set("Seleccionar")

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
            
def actualizar_dia_filtro(event):
    selected_usuario_filtro = combobox_usuarios_filtro.get()
    selected_banco_filtro = combobox_bancos_filtro.get()
    selected_nro_tarjeta_filtro = combobox_nro_tarjeta_filtro.get()

    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT 
                    SUBSTR(('00' || CAST(T.VENCIMIENTO AS TEXT)), -2),
                    T.CIERRE
                FROM BANCOS B
                JOIN TARJETAS T ON T.BANCOS_BANCO = B.BANCO
                JOIN USUARIOS U ON U.USUARIO = T.USUARIOS_USUARIO
                WHERE U.NOMBRE_USUARIO = :nombre  AND B.NOMBRE_BANCO = :banco  AND T.NRO_TARJETA = :nro_tarjeta
                """,
                (
                    selected_usuario_filtro,
                    selected_banco_filtro,
                    selected_nro_tarjeta_filtro,
                ),
            )
            vencimiento = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)

            if (selected_banco_filtro and selected_usuario_filtro and selected_nro_tarjeta_filtro):
                entry_dia["state"] = "normal"
                entry_dia.delete(0, "end")
                entry_dia.insert(0, vencimiento[0][0])
                entry_dia["state"] = "readonly"

                combobox_mes["state"] = "readonly"
                combobox_año["state"] = "readonly"

            conexion = conectar_bd()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    nombre_usuario = combobox_usuarios_filtro.get()
                    nombre_banco = combobox_bancos_filtro.get()
                    nro_tarjeta = combobox_nro_tarjeta_filtro.get()

                    cursor.execute(
                        """
                        SELECT
                            CAST(strftime('%Y', G.fecha) AS INTEGER)
                        FROM GASTOS G
                        JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                        JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                        JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                        WHERE U.NOMBRE_USUARIO = :nombre_usuario AND B.NOMBRE_BANCO = :nombre_banco  AND T.NRO_TARJETA = :nro_tarjeta
                        GROUP BY CAST(strftime('%Y', G.fecha) AS INTEGER)
                        ORDER BY CAST(strftime('%Y', G.fecha) AS INTEGER) DESC
                        """,
                        (
                            nombre_usuario, 
                            nombre_banco, 
                            nro_tarjeta
                        ),
                    )
                    años = cursor.fetchall()
                    cursor.close()
                    cerrar_bd(conexion)

                    opciones_años = [año[0] for año in años]
                    combobox_año["values"] = opciones_años
                    combobox_año.set(opciones_años[0])

                except Exception as ex:
                    cerrar_bd(conexion)
                    messagebox.showerror("Error", "Error al obtener datos: " + str(ex))

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
            
# Asociar las funciones a los eventos de cambio en los combobox
combobox_usuarios_filtro.bind("<<ComboboxSelected>>", actualizar_bancos_filtro)
combobox_bancos_filtro.bind("<<ComboboxSelected>>", actualizar_nros_tarjeta_filtro)
combobox_nro_tarjeta_filtro.bind("<<ComboboxSelected>>", actualizar_dia_filtro)

label_dia = ttk.Label(frame_filtros, text="Día:")
label_dia.grid(row=6, column=0, padx=(15, 0), pady=(5, 0), sticky="nsew")

label_mes = ttk.Label(frame_filtros, text="Mes:")
label_mes.grid(row=6, column=1, padx=(15, 0), pady=(5, 0), sticky="nsew")

label_año = ttk.Label(frame_filtros, text="Año:")
label_año.grid(row=6, column=2, padx=(15, 0), pady=(5, 0), sticky="nsew")

entry_dia = ttk.Entry(frame_filtros, state="normal", width=1)
entry_dia.grid(row=7, column=0, padx=(15, 0), pady=(5, 15), sticky="nsew")
entry_dia.insert(0, "01")
entry_dia["state"] = "disabled"

def selected_mes(event):
    selected_value = combobox_mes.get().split("-")[0]
    combobox_mes.set(selected_value.zfill(2))
    
combobox_mes = ttk.Combobox(
    frame_filtros,
    values=[
        "01-ENE",
        "02-FEB",
        "03-MAR",
        "04-ABR",
        "05-MAY",
        "06-JUN",
        "07-JUL",
        "08-AGO",
        "09-SEP",
        "10-OCT",
        "11-NOV",
        "12-DIC",
    ],
    state="normal",
    width=1,
)
combobox_mes.grid(row=7, column=1, padx=(3, 0), pady=(5, 15), sticky="nsew")
combobox_mes.insert(0, "01")
combobox_mes["state"] = "disabled"
combobox_mes.bind("<<ComboboxSelected>>", selected_mes)

combobox_año = ttk.Combobox(frame_filtros, state="normal", width=1)
combobox_año.grid(row=7, column=2, padx=(3, 10), pady=(5, 15), sticky="nsew")
combobox_año.insert(0, "2000")
combobox_año["state"] = "disabled"


boton_filtrar = ttk.Button(frame_filtros, text="Filtrar", width=5, command=filtrar_datos)
boton_filtrar.grid(row=8, column=0, columnspan=2, padx=(15, 0), pady=(0, 11), sticky="nsew")

boton_limpiar = ttk.Button(frame_filtros, text="Limpiar", width=6, command=actualizar)
boton_limpiar.grid(row=8, column=2, columnspan=2, padx=(5, 15), pady=(0, 11), sticky="nsew")


# FRAME REPORTE #
frame_reporte = ttk.LabelFrame(frame, text="Resumen de Gastos")
frame_reporte.grid(row=2, column=0, columnspan=2, padx=(5, 0), pady=(0, 5), sticky="nsew")

frame_total = ttk.Frame(frame_reporte)
frame_total.grid(row=0, column=0, padx=(5, 0), pady=(5, 10), sticky="nsew")

# Notebook
notebook = ttk.Notebook(frame_total)

meses = {
    1: "ENE",
    2: "FEB",
    3: "MAR",
    4: "ABR",
    5: "MAY",
    6: "JUN",
    7: "JUL",
    8: "AGO",
    9: "SEP",
    10: "OCT",
    11: "NOV",
    12: "DIC"
}
fecha_actual = datetime.now().date()
mes = fecha_actual.month
año = fecha_actual.year
mes_actual = meses[mes]
    
# Tab #1
tab_1 = ttk.Frame(notebook)
notebook.add(tab_1, text="Gastos")

def reporte_gastos():
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT
                    SUM(G.MONTO) "GASTO TOTAL",
                    CAST(strftime('%m', G.FECHA) AS INTEGER) "MES"
                FROM GASTOS G
                JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                WHERE CAST(strftime('%Y', G.FECHA) AS INTEGER) = :año
                GROUP BY "MES"
                ORDER BY "MES" DESC
                """,
                (año,),
            )
            gasto_mes = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)
            
        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
    
    if mes == 1:
        mes_pasado = meses[12]
        año_pasado = año-1
        
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    SELECT
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.FECHA) AS INTEGER) "MES"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE CAST(strftime('%Y', G.FECHA) AS INTEGER) = :año_pasado
                    GROUP BY "MES"
                    ORDER BY "MES" DESC
                    """,
                    (año_pasado,),
                )
                gasto_pasado = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion)

                if len(gasto_mes) == 0 and len(gasto_pasado) == 0:
                    entry_gasto_mes["state"] = "normal"
                    entry_gasto_mes.delete(0, "end")
                    entry_gasto_mes.insert(0, 0.0)
                    entry_gasto_mes["state"] = "readonly"
                    
                    entry_gasto_mes_pasado["state"] = "normal"
                    entry_gasto_mes_pasado.delete(0, "end")
                    entry_gasto_mes_pasado.insert(0, 0.0)
                    entry_gasto_mes_pasado["state"] = "readonly"
                    
                elif len(gasto_mes) == 1 and len(gasto_pasado) == 0:
                    entry_gasto_mes["state"] = "normal"
                    entry_gasto_mes.delete(0, "end")
                    entry_gasto_mes.insert(0, f"{mes_actual}   |   S/. " + str(round(gasto_mes[0][0],2)))
                    entry_gasto_mes["state"] = "readonly"
                    
                    entry_gasto_mes_pasado["state"] = "normal"
                    entry_gasto_mes_pasado.delete(0, "end")
                    entry_gasto_mes_pasado.insert(0, 0.0)
                    entry_gasto_mes_pasado["state"] = "readonly"
                    
                elif len(gasto_mes) == 0 and len(gasto_pasado) == 1:
                    entry_gasto_mes["state"] = "normal"
                    entry_gasto_mes.delete(0, "end")
                    entry_gasto_mes.insert(0, 0.0)
                    entry_gasto_mes["state"] = "readonly"
                    
                    entry_gasto_mes_pasado["state"] = "normal"
                    entry_gasto_mes_pasado.delete(0, "end")
                    entry_gasto_mes_pasado.insert(0, f"{mes_pasado}   |   S/. " + str(round(gasto_pasado[0][0],2)))
                    entry_gasto_mes_pasado["state"] = "readonly"
                    
                elif len(gasto_mes) >= 1 and len(gasto_pasado) >= 1:
                    entry_gasto_mes["state"] = "normal"
                    entry_gasto_mes.delete(0, "end")
                    entry_gasto_mes.insert(0, f"{mes_actual}   |   S/. " + str(round(gasto_mes[0][0],2)))
                    entry_gasto_mes["state"] = "readonly"
                    
                    entry_gasto_mes_pasado["state"] = "normal"
                    entry_gasto_mes_pasado.delete(0, "end")
                    entry_gasto_mes_pasado.insert(0, f"{mes_pasado}   |   S/. " + str(round(gasto_pasado[0][0],2)))
                    entry_gasto_mes_pasado["state"] = "readonly"
                    
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        conexion1 = conectar_bd()
        if conexion1:
            try:
                cursor = conexion1.cursor()
                cursor.execute(
                    """
                    SELECT
                        SUM(G.MONTO) "GASTO TOTAL"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE CAST(strftime('%Y', G.fecha) AS INTEGER) = :año
                    """,
                    (año,),
                )
                datos = cursor.fetchall()
                cursor.close()
                
                cerrar_bd(conexion1)
                
                if datos[0][0] is None:
                    entry_gasto_mes_promedio["state"] = "normal"
                    entry_gasto_mes_promedio.delete(0, "end")
                    entry_gasto_mes_promedio.insert(0, 0.0)
                    entry_gasto_mes_promedio["state"] = "readonly"
                    
                    entry_gasto_año["state"] = "normal"
                    entry_gasto_año.delete(0, "end")
                    entry_gasto_año.insert(0, 0.0)
                    entry_gasto_año["state"] = "readonly"
                else:
                    promedio = datos[0][0]/mes
                    entry_gasto_mes_promedio["state"] = "normal"
                    entry_gasto_mes_promedio.delete(0, "end")
                    entry_gasto_mes_promedio.insert(0, f"{año}   |   S/. " + str(round(promedio,2)) + "/mes")
                    entry_gasto_mes_promedio["state"] = "readonly"
                    
                    entry_gasto_año["state"] = "normal"
                    entry_gasto_año.delete(0, "end")
                    entry_gasto_año.insert(0, f"{año}   |   S/. " + str(round(datos[0][0],2)) + "/año")
                    entry_gasto_año["state"] = "readonly"
                
            except Exception as ex:
                cerrar_bd(conexion1)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
        
        conexion2 = conectar_bd()
        if conexion2:
            try:
                cursor = conexion2.cursor()
                cursor.execute(
                    """
                    SELECT
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.fecha) AS INTEGER) "MES"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE CAST(strftime('%Y', G.fecha) AS INTEGER) = :año
                    GROUP BY "MES"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (año,),
                )
                datos = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion2)
                
                if len(datos) == 0:
                    entry_gasto_alto["state"] = "normal"
                    entry_gasto_alto.delete(0, "end")
                    entry_gasto_alto.insert(0, 0.0)
                    entry_gasto_alto["state"] = "readonly"
                    
                    entry_gasto_bajo["state"] = "normal"
                    entry_gasto_bajo.delete(0, "end")
                    entry_gasto_bajo.insert(0, 0.0)
                    entry_gasto_bajo["state"] = "readonly"
                else:
                    mes_alto = datos[0][1]
                    mes_bajo = datos[-1][1]
                    formato_mes_alto = meses.get(mes_alto, "")
                    mes_alto = f"{formato_mes_alto}"
                    formato_mes_bajo = meses.get(mes_bajo, "")
                    mes_bajo = f"{formato_mes_bajo}"
                    
                    entry_gasto_alto["state"] = "normal"
                    entry_gasto_alto.delete(0, "end")
                    entry_gasto_alto.insert(0, f"{mes_alto}   |   S/. " + str(round(datos[0][0],2)))
                    entry_gasto_alto["state"] = "readonly"
                    
                    entry_gasto_bajo["state"] = "normal"
                    entry_gasto_bajo.delete(0, "end")
                    entry_gasto_bajo.insert(0, f"{mes_bajo}   |   S/. " + str(round(datos[-1][0],2)))
                    entry_gasto_bajo["state"] = "readonly"
                    
            except Exception as ex:
                cerrar_bd(conexion2)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
    else:
        mes_pasado = meses[mes-1]

        if (len(gasto_mes) == 0) or (len(gasto_mes) > 1 and gasto_mes[0][1] != mes and gasto_mes[1][1] != mes-1):
            entry_gasto_mes["state"] = "normal"
            entry_gasto_mes.delete(0, "end")
            entry_gasto_mes.insert(0, 0.0)
            entry_gasto_mes["state"] = "readonly"
            
            entry_gasto_mes_pasado["state"] = "normal"
            entry_gasto_mes_pasado.delete(0, "end")
            entry_gasto_mes_pasado.insert(0, 0.0)
            entry_gasto_mes_pasado["state"] = "readonly"
            
        elif len(gasto_mes) > 1 and gasto_mes[0][1] == mes and gasto_mes[1][1] == mes-1:
            entry_gasto_mes["state"] = "normal"
            entry_gasto_mes.delete(0, "end")
            entry_gasto_mes.insert(0, f"{mes_actual}   |   S/. " + str(round(gasto_mes[0][0],2)))
            entry_gasto_mes["state"] = "readonly"
            
            entry_gasto_mes_pasado["state"] = "normal"
            entry_gasto_mes_pasado.delete(0, "end")
            entry_gasto_mes_pasado.insert(0, f"{mes_pasado}   |   S/. " + str(round(gasto_mes[1][0],2)))
            entry_gasto_mes_pasado["state"] = "readonly"
            
        elif (len(gasto_mes) == 1 and gasto_mes[0][1] == mes) or (len(gasto_mes) > 1 and gasto_mes[0][1] == mes and gasto_mes[1][1] != mes-1):
            entry_gasto_mes["state"] = "normal"
            entry_gasto_mes.delete(0, "end")
            entry_gasto_mes.insert(0, f"{mes_actual}   |   S/. " + str(round(gasto_mes[0][0],2)))
            entry_gasto_mes["state"] = "readonly"
            
            entry_gasto_mes_pasado["state"] = "normal"
            entry_gasto_mes_pasado.delete(0, "end")
            entry_gasto_mes_pasado.insert(0, 0.0)
            entry_gasto_mes_pasado["state"] = "readonly"
            
        elif (len(gasto_mes) == 1 and gasto_mes[0][1] == mes-1) or (len(gasto_mes) > 1 and gasto_mes[0][1] != mes and gasto_mes[1][1] == mes-1):
            entry_gasto_mes["state"] = "normal"
            entry_gasto_mes.delete(0, "end")
            entry_gasto_mes.insert(0, 0.0)
            entry_gasto_mes["state"] = "readonly"
            
            entry_gasto_mes_pasado["state"] = "normal"
            entry_gasto_mes_pasado.delete(0, "end")
            entry_gasto_mes_pasado.insert(0, f"{mes_pasado}   |   S/. " + str(round(gasto_mes[0][0],2)))
            entry_gasto_mes_pasado["state"] = "readonly"
                       
        conexion1 = conectar_bd()
        if conexion1:
            try:
                cursor = conexion1.cursor()
                cursor.execute(
                    """
                    SELECT
                        SUM(G.MONTO) "GASTO TOTAL"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE CAST(strftime('%Y', G.fecha) AS INTEGER) = :año
                    """,
                    (año,),
                )
                datos = cursor.fetchall()
                cursor.close()
                
                cerrar_bd(conexion1)
                
                if datos[0][0] is None:
                    entry_gasto_mes_promedio["state"] = "normal"
                    entry_gasto_mes_promedio.delete(0, "end")
                    entry_gasto_mes_promedio.insert(0, 0.0)
                    entry_gasto_mes_promedio["state"] = "readonly"
                    
                    entry_gasto_año["state"] = "normal"
                    entry_gasto_año.delete(0, "end")
                    entry_gasto_año.insert(0, 0.0)
                    entry_gasto_año["state"] = "readonly"
                else:
                    promedio = datos[0][0]/mes
                    entry_gasto_mes_promedio["state"] = "normal"
                    entry_gasto_mes_promedio.delete(0, "end")
                    entry_gasto_mes_promedio.insert(0, f"{año}   |   S/. " + str(round(promedio,2)) + "/mes")
                    entry_gasto_mes_promedio["state"] = "readonly"
                    
                    entry_gasto_año["state"] = "normal"
                    entry_gasto_año.delete(0, "end")
                    entry_gasto_año.insert(0, f"{año}   |   S/. " + str(round(datos[0][0],2)) + "/año")
                    entry_gasto_año["state"] = "readonly"
                
            except Exception as ex:
                cerrar_bd(conexion1)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
        
        conexion2 = conectar_bd()
        if conexion2:
            try:
                cursor = conexion2.cursor()
                cursor.execute(
                    """
                    SELECT
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.fecha) AS INTEGER) "MES"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE CAST(strftime('%Y', G.fecha) AS INTEGER) = :año
                    GROUP BY "MES"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (año,),
                )
                datos = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion2)
                
                if len(datos) == 0:
                    entry_gasto_alto["state"] = "normal"
                    entry_gasto_alto.delete(0, "end")
                    entry_gasto_alto.insert(0, 0.0)
                    entry_gasto_alto["state"] = "readonly"
                    
                    entry_gasto_bajo["state"] = "normal"
                    entry_gasto_bajo.delete(0, "end")
                    entry_gasto_bajo.insert(0, 0.0)
                    entry_gasto_bajo["state"] = "readonly"
                else:
                    mes_alto = datos[0][1]
                    mes_bajo = datos[-1][1]
                    formato_mes_alto = meses.get(mes_alto, "")
                    mes_alto = f"{formato_mes_alto}"
                    formato_mes_bajo = meses.get(mes_bajo, "")
                    mes_bajo = f"{formato_mes_bajo}"
                    
                    entry_gasto_alto["state"] = "normal"
                    entry_gasto_alto.delete(0, "end")
                    entry_gasto_alto.insert(0, f"{mes_alto}   |   S/. " + str(round(datos[0][0],2)))
                    entry_gasto_alto["state"] = "readonly"
                    
                    entry_gasto_bajo["state"] = "normal"
                    entry_gasto_bajo.delete(0, "end")
                    entry_gasto_bajo.insert(0, f"{mes_bajo}   |   S/. " + str(round(datos[-1][0],2)))
                    entry_gasto_bajo["state"] = "readonly"
                    
            except Exception as ex:
                cerrar_bd(conexion2)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
label_gasto_mes = ttk.Label(tab_1, text="Gasto Mes Actual:")
label_gasto_mes.grid(row=0, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_gasto_mes = ttk.Entry(tab_1, state="disabled", width=27)
entry_gasto_mes.grid(row=1, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_gasto_mes_pasado = ttk.Label(tab_1, text="Gasto Mes Pasado:")
label_gasto_mes_pasado.grid(row=0, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_gasto_mes_pasado = ttk.Entry(tab_1, state="disabled", width=27)
entry_gasto_mes_pasado.grid(row=1, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_gasto_mes_promedio = ttk.Label(tab_1, text="Gasto Mes Promedio:")
label_gasto_mes_promedio.grid(row=2, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_gasto_mes_promedio = ttk.Entry(tab_1, state="disabled", width=27)
entry_gasto_mes_promedio.grid(row=3, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_gasto_año = ttk.Label(tab_1, text="Gasto Año Actual:")
label_gasto_año.grid(row=2, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_gasto_año = ttk.Entry(tab_1, state="disabled", width=27)
entry_gasto_año.grid(row=3, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_gasto_alto = ttk.Label(tab_1, text="Gasto Más Alto (Mes):")
label_gasto_alto.grid(row=4, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_gasto_alto = ttk.Entry(tab_1, state="disabled", width=27)
entry_gasto_alto.grid(row=5, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_gasto_bajo = ttk.Label(tab_1, text="Gasto Más Bajo (Mes):")
label_gasto_bajo.grid(row=4, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_gasto_bajo = ttk.Entry(tab_1, state="disabled", width=27)
entry_gasto_bajo.grid(row=5, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")

# Tab #2
tab_2 = ttk.Frame(notebook)
notebook.add(tab_2, text="Usuarios")

def reporte_usuarios():
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT
                    U.NOMBRE_USUARIO "USUARIO",
                    COUNT(*) "FRECUENCIA",
                    SUM(G.MONTO) "GASTO TOTAL",
                    CAST(strftime('%m', G.fecha) AS INTEGER) "MES",
                    CAST(strftime('%Y', G.fecha) AS INTEGER) "AÑO"
                FROM GASTOS G
                JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                WHERE "MES" = :mes AND "AÑO" = :año
                GROUP BY "USUARIO"
                ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                """,
                (mes, año,),
            )
            datos1 = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)
            
        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
            
    if mes == 1:
        mes_pasado = meses[12]
        año_pasado = año-1
        mes_p = 12
        
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    SELECT
                        U.NOMBRE_USUARIO "USUARIO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.fecha) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.fecha) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE "MES" = :mes_p AND "AÑO" = :año_pasado
                    GROUP BY "USUARIO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (mes_p, año_pasado,),
                )
                datos2 = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        if len(datos1) == 0 and len(datos2) == 0:
            entry_frecuencia["state"] = "normal"
            entry_frecuencia.delete(0, "end")
            entry_frecuencia.insert(0, "—")
            entry_frecuencia["state"] = "readonly"
            
            entry_frecuencia_mes_pasado["state"] = "normal"
            entry_frecuencia_mes_pasado.delete(0, "end")
            entry_frecuencia_mes_pasado.insert(0, "—")
            entry_frecuencia_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) == 0:
            entry_frecuencia["state"] = "normal"
            entry_frecuencia.delete(0, "end")
            entry_frecuencia.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia["state"] = "readonly"

            entry_frecuencia_mes_pasado["state"] = "normal"
            entry_frecuencia_mes_pasado.delete(0, "end")
            entry_frecuencia_mes_pasado.insert(0, "—")
            entry_frecuencia_mes_pasado["state"] = "readonly"
            
        elif len(datos1) == 0 and len(datos2) > 0:
            entry_frecuencia["state"] = "normal"
            entry_frecuencia.delete(0, "end")
            entry_frecuencia.insert(0, "—")
            entry_frecuencia["state"] = "readonly"

            entry_frecuencia_mes_pasado["state"] = "normal"
            entry_frecuencia_mes_pasado.delete(0, "end")
            entry_frecuencia_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) > 0:
            entry_frecuencia["state"] = "normal"
            entry_frecuencia.delete(0, "end")
            entry_frecuencia.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia["state"] = "readonly"

            entry_frecuencia_mes_pasado["state"] = "normal"
            entry_frecuencia_mes_pasado.delete(0, "end")
            entry_frecuencia_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_mes_pasado["state"] = "readonly"
            
        conexion1 = conectar_bd()
        if conexion1:
            try:
                cursor = conexion1.cursor()
                cursor.execute(
                    """
                    SELECT
                        U.NOMBRE_USUARIO "USUARIO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%Y', G.fecha) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE "AÑO" = :año
                    GROUP BY "USUARIO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (año,),
                )
                datos3 = cursor.fetchall()
                cursor.close()
                
                cerrar_bd(conexion1)
                
                if len(datos3) == 0:
                    entry_frecuencia_promedio["state"] = "normal"
                    entry_frecuencia_promedio.delete(0, "end")
                    entry_frecuencia_promedio.insert(0, "—")
                    entry_frecuencia_promedio["state"] = "readonly"
                    
                    entry_frecuencia_año["state"] = "normal"
                    entry_frecuencia_año.delete(0, "end")
                    entry_frecuencia_año.insert(0, "—")
                    entry_frecuencia_año["state"] = "readonly"
                else:
                    promedio = datos3[0][1]/mes
                    entry_frecuencia_promedio["state"] = "normal"
                    entry_frecuencia_promedio.delete(0, "end")
                    entry_frecuencia_promedio.insert(0, f"{año} | " + str(datos3[0][0]) + " | fi: " + str(round((promedio),2)) + "/mes")
                    entry_frecuencia_promedio["state"] = "readonly"
                    
                    entry_frecuencia_año["state"] = "normal"
                    entry_frecuencia_año.delete(0, "end")
                    entry_frecuencia_año.insert(0, f"{año} | " + str(datos3[0][0]) + " |  fi: " + str(datos3[0][1]) + "/año")
                    entry_frecuencia_año["state"] = "readonly"
                
            except Exception as ex:
                cerrar_bd(conexion1)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
        
        conexion2 = conectar_bd()
        if conexion2:
            try:
                cursor = conexion2.cursor()
                cursor.execute(
                    """
                    SELECT
                        U.NOMBRE_USUARIO "USUARIO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.fecha) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.fecha) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE "MES" = :mes AND "AÑO" = :año
                    GROUP BY "USUARIO"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (mes, año,),
                )
                datos_ = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion2)
                
            except Exception as ex:
                cerrar_bd(conexion2)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        conexion3 = conectar_bd()
        if conexion3:
            try:
                cursor = conexion3.cursor()
                cursor.execute(
                    """
                    SELECT
                        U.NOMBRE_USUARIO "USUARIO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.fecha) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.fecha) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE "MES" = :mes_p AND "AÑO" = :año_pasado
                    GROUP BY "USUARIO"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (mes_p, año_pasado,),
                )
                datos_p = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion3)
                
            except Exception as ex:
                cerrar_bd(conexion3)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        if len(datos_) == 0 and len(datos_p) == 0:
            entry_mas_gastos["state"] = "normal"
            entry_mas_gastos.delete(0, "end")
            entry_mas_gastos.insert(0, "—")
            entry_mas_gastos["state"] = "readonly"
            
            entry_mas_gastos_pasado["state"] = "normal"
            entry_mas_gastos_pasado.delete(0, "end")
            entry_mas_gastos_pasado.insert(0, "—")
            entry_mas_gastos_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) == 0:
            entry_mas_gastos["state"] = "normal"
            entry_mas_gastos.delete(0, "end")
            entry_mas_gastos.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos["state"] = "readonly"
            
            entry_mas_gastos_pasado["state"] = "normal"
            entry_mas_gastos_pasado.delete(0, "end")
            entry_mas_gastos_pasado.insert(0, "—")
            entry_mas_gastos_pasado["state"] = "readonly"
            
        elif len(datos_) == 0 and len(datos_p) > 0:
            entry_mas_gastos["state"] = "normal"
            entry_mas_gastos.delete(0, "end")
            entry_mas_gastos.insert(0, "—")
            entry_mas_gastos["state"] = "readonly"
            
            entry_mas_gastos_pasado["state"] = "normal"
            entry_mas_gastos_pasado.delete(0, "end")
            entry_mas_gastos_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) > 0:
            entry_mas_gastos["state"] = "normal"
            entry_mas_gastos.delete(0, "end")
            entry_mas_gastos.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos["state"] = "readonly"
            
            entry_mas_gastos_pasado["state"] = "normal"
            entry_mas_gastos_pasado.delete(0, "end")
            entry_mas_gastos_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_pasado["state"] = "readonly"
            
    else:
        mes_pasado = meses[mes-1]
        
        conexion = conectar_bd()
        if conexion:
            mes_p = mes-1
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    SELECT
                        U.NOMBRE_USUARIO "USUARIO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.fecha) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.fecha) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE "MES" = :mes_p AND "AÑO" = :año
                    GROUP BY "USUARIO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (mes_p, año,),
                )
                datos2 = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                    
        if len(datos1) == 0 and len(datos2) == 0:
            entry_frecuencia["state"] = "normal"
            entry_frecuencia.delete(0, "end")
            entry_frecuencia.insert(0, "—")
            entry_frecuencia["state"] = "readonly"
            
            entry_frecuencia_mes_pasado["state"] = "normal"
            entry_frecuencia_mes_pasado.delete(0, "end")
            entry_frecuencia_mes_pasado.insert(0, "—")
            entry_frecuencia_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) == 0:
            entry_frecuencia["state"] = "normal"
            entry_frecuencia.delete(0, "end")
            entry_frecuencia.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia["state"] = "readonly"

            entry_frecuencia_mes_pasado["state"] = "normal"
            entry_frecuencia_mes_pasado.delete(0, "end")
            entry_frecuencia_mes_pasado.insert(0, "—")
            entry_frecuencia_mes_pasado["state"] = "readonly"
            
        elif len(datos1) == 0 and len(datos2) > 0:
            entry_frecuencia["state"] = "normal"
            entry_frecuencia.delete(0, "end")
            entry_frecuencia.insert(0, "—")
            entry_frecuencia["state"] = "readonly"

            entry_frecuencia_mes_pasado["state"] = "normal"
            entry_frecuencia_mes_pasado.delete(0, "end")
            entry_frecuencia_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) > 0:
            entry_frecuencia["state"] = "normal"
            entry_frecuencia.delete(0, "end")
            entry_frecuencia.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia["state"] = "readonly"

            entry_frecuencia_mes_pasado["state"] = "normal"
            entry_frecuencia_mes_pasado.delete(0, "end")
            entry_frecuencia_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_mes_pasado["state"] = "readonly"
                       
        conexion1 = conectar_bd()
        if conexion1:
            try:
                cursor = conexion1.cursor()
                cursor.execute(
                    """
                    SELECT
                        U.NOMBRE_USUARIO "USUARIO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%Y', G.fecha) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE "AÑO" = :año
                    GROUP BY "USUARIO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (año,),
                )
                datos3 = cursor.fetchall()
                cursor.close()
                
                cerrar_bd(conexion1)
                
                if len(datos3) == 0:
                    entry_frecuencia_promedio["state"] = "normal"
                    entry_frecuencia_promedio.delete(0, "end")
                    entry_frecuencia_promedio.insert(0, "—")
                    entry_frecuencia_promedio["state"] = "readonly"
                    
                    entry_frecuencia_año["state"] = "normal"
                    entry_frecuencia_año.delete(0, "end")
                    entry_frecuencia_año.insert(0, "—")
                    entry_frecuencia_año["state"] = "readonly"
                else:
                    promedio = datos3[0][1]/mes
                    entry_frecuencia_promedio["state"] = "normal"
                    entry_frecuencia_promedio.delete(0, "end")
                    entry_frecuencia_promedio.insert(0, f"{año} | " + str(datos3[0][0]) + " | fi: " + str(round((promedio),2)) + "/mes")
                    entry_frecuencia_promedio["state"] = "readonly"
                    
                    entry_frecuencia_año["state"] = "normal"
                    entry_frecuencia_año.delete(0, "end")
                    entry_frecuencia_año.insert(0, f"{año} | " + str(datos3[0][0]) + " |  fi: " + str(datos3[0][1]) + "/año")
                    entry_frecuencia_año["state"] = "readonly"
                
            except Exception as ex:
                cerrar_bd(conexion1)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
        
        conexion2 = conectar_bd()
        if conexion2:
            try:
                cursor = conexion2.cursor()
                cursor.execute(
                    """
                    SELECT
                        U.NOMBRE_USUARIO "USUARIO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.fecha) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.fecha) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE "MES" = :mes AND "AÑO" = :año
                    GROUP BY "USUARIO"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (mes, año,),
                )
                datos_ = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion2)
                
            except Exception as ex:
                cerrar_bd(conexion2)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        conexion3 = conectar_bd()
        if conexion3:
            mes_p = mes-1
            try:
                cursor = conexion3.cursor()
                cursor.execute(
                    """
                    SELECT
                        U.NOMBRE_USUARIO "USUARIO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.fecha) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.fecha) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
                    WHERE "MES" = :mes_p AND "AÑO" = :año
                    GROUP BY "USUARIO"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (mes_p, año,),
                )
                datos_p = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion3)
                
            except Exception as ex:
                cerrar_bd(conexion3)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        if len(datos_) == 0 and len(datos_p) == 0:
            entry_mas_gastos["state"] = "normal"
            entry_mas_gastos.delete(0, "end")
            entry_mas_gastos.insert(0, "—")
            entry_mas_gastos["state"] = "readonly"
            
            entry_mas_gastos_pasado["state"] = "normal"
            entry_mas_gastos_pasado.delete(0, "end")
            entry_mas_gastos_pasado.insert(0, "—")
            entry_mas_gastos_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) == 0:
            entry_mas_gastos["state"] = "normal"
            entry_mas_gastos.delete(0, "end")
            entry_mas_gastos.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos["state"] = "readonly"
            
            entry_mas_gastos_pasado["state"] = "normal"
            entry_mas_gastos_pasado.delete(0, "end")
            entry_mas_gastos_pasado.insert(0, "—")
            entry_mas_gastos_pasado["state"] = "readonly"
            
        elif len(datos_) == 0 and len(datos_p) > 0:
            entry_mas_gastos["state"] = "normal"
            entry_mas_gastos.delete(0, "end")
            entry_mas_gastos.insert(0, "—")
            entry_mas_gastos["state"] = "readonly"
            
            entry_mas_gastos_pasado["state"] = "normal"
            entry_mas_gastos_pasado.delete(0, "end")
            entry_mas_gastos_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) > 0:
            entry_mas_gastos["state"] = "normal"
            entry_mas_gastos.delete(0, "end")
            entry_mas_gastos.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos["state"] = "readonly"
            
            entry_mas_gastos_pasado["state"] = "normal"
            entry_mas_gastos_pasado.delete(0, "end")
            entry_mas_gastos_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_pasado["state"] = "readonly"
            
label_frecuencia = ttk.Label(tab_2, text="Frecuencia Mes Actual:")
label_frecuencia.grid(row=0, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia = ttk.Entry(tab_2, state="disabled", width=27)
entry_frecuencia.grid(row=1, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_frecuencia_mes_pasado = ttk.Label(tab_2, text="Frecuencia Mes Pasado:")
label_frecuencia_mes_pasado.grid(row=0, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia_mes_pasado = ttk.Entry(tab_2, state="disabled", width=27)
entry_frecuencia_mes_pasado.grid(row=1, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_frecuencia_promedio = ttk.Label(tab_2, text="Frecuencia Mes Promedio:")
label_frecuencia_promedio.grid(row=2, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia_promedio = ttk.Entry(tab_2, state="disabled", width=27)
entry_frecuencia_promedio.grid(row=3, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_frecuencia_año = ttk.Label(tab_2, text="Frecuencia Año Actual:")
label_frecuencia_año.grid(row=2, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia_año = ttk.Entry(tab_2, state="disabled", width=27)
entry_frecuencia_año.grid(row=3, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_mas_gastos = ttk.Label(tab_2, text="+ Gastos Mes Actual:")
label_mas_gastos.grid(row=4, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_mas_gastos = ttk.Entry(tab_2, state="disabled", width=27)
entry_mas_gastos.grid(row=5, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_mas_gastos_pasado = ttk.Label(tab_2, text="+ Gastos Mes Pasado:")
label_mas_gastos_pasado.grid(row=4, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_mas_gastos_pasado = ttk.Entry(tab_2, state="disabled", width=27)
entry_mas_gastos_pasado.grid(row=5, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")


# Tab #3
tab_3 = ttk.Frame(notebook)
notebook.add(tab_3, text="Bancos")

def reporte_bancos():
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT
                    B.NOMBRE_BANCO "BANCO",
                    COUNT(*) "FRECUENCIA",
                    SUM(G.MONTO) "GASTO TOTAL",
                    CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                    CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                FROM GASTOS G
                JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                WHERE "MES" = :mes AND "AÑO" = :año
                GROUP BY "BANCO"
                ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                """,
                (mes, año,),
            )
            datos1 = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)
            
        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
            
    if mes == 1:
        mes_pasado = meses[12]
        año_pasado = año-1
        mes_p = 12
        
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    SELECT
                        B.NOMBRE_BANCO "BANCO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                    JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                    WHERE "MES" = :mes_p AND "AÑO" = :año_pasado
                    GROUP BY "BANCO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (mes_p, año_pasado,),
                )
                datos2 = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        if len(datos1) == 0 and len(datos2) == 0:
            entry_frecuencia_banco["state"] = "normal"
            entry_frecuencia_banco.delete(0, "end")
            entry_frecuencia_banco.insert(0, "—")
            entry_frecuencia_banco["state"] = "readonly"
            
            entry_frecuencia_banco_mes_pasado["state"] = "normal"
            entry_frecuencia_banco_mes_pasado.delete(0, "end")
            entry_frecuencia_banco_mes_pasado.insert(0, "—")
            entry_frecuencia_banco_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) == 0:
            entry_frecuencia_banco["state"] = "normal"
            entry_frecuencia_banco.delete(0, "end")
            entry_frecuencia_banco.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia_banco["state"] = "readonly"

            entry_frecuencia_banco_mes_pasado["state"] = "normal"
            entry_frecuencia_banco_mes_pasado.delete(0, "end")
            entry_frecuencia_banco_mes_pasado.insert(0, "—")
            entry_frecuencia_banco_mes_pasado["state"] = "readonly"
            
        elif len(datos1) == 0 and len(datos2) > 0:
            entry_frecuencia_banco["state"] = "normal"
            entry_frecuencia_banco.delete(0, "end")
            entry_frecuencia_banco.insert(0, "—")
            entry_frecuencia_banco["state"] = "readonly"

            entry_frecuencia_banco_mes_pasado["state"] = "normal"
            entry_frecuencia_banco_mes_pasado.delete(0, "end")
            entry_frecuencia_banco_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_banco_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) > 0:
            entry_frecuencia_banco["state"] = "normal"
            entry_frecuencia_banco.delete(0, "end")
            entry_frecuencia_banco.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia_banco["state"] = "readonly"

            entry_frecuencia_banco_mes_pasado["state"] = "normal"
            entry_frecuencia_banco_mes_pasado.delete(0, "end")
            entry_frecuencia_banco_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_banco_mes_pasado["state"] = "readonly"
            
        conexion1 = conectar_bd()
        if conexion1:
            try:
                cursor = conexion1.cursor()
                cursor.execute(
                    """
                    SELECT
                        B.NOMBRE_BANCO "BANCO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                    JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                    WHERE "AÑO" = :año
                    GROUP BY "BANCO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (año,),
                )
                datos3 = cursor.fetchall()
                cursor.close()
                
                cerrar_bd(conexion1)
                
                if len(datos3) == 0:
                    entry_frecuencia_banco_promedio["state"] = "normal"
                    entry_frecuencia_banco_promedio.delete(0, "end")
                    entry_frecuencia_banco_promedio.insert(0, "—")
                    entry_frecuencia_banco_promedio["state"] = "readonly"
                    
                    entry_frecuencia_banco_año["state"] = "normal"
                    entry_frecuencia_banco_año.delete(0, "end")
                    entry_frecuencia_banco_año.insert(0, "—")
                    entry_frecuencia_banco_año["state"] = "readonly"
                else:
                    promedio = datos3[0][1]/mes
                    entry_frecuencia_banco_promedio["state"] = "normal"
                    entry_frecuencia_banco_promedio.delete(0, "end")
                    entry_frecuencia_banco_promedio.insert(0, f"{año} | " + str(datos3[0][0]) + " | fi: " + str(round((promedio),2)) + "/mes")
                    entry_frecuencia_banco_promedio["state"] = "readonly"
                    
                    entry_frecuencia_banco_año["state"] = "normal"
                    entry_frecuencia_banco_año.delete(0, "end")
                    entry_frecuencia_banco_año.insert(0, f"{año} | " + str(datos3[0][0]) + " |  fi: " + str(datos3[0][1]) + "/año")
                    entry_frecuencia_banco_año["state"] = "readonly"
                
            except Exception as ex:
                cerrar_bd(conexion1)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
        
        conexion2 = conectar_bd()
        if conexion2:
            try:
                cursor = conexion2.cursor()
                cursor.execute(
                    """
                    SELECT
                        B.NOMBRE_BANCO "BANCO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                    JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                    WHERE "MES" = :mes AND "AÑO" = :año
                    GROUP BY "BANCO"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (mes, año,),
                )
                datos_ = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion2)
                
            except Exception as ex:
                cerrar_bd(conexion2)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        conexion3 = conectar_bd()
        if conexion3:
            try:
                cursor = conexion3.cursor()
                cursor.execute(
                    """
                    SELECT
                        B.NOMBRE_BANCO "BANCO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                    JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                    WHERE "MES" = :mes_p AND "AÑO" = :año_pasado
                    GROUP BY "BANCO"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (mes_p, año_pasado,),
                )
                datos_p = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion3)
                
            except Exception as ex:
                cerrar_bd(conexion3)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        if len(datos_) == 0 and len(datos_p) == 0:
            entry_mas_gastos_banco["state"] = "normal"
            entry_mas_gastos_banco.delete(0, "end")
            entry_mas_gastos_banco.insert(0, "—")
            entry_mas_gastos_banco["state"] = "readonly"
            
            entry_mas_gastos_banco_pasado["state"] = "normal"
            entry_mas_gastos_banco_pasado.delete(0, "end")
            entry_mas_gastos_banco_pasado.insert(0, "—")
            entry_mas_gastos_banco_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) == 0:
            entry_mas_gastos_banco["state"] = "normal"
            entry_mas_gastos_banco.delete(0, "end")
            entry_mas_gastos_banco.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos_banco["state"] = "readonly"
            
            entry_mas_gastos_banco_pasado["state"] = "normal"
            entry_mas_gastos_banco_pasado.delete(0, "end")
            entry_mas_gastos_banco_pasado.insert(0, "—")
            entry_mas_gastos_banco_pasado["state"] = "readonly"
            
        elif len(datos_) == 0 and len(datos_p) > 0:
            entry_mas_gastos_banco["state"] = "normal"
            entry_mas_gastos_banco.delete(0, "end")
            entry_mas_gastos_banco.insert(0, "—")
            entry_mas_gastos_banco["state"] = "readonly"
            
            entry_mas_gastos_banco_pasado["state"] = "normal"
            entry_mas_gastos_banco_pasado.delete(0, "end")
            entry_mas_gastos_banco_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_banco_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) > 0:
            entry_mas_gastos_banco["state"] = "normal"
            entry_mas_gastos_banco.delete(0, "end")
            entry_mas_gastos_banco.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos_banco["state"] = "readonly"
            
            entry_mas_gastos_banco_pasado["state"] = "normal"
            entry_mas_gastos_banco_pasado.delete(0, "end")
            entry_mas_gastos_banco_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_banco_pasado["state"] = "readonly"
            
    else:
        mes_pasado = meses[mes-1]
        
        conexion = conectar_bd()
        if conexion:
            mes_p = mes-1
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    SELECT
                        B.NOMBRE_BANCO "BANCO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                    JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                    WHERE "MES" = :mes_p AND "AÑO" = :año
                    GROUP BY "BANCO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (mes_p, año,),
                )
                datos2 = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                    
        if len(datos1) == 0 and len(datos2) == 0:
            entry_frecuencia_banco["state"] = "normal"
            entry_frecuencia_banco.delete(0, "end")
            entry_frecuencia_banco.insert(0, "—")
            entry_frecuencia_banco["state"] = "readonly"
            
            entry_frecuencia_banco_mes_pasado["state"] = "normal"
            entry_frecuencia_banco_mes_pasado.delete(0, "end")
            entry_frecuencia_banco_mes_pasado.insert(0, "—")
            entry_frecuencia_banco_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) == 0:
            entry_frecuencia_banco["state"] = "normal"
            entry_frecuencia_banco.delete(0, "end")
            entry_frecuencia_banco.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia_banco["state"] = "readonly"

            entry_frecuencia_banco_mes_pasado["state"] = "normal"
            entry_frecuencia_banco_mes_pasado.delete(0, "end")
            entry_frecuencia_banco_mes_pasado.insert(0, "—")
            entry_frecuencia_banco_mes_pasado["state"] = "readonly"
            
        elif len(datos1) == 0 and len(datos2) > 0:
            entry_frecuencia_banco["state"] = "normal"
            entry_frecuencia_banco.delete(0, "end")
            entry_frecuencia_banco.insert(0, "—")
            entry_frecuencia_banco["state"] = "readonly"

            entry_frecuencia_banco_mes_pasado["state"] = "normal"
            entry_frecuencia_banco_mes_pasado.delete(0, "end")
            entry_frecuencia_banco_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_banco_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) > 0:
            entry_frecuencia_banco["state"] = "normal"
            entry_frecuencia_banco.delete(0, "end")
            entry_frecuencia_banco.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia_banco["state"] = "readonly"

            entry_frecuencia_banco_mes_pasado["state"] = "normal"
            entry_frecuencia_banco_mes_pasado.delete(0, "end")
            entry_frecuencia_banco_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_banco_mes_pasado["state"] = "readonly"
                       
        conexion1 = conectar_bd()
        if conexion1:
            try:
                cursor = conexion1.cursor()
                cursor.execute(
                    """
                    SELECT
                        B.NOMBRE_BANCO "BANCO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                    JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                    WHERE "AÑO" = :año
                    GROUP BY "BANCO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (año,),
                )
                datos3 = cursor.fetchall()
                cursor.close()
                
                cerrar_bd(conexion1)
                
                if len(datos3) == 0:
                    entry_frecuencia_banco_promedio["state"] = "normal"
                    entry_frecuencia_banco_promedio.delete(0, "end")
                    entry_frecuencia_banco_promedio.insert(0, "—")
                    entry_frecuencia_banco_promedio["state"] = "readonly"
                    
                    entry_frecuencia_banco_año["state"] = "normal"
                    entry_frecuencia_banco_año.delete(0, "end")
                    entry_frecuencia_banco_año.insert(0, "—")
                    entry_frecuencia_banco_año["state"] = "readonly"
                else:
                    promedio = datos3[0][1]/mes
                    entry_frecuencia_banco_promedio["state"] = "normal"
                    entry_frecuencia_banco_promedio.delete(0, "end")
                    entry_frecuencia_banco_promedio.insert(0, f"{año} | " + str(datos3[0][0]) + " | fi: " + str(round((promedio),2)) + "/mes")
                    entry_frecuencia_banco_promedio["state"] = "readonly"
                    
                    entry_frecuencia_banco_año["state"] = "normal"
                    entry_frecuencia_banco_año.delete(0, "end")
                    entry_frecuencia_banco_año.insert(0, f"{año} | " + str(datos3[0][0]) + " |  fi: " + str(datos3[0][1]) + "/año")
                    entry_frecuencia_banco_año["state"] = "readonly"
                
            except Exception as ex:
                cerrar_bd(conexion1)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
        
        conexion2 = conectar_bd()
        if conexion2:
            try:
                cursor = conexion2.cursor()
                cursor.execute(
                    """
                    SELECT
                        B.NOMBRE_BANCO "BANCO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                    JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                    WHERE "MES" = :mes AND "AÑO" = :año
                    GROUP BY "BANCO"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (mes, año,),
                )
                datos_ = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion2)
                
            except Exception as ex:
                cerrar_bd(conexion2)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        conexion3 = conectar_bd()
        if conexion3:
            mes_p = mes-1
            try:
                cursor = conexion3.cursor()
                cursor.execute(
                    """
                    SELECT
                        B.NOMBRE_BANCO "BANCO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.fecha) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.fecha) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                    JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                    WHERE "MES" = :mes_p AND "AÑO" = :año
                    GROUP BY "BANCO"
                    ORDER BY "GASTO TOTAL" DESC

                    """,
                    (mes_p, año,),
                )
                datos_p = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion3)
                
            except Exception as ex:
                cerrar_bd(conexion3)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        if len(datos_) == 0 and len(datos_p) == 0:
            entry_mas_gastos_banco["state"] = "normal"
            entry_mas_gastos_banco.delete(0, "end")
            entry_mas_gastos_banco.insert(0, "—")
            entry_mas_gastos_banco["state"] = "readonly"
            
            entry_mas_gastos_banco_pasado["state"] = "normal"
            entry_mas_gastos_banco_pasado.delete(0, "end")
            entry_mas_gastos_banco_pasado.insert(0, "—")
            entry_mas_gastos_banco_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) == 0:
            entry_mas_gastos_banco["state"] = "normal"
            entry_mas_gastos_banco.delete(0, "end")
            entry_mas_gastos_banco.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos_banco["state"] = "readonly"
            
            entry_mas_gastos_banco_pasado["state"] = "normal"
            entry_mas_gastos_banco_pasado.delete(0, "end")
            entry_mas_gastos_banco_pasado.insert(0, "—")
            entry_mas_gastos_banco_pasado["state"] = "readonly"
            
        elif len(datos_) == 0 and len(datos_p) > 0:
            entry_mas_gastos_banco["state"] = "normal"
            entry_mas_gastos_banco.delete(0, "end")
            entry_mas_gastos_banco.insert(0, "—")
            entry_mas_gastos_banco["state"] = "readonly"
            
            entry_mas_gastos_banco_pasado["state"] = "normal"
            entry_mas_gastos_banco_pasado.delete(0, "end")
            entry_mas_gastos_banco_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_banco_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) > 0:
            entry_mas_gastos_banco["state"] = "normal"
            entry_mas_gastos_banco.delete(0, "end")
            entry_mas_gastos_banco.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos_banco["state"] = "readonly"
            
            entry_mas_gastos_banco_pasado["state"] = "normal"
            entry_mas_gastos_banco_pasado.delete(0, "end")
            entry_mas_gastos_banco_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_banco_pasado["state"] = "readonly"

label_frecuencia_banco = ttk.Label(tab_3, text="Frecuencia Mes Actual:")
label_frecuencia_banco.grid(row=0, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia_banco = ttk.Entry(tab_3, state="disabled", width=27)
entry_frecuencia_banco.grid(row=1, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_frecuencia_banco_mes_pasado = ttk.Label(tab_3, text="Frecuencia Mes Pasado:")
label_frecuencia_banco_mes_pasado.grid(row=0, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia_banco_mes_pasado = ttk.Entry(tab_3, state="disabled", width=27)
entry_frecuencia_banco_mes_pasado.grid(row=1, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_frecuencia_banco_promedio = ttk.Label(tab_3, text="Frecuencia Mes Promedio:")
label_frecuencia_banco_promedio.grid(row=2, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia_banco_promedio = ttk.Entry(tab_3, state="disabled", width=27)
entry_frecuencia_banco_promedio.grid(row=3, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_frecuencia_banco_año = ttk.Label(tab_3, text="Frecuencia Año Actual:")
label_frecuencia_banco_año.grid(row=2, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia_banco_año = ttk.Entry(tab_3, state="disabled", width=27)
entry_frecuencia_banco_año.grid(row=3, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_mas_gastos_banco = ttk.Label(tab_3, text="+ Gastos Mes Actual:")
label_mas_gastos_banco.grid(row=4, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_mas_gastos_banco = ttk.Entry(tab_3, state="disabled", width=27)
entry_mas_gastos_banco.grid(row=5, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_mas_gastos_banco_pasado = ttk.Label(tab_3, text="+ Gastos Mes Pasado:")
label_mas_gastos_banco_pasado.grid(row=4, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_mas_gastos_banco_pasado = ttk.Entry(tab_3, state="disabled", width=27)
entry_mas_gastos_banco_pasado.grid(row=5, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")


# Tab #4
tab_4 = ttk.Frame(notebook)
notebook.add(tab_4, text="Establecimientos")

def reporte_establecimientos():
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT
                    E.NOMBRE_EST "ESTABLECIMIENTO",
                    COUNT(*) "FRECUENCIA",
                    SUM(G.MONTO) "GASTO TOTAL",
                    CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                    CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                FROM GASTOS G
                JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
                WHERE "MES" = :mes AND "AÑO" = :año
                GROUP BY "ESTABLECIMIENTO"
                ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                """,
                (mes, año,),
            )
            datos1 = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)
            
        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
            
    if mes == 1:
        mes_pasado = meses[12]
        año_pasado = año-1
        mes_p = 12
        
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    SELECT
                        E.NOMBRE_EST "ESTABLECIMIENTO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
                    WHERE "MES" = :mes_p AND "AÑO" = :año_pasado
                    GROUP BY "ESTABLECIMIENTO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (mes_p, año_pasado,),
                )
                datos2 = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        if len(datos1) == 0 and len(datos2) == 0:
            entry_frecuencia_est["state"] = "normal"
            entry_frecuencia_est.delete(0, "end")
            entry_frecuencia_est.insert(0, "—")
            entry_frecuencia_est["state"] = "readonly"
            
            entry_frecuencia_est_mes_pasado["state"] = "normal"
            entry_frecuencia_est_mes_pasado.delete(0, "end")
            entry_frecuencia_est_mes_pasado.insert(0, "—")
            entry_frecuencia_est_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) == 0:
            entry_frecuencia_est["state"] = "normal"
            entry_frecuencia_est.delete(0, "end")
            entry_frecuencia_est.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia_est["state"] = "readonly"

            entry_frecuencia_est_mes_pasado["state"] = "normal"
            entry_frecuencia_est_mes_pasado.delete(0, "end")
            entry_frecuencia_est_mes_pasado.insert(0, "—")
            entry_frecuencia_est_mes_pasado["state"] = "readonly"
            
        elif len(datos1) == 0 and len(datos2) > 0:
            entry_frecuencia_est["state"] = "normal"
            entry_frecuencia_est.delete(0, "end")
            entry_frecuencia_est.insert(0, "—")
            entry_frecuencia_est["state"] = "readonly"

            entry_frecuencia_est_mes_pasado["state"] = "normal"
            entry_frecuencia_est_mes_pasado.delete(0, "end")
            entry_frecuencia_est_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_est_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) > 0:
            entry_frecuencia_est["state"] = "normal"
            entry_frecuencia_est.delete(0, "end")
            entry_frecuencia_est.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia_est["state"] = "readonly"

            entry_frecuencia_est_mes_pasado["state"] = "normal"
            entry_frecuencia_est_mes_pasado.delete(0, "end")
            entry_frecuencia_est_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_est_mes_pasado["state"] = "readonly"
            
        conexion1 = conectar_bd()
        if conexion1:
            try:
                cursor = conexion1.cursor()
                cursor.execute(
                    """
                    SELECT
                        E.NOMBRE_EST "ESTABLECIMIENTO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
                    WHERE "AÑO" = :año
                    GROUP BY "ESTABLECIMIENTO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (año,),
                )
                datos3 = cursor.fetchall()
                cursor.close()
                
                cerrar_bd(conexion1)
                
                if len(datos3) == 0:
                    entry_frecuencia_est_promedio["state"] = "normal"
                    entry_frecuencia_est_promedio.delete(0, "end")
                    entry_frecuencia_est_promedio.insert(0, "—")
                    entry_frecuencia_est_promedio["state"] = "readonly"
                    
                    entry_frecuencia_est_año["state"] = "normal"
                    entry_frecuencia_est_año.delete(0, "end")
                    entry_frecuencia_est_año.insert(0, "—")
                    entry_frecuencia_est_año["state"] = "readonly"
                else:
                    promedio = datos3[0][1]/mes
                    entry_frecuencia_est_promedio["state"] = "normal"
                    entry_frecuencia_est_promedio.delete(0, "end")
                    entry_frecuencia_est_promedio.insert(0, f"{año} | " + str(datos3[0][0]) + " | fi: " + str(round((promedio),2)) + "/mes")
                    entry_frecuencia_est_promedio["state"] = "readonly"
                    
                    entry_frecuencia_est_año["state"] = "normal"
                    entry_frecuencia_est_año.delete(0, "end")
                    entry_frecuencia_est_año.insert(0, f"{año} | " + str(datos3[0][0]) + " |  fi: " + str(datos3[0][1]) + "/año")
                    entry_frecuencia_est_año["state"] = "readonly"
                
            except Exception as ex:
                cerrar_bd(conexion1)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
        
        conexion2 = conectar_bd()
        if conexion2:
            try:
                cursor = conexion2.cursor()
                cursor.execute(
                    """
                    SELECT
                        E.NOMBRE_EST "ESTABLECIMIENTO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
                    WHERE "MES" = :mes AND "AÑO" = :año
                    GROUP BY "ESTABLECIMIENTO"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (mes, año,),
                )
                datos_ = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion2)
                
            except Exception as ex:
                cerrar_bd(conexion2)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        conexion3 = conectar_bd()
        if conexion3:
            try:
                cursor = conexion3.cursor()
                cursor.execute(
                    """
                    SELECT
                        E.NOMBRE_EST "ESTABLECIMIENTO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
                    WHERE "MES" = :mes_p AND "AÑO" = :año_pasado
                    GROUP BY "ESTABLECIMIENTO"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (mes_p, año_pasado,),
                )
                datos_p = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion3)
                
            except Exception as ex:
                cerrar_bd(conexion3)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        if len(datos_) == 0 and len(datos_p) == 0:
            entry_mas_gastos_est["state"] = "normal"
            entry_mas_gastos_est.delete(0, "end")
            entry_mas_gastos_est.insert(0, "—")
            entry_mas_gastos_est["state"] = "readonly"
            
            entry_mas_gastos_est_pasado["state"] = "normal"
            entry_mas_gastos_est_pasado.delete(0, "end")
            entry_mas_gastos_est_pasado.insert(0, "—")
            entry_mas_gastos_est_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) == 0:
            entry_mas_gastos_est["state"] = "normal"
            entry_mas_gastos_est.delete(0, "end")
            entry_mas_gastos_est.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos_est["state"] = "readonly"
            
            entry_mas_gastos_est_pasado["state"] = "normal"
            entry_mas_gastos_est_pasado.delete(0, "end")
            entry_mas_gastos_est_pasado.insert(0, "—")
            entry_mas_gastos_est_pasado["state"] = "readonly"
            
        elif len(datos_) == 0 and len(datos_p) > 0:
            entry_mas_gastos_est["state"] = "normal"
            entry_mas_gastos_est.delete(0, "end")
            entry_mas_gastos_est.insert(0, "—")
            entry_mas_gastos_est["state"] = "readonly"
            
            entry_mas_gastos_est_pasado["state"] = "normal"
            entry_mas_gastos_est_pasado.delete(0, "end")
            entry_mas_gastos_est_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_est_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) > 0:
            entry_mas_gastos_est["state"] = "normal"
            entry_mas_gastos_est.delete(0, "end")
            entry_mas_gastos_est.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos_est["state"] = "readonly"
            
            entry_mas_gastos_est_pasado["state"] = "normal"
            entry_mas_gastos_est_pasado.delete(0, "end")
            entry_mas_gastos_est_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_est_pasado["state"] = "readonly"
            
    else:
        mes_pasado = meses[mes-1]
        
        conexion = conectar_bd()
        if conexion:
            mes_p = mes-1
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    SELECT
                        E.NOMBRE_EST "ESTABLECIMIENTO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
                    WHERE "MES" = :mes_p AND "AÑO" = :año
                    GROUP BY "ESTABLECIMIENTO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (mes_p, año,),
                )
                datos2 = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                    
        if len(datos1) == 0 and len(datos2) == 0:
            entry_frecuencia_est["state"] = "normal"
            entry_frecuencia_est.delete(0, "end")
            entry_frecuencia_est.insert(0, "—")
            entry_frecuencia_est["state"] = "readonly"
            
            entry_frecuencia_est_mes_pasado["state"] = "normal"
            entry_frecuencia_est_mes_pasado.delete(0, "end")
            entry_frecuencia_est_mes_pasado.insert(0, "—")
            entry_frecuencia_est_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) == 0:
            entry_frecuencia_est["state"] = "normal"
            entry_frecuencia_est.delete(0, "end")
            entry_frecuencia_est.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia_est["state"] = "readonly"

            entry_frecuencia_est_mes_pasado["state"] = "normal"
            entry_frecuencia_est_mes_pasado.delete(0, "end")
            entry_frecuencia_est_mes_pasado.insert(0, "—")
            entry_frecuencia_est_mes_pasado["state"] = "readonly"
            
        elif len(datos1) == 0 and len(datos2) > 0:
            entry_frecuencia_est["state"] = "normal"
            entry_frecuencia_est.delete(0, "end")
            entry_frecuencia_est.insert(0, "—")
            entry_frecuencia_est["state"] = "readonly"

            entry_frecuencia_est_mes_pasado["state"] = "normal"
            entry_frecuencia_est_mes_pasado.delete(0, "end")
            entry_frecuencia_est_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_est_mes_pasado["state"] = "readonly"
            
        elif len(datos1) > 0 and len(datos2) > 0:
            entry_frecuencia_est["state"] = "normal"
            entry_frecuencia_est.delete(0, "end")
            entry_frecuencia_est.insert(0, f"{mes_actual} | " + str(datos1[0][0]) + " | fi: " + str(datos1[0][1]))
            entry_frecuencia_est["state"] = "readonly"

            entry_frecuencia_est_mes_pasado["state"] = "normal"
            entry_frecuencia_est_mes_pasado.delete(0, "end")
            entry_frecuencia_est_mes_pasado.insert(0, f"{mes_pasado} | " + str(datos2[0][0]) + " | fi: " + str(datos2[0][1]))
            entry_frecuencia_est_mes_pasado["state"] = "readonly"
                       
        conexion1 = conectar_bd()
        if conexion1:
            try:
                cursor = conexion1.cursor()
                cursor.execute(
                    """
                    SELECT
                        E.NOMBRE_EST "ESTABLECIMIENTO",
                        COUNT(*) "FRECUENCIA",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
                    WHERE "AÑO" = :año
                    GROUP BY "ESTABLECIMIENTO"
                    ORDER BY "FRECUENCIA" DESC, "GASTO TOTAL" DESC
                    """,
                    (año,),
                )
                datos3 = cursor.fetchall()
                cursor.close()
                
                cerrar_bd(conexion1)
                
                if len(datos3) == 0:
                    entry_frecuencia_est_promedio["state"] = "normal"
                    entry_frecuencia_est_promedio.delete(0, "end")
                    entry_frecuencia_est_promedio.insert(0, "—")
                    entry_frecuencia_est_promedio["state"] = "readonly"
                    
                    entry_frecuencia_est_año["state"] = "normal"
                    entry_frecuencia_est_año.delete(0, "end")
                    entry_frecuencia_est_año.insert(0, "—")
                    entry_frecuencia_est_año["state"] = "readonly"
                else:
                    promedio = datos3[0][1]/mes
                    entry_frecuencia_est_promedio["state"] = "normal"
                    entry_frecuencia_est_promedio.delete(0, "end")
                    entry_frecuencia_est_promedio.insert(0, f"{año} | " + str(datos3[0][0]) + " | fi: " + str(round((promedio),2)) + "/mes")
                    entry_frecuencia_est_promedio["state"] = "readonly"
                    
                    entry_frecuencia_est_año["state"] = "normal"
                    entry_frecuencia_est_año.delete(0, "end")
                    entry_frecuencia_est_año.insert(0, f"{año} | " + str(datos3[0][0]) + " |  fi: " + str(datos3[0][1]) + "/año")
                    entry_frecuencia_est_año["state"] = "readonly"
                
            except Exception as ex:
                cerrar_bd(conexion1)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
        
        conexion2 = conectar_bd()
        if conexion2:
            try:
                cursor = conexion2.cursor()
                cursor.execute(
                    """
                    SELECT
                        E.NOMBRE_EST "ESTABLECIMIENTO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.FECHA) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.FECHA) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
                    WHERE "MES" = :mes AND "AÑO" = :año
                    GROUP BY "ESTABLECIMIENTO"
                    ORDER BY "GASTO TOTAL" DESC
                    """,
                    (mes, año,),
                )
                datos_ = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion2)
                
            except Exception as ex:
                cerrar_bd(conexion2)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        conexion3 = conectar_bd()
        if conexion3:
            mes_p = mes-1
            try:
                cursor = conexion3.cursor()
                cursor.execute(
                    """
                    SELECT
                        E.NOMBRE_EST "ESTABLECIMIENTO",
                        SUM(G.MONTO) "GASTO TOTAL",
                        CAST(strftime('%m', G.fecha) AS INTEGER) "MES",
                        CAST(strftime('%Y', G.fecha) AS INTEGER) "AÑO"
                    FROM GASTOS G
                    JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
                    WHERE "MES" = :mes_p AND "AÑO" = :año
                    GROUP BY "ESTABLECIMIENTO"
                    ORDER BY "GASTO TOTAL" DESC

                    """,
                    (mes_p, año,),
                )
                datos_p = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion3)
                
            except Exception as ex:
                cerrar_bd(conexion3)
                messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
                
        if len(datos_) == 0 and len(datos_p) == 0:
            entry_mas_gastos_est["state"] = "normal"
            entry_mas_gastos_est.delete(0, "end")
            entry_mas_gastos_est.insert(0, "—")
            entry_mas_gastos_est["state"] = "readonly"
            
            entry_mas_gastos_est_pasado["state"] = "normal"
            entry_mas_gastos_est_pasado.delete(0, "end")
            entry_mas_gastos_est_pasado.insert(0, "—")
            entry_mas_gastos_est_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) == 0:
            entry_mas_gastos_est["state"] = "normal"
            entry_mas_gastos_est.delete(0, "end")
            entry_mas_gastos_est.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos_est["state"] = "readonly"
            
            entry_mas_gastos_est_pasado["state"] = "normal"
            entry_mas_gastos_est_pasado.delete(0, "end")
            entry_mas_gastos_est_pasado.insert(0, "—")
            entry_mas_gastos_est_pasado["state"] = "readonly"
            
        elif len(datos_) == 0 and len(datos_p) > 0:
            entry_mas_gastos_est["state"] = "normal"
            entry_mas_gastos_est.delete(0, "end")
            entry_mas_gastos_est.insert(0, "—")
            entry_mas_gastos_est["state"] = "readonly"
            
            entry_mas_gastos_est_pasado["state"] = "normal"
            entry_mas_gastos_est_pasado.delete(0, "end")
            entry_mas_gastos_est_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_est_pasado["state"] = "readonly"
            
        elif len(datos_) > 0 and len(datos_p) > 0:
            entry_mas_gastos_est["state"] = "normal"
            entry_mas_gastos_est.delete(0, "end")
            entry_mas_gastos_est.insert(0, f"{mes_actual} | " + str(datos_[0][0]) + " | S/. " + str(round(datos_[0][1],2)))
            entry_mas_gastos_est["state"] = "readonly"
            
            entry_mas_gastos_est_pasado["state"] = "normal"
            entry_mas_gastos_est_pasado.delete(0, "end")
            entry_mas_gastos_est_pasado.insert(0, f"{mes_pasado} | " + str(datos_p[0][0]) + " | S/. " + str(round(datos_p[0][1],2)))
            entry_mas_gastos_est_pasado["state"] = "readonly"

label_frecuencia_est = ttk.Label(tab_4, text="Frecuencia Mes Actual:")
label_frecuencia_est.grid(row=0, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia_est = ttk.Entry(tab_4, state="disabled", width=27)
entry_frecuencia_est.grid(row=1, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_frecuencia_est_mes_pasado = ttk.Label(tab_4, text="Frecuencia Mes Pasado:")
label_frecuencia_est_mes_pasado.grid(row=0, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia_est_mes_pasado = ttk.Entry(tab_4, state="disabled", width=27)
entry_frecuencia_est_mes_pasado.grid(row=1, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_frecuencia_est_promedio = ttk.Label(tab_4, text="Frecuencia Mes Promedio:")
label_frecuencia_est_promedio.grid(row=2, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia_est_promedio = ttk.Entry(tab_4, state="disabled", width=27)
entry_frecuencia_est_promedio.grid(row=3, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_frecuencia_est_año = ttk.Label(tab_4, text="Frecuencia Año Actual:")
label_frecuencia_est_año.grid(row=2, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_frecuencia_est_año = ttk.Entry(tab_4, state="disabled", width=27)
entry_frecuencia_est_año.grid(row=3, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_mas_gastos_est = ttk.Label(tab_4, text="+ Gastos Mes Actual:")
label_mas_gastos_est.grid(row=4, column=0, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_mas_gastos_est = ttk.Entry(tab_4, state="disabled", width=27)
entry_mas_gastos_est.grid(row=5, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")

label_mas_gastos_est_pasado = ttk.Label(tab_4, text="+ Gastos Mes Pasado:")
label_mas_gastos_est_pasado.grid(row=4, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
entry_mas_gastos_est_pasado = ttk.Entry(tab_4, state="disabled", width=27)
entry_mas_gastos_est_pasado.grid(row=5, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")

notebook.pack(expand=True, fill="both", padx=5, pady=0)

separador = ttk.Separator(frame_reporte)
separador.grid(row=0, column=1, padx=(15, 15), pady=(5, 10), sticky="nsew")


# FRAME FACTURACIÓN #
frame_facturacion = ttk.LabelFrame(frame_reporte, text="Periodo de Facturación")
frame_facturacion.grid(row=0, column=2, padx=(5, 5), pady=(0, 10), sticky="nsew")

label_inicio = ttk.Label(frame_facturacion, text="Fecha Inicio:")
label_inicio.grid(row=0, column=0, padx=(15, 15), pady=(5, 0), sticky="nsew")
entry_inicio = ttk.Entry(frame_facturacion, state="disabled", width=10)
entry_inicio.grid(row=1, column=0, padx=(15, 15), pady=(0, 15), sticky="nsew")


label_cierre = ttk.Label(frame_facturacion, text="Fecha Fin:")
label_cierre.grid(row=0, column=1, padx=(0, 15), pady=(5, 0), sticky="nsew")
entry_cierre = ttk.Entry(frame_facturacion, state="disabled", width=10)
entry_cierre.grid(row=1, column=1, padx=(0, 15), pady=(0, 15), sticky="nsew")


label_pago = ttk.Label(frame_facturacion, text="Fecha Pago:")
label_pago.grid(row=2, column=0, padx=(15, 15), pady=(5, 0), sticky="nsew")
entry_pago = ttk.Entry(frame_facturacion, state="disabled", width=10)
entry_pago.grid(row=3, column=0, padx=(15, 15), pady=(0, 15), sticky="nsew")


label_total = ttk.Label(frame_facturacion, text="Pago del Mes:", font=("Arial", 10, "bold"))
label_total.grid(row=2, column=1, padx=(0, 15), pady=(5, 0), sticky="nsew")
entry_total = ttk.Entry(frame_facturacion, state="disabled", width=10)
entry_total.grid(row=3, column=1, padx=(0, 15), pady=(0, 15), sticky="nsew")


label_promedio = ttk.Label(frame_facturacion, text="Pago Promedio:")
label_promedio.grid(row=4, column=0, padx=(15, 15), pady=(5, 0), sticky="nsew")
entry_promedio = ttk.Entry(frame_facturacion, state="disabled", width=10)
entry_promedio.grid(row=5, column=0, padx=(15, 15), pady=(0, 15), sticky="nsew")


boton_generar_reporte = ttk.Button(frame_facturacion, text="Excel")
boton_generar_reporte.grid(row=5, column=1, padx=(0, 15), pady=(0, 15), sticky="n")


# FRAME CONFIGURACIÓN #
frame_config = ttk.LabelFrame(frame, text="Configuración")
frame_config.grid(row=2, column=2, padx=(5, 5), pady=(0, 5), sticky="nsew")

boton_tarjeta = ttk.Button(frame_config, text="Tarjetas", command=lambda: ventana_tarjetas(style))
boton_tarjeta.grid(row=0, column=0, columnspan=2, padx=(15, 15), pady=(5, 10), sticky="nsew")

boton_usuario = ttk.Button(frame_config, text="Usuarios", command=lambda: ventana_usuarios(style))
boton_usuario.grid(row=1, column=0, columnspan=2, padx=(15, 15), pady=(5, 10), sticky="nsew")

boton_banco = ttk.Button(frame_config, text="Bancos", command=lambda: ventana_bancos(style))
boton_banco.grid(row=2, column=0, columnspan=2, padx=(15, 15), pady=(5, 10), sticky="nsew")

boton_establecimiento = ttk.Button(frame_config, text="Establecimientos", command=lambda: ventana_establecimientos(style))
boton_establecimiento.grid(row=3, column=0, columnspan=2, padx=(15, 15), pady=(5, 10), sticky="nsew")

separador = ttk.Separator(frame_config)
separador.grid(row=4, column=0, columnspan=2, padx=(15, 15), pady=(3, 3), sticky="nsew")

label_switch = ttk.Label(frame_config, text="Tema Claro/Oscuro")
label_switch.grid(row=5, column=0, padx=(15, 0), pady=(5, 10), sticky="nsew")
# Switch
switch = ttk.Checkbutton(frame_config, style="Switch", command=switch_callback)
switch.grid(row=5, column=1, padx=(10, 15), pady=(5, 10), sticky="nsew")


# VENTANA USUARIOS #
def ventana_usuarios(parent_style):
    ventana_usuarios = tk.Toplevel()
    ventana_usuarios.title("Configuración de Usuarios")
    ventana_usuarios.resizable(0, 0)
    
    # Corrige el tamaño del treeview
    if treeview:
        treeview.destroy()
    tree()
    actualizar()
    
    def seleccion_usuarios(event):
        seleccion = treeview_usuarios.selection()

        if seleccion:
            item = seleccion[0]
            usuario = treeview_usuarios.item(item, "values")

            entry_user.delete(0, tk.END)
            entry_user.insert(0, usuario[1])
    
    def registrar_usuario():
        usuario = entry_user.get()
        if usuario == "":
            messagebox.showwarning("Error de registro", "ERROR: FALTAN COMPLETAR ESPACIOS OBLIGATORIOS.")
            return
        else:
            id = generar_id_usuario()
        
            conexion = conectar_bd()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    cursor.execute(
                        """
                        INSERT INTO USUARIOS (usuario, nombre_usuario) VALUES (:id, :usuario)
                        """, 
                        (
                            id, 
                            usuario
                        )
                    )
                    conexion.commit()
                    cursor.close()
                    cerrar_bd(conexion)
                    tabla_usuarios()
                    
                    entry_user.delete(0, tk.END)
                    
                    messagebox.showinfo("Usuario Registrado", "El usuario se registro correctamente.")

                except Exception as ex:
                    cerrar_bd(conexion)
                    messagebox.showerror("Error", "Error al insertar datos: " + str(ex))
    
    def editar_usuario():
        seleccion = treeview_usuarios.selection()
        if len(seleccion) == 0:
            messagebox.showwarning("Sin Selección", "ERROR: SE DEBE SELECCIONAR UNA FILA.")
            return
        respuesta = messagebox.askyesno("Confirmar Edición", "ADVERTENCIA: Modificar un usuario afecta toda la información relacionada a este. ¿Deseas continuar?")
        if respuesta:
            editar_usuario_seleccionado(seleccion)

    def editar_usuario_seleccionado(seleccion):
        item_values = treeview_usuarios.item(seleccion, "values")
        id = item_values[0]
        usuario = entry_user.get()
        
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    UPDATE USUARIOS
                    SET
                        NOMBRE_USUARIO = :usuario
                    WHERE USUARIO = :id
                    """,
                    (usuario, id)
                )
                conexion.commit()
                cursor.close()
                cerrar_bd(conexion)
                messagebox.showinfo("Cambios Guardados", "El usuario se modificó correctamente.",)
                tabla_usuarios()
                
                entry_user.delete(0, tk.END)

            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al modificar usuario: " + str(ex))
                
    def eliminar_usuario():
        seleccion = treeview_usuarios.selection()
        if len(seleccion) == 0:
            messagebox.showwarning("Sin selección", "ERROR: SE DEBE SELECCIONAR UNA FILA.")
            return
        respuesta = messagebox.askyesno("Confirmar Eliminación", "ADVERTENCIA: Eliminar un usuario afecta toda la información relacionada a este. ¿Deseas continuar?")
        if respuesta:
            eliminar_usuario_seleccionado(seleccion)

    def eliminar_usuario_seleccionado(seleccion):
        item_values = treeview_usuarios.item(seleccion, "values")
        id = item_values[0]

        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    DELETE FROM GASTOS WHERE USUARIOS_USUARIO = :id
                    """, 
                    (id,)
                )
                conexion.commit()
                cursor.close()
                
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    DELETE FROM TARJETAS WHERE USUARIOS_USUARIO = :id
                    """, 
                    (id,)
                )
                conexion.commit()
                cursor.close()
                
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    DELETE FROM USUARIOS WHERE USUARIO = :id
                    """, 
                    (id,)
                )
                conexion.commit()
                cursor.close()
                
                cerrar_bd(conexion)

                treeview_usuarios.delete(seleccion)
                messagebox.showinfo("Eliminación Confirmada", "El usuario se eliminó correctamente.",)
                tabla_usuarios()

            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al eliminar usuario: " + str(ex))
    
    
    ventana_style = ttk.Style(ventana_usuarios)
    ventana_style.theme_use(parent_style.theme_use())
    
    frame = ttk.Frame(ventana_usuarios)
    frame.pack()
    
    label_user = ttk.Label(frame, text="Nombre de usuario:")
    label_user.grid(row=0, column=0, padx=(15, 5), pady=(12, 5), sticky="nsew")

    entry_user = ttk.Entry(frame, state="normal")
    entry_user.grid(row=1, column=0, padx=(15, 5), pady=(0, 5), sticky="nsew")
    
    separador = ttk.Separator(frame)
    separador.grid(row=2, column=0, padx=(15, 5), pady=(5, 5), sticky="nsew")
    
    boton_crear_user = ttk.Button(frame, text="Crear Usuario", command=registrar_usuario)
    boton_crear_user.grid(row=3, column=0, padx=(15, 5), pady=(5, 5), sticky="nsew")

    boton_editar_user = ttk.Button(frame, text="Editar Usuario", command=editar_usuario)
    boton_editar_user.grid(row=4, column=0, padx=(15, 5), pady=(5, 5), sticky="nsew")

    boton_eliminar_user = ttk.Button(frame, text="Eliminar Usuario", command=eliminar_usuario)
    boton_eliminar_user.grid(row=5, column=0, padx=(15, 5), pady=(5, 12), sticky="nsew")
    
    separador = ttk.Separator(frame)
    separador.grid(row=0, column=1, rowspan=10, padx=(5, 5), pady=(5, 5), sticky="nsew")
    
    def tree_user():
        frame_tabla_usuarios = ttk.Frame(frame)
        frame_tabla_usuarios.grid(row=0, column=2, rowspan=10, padx=(5, 15), pady=(5, 5), sticky="nsew")

        scroll_tabla = ttk.Scrollbar(frame_tabla_usuarios)
        scroll_tabla.pack(side="right", fill="y")
        
        encabezados = ("ID", "USUARIO")
        global treeview_usuarios
        treeview_usuarios = ttk.Treeview(
            frame_tabla_usuarios,
            show="headings",
            yscrollcommand=scroll_tabla.set,
            columns=encabezados,
            height=7,
        )
        treeview_usuarios.column("ID", width=20)
        treeview_usuarios.column("USUARIO", width=100)

        for encabezado in encabezados:
            treeview_usuarios.heading(encabezado, text=encabezado)

        treeview_usuarios.pack()
        treeview_usuarios.configure()
        scroll_tabla.configure(command=treeview_usuarios.yview)
        treeview_usuarios.bind("<ButtonRelease-1>", seleccion_usuarios)
        
    def tabla_usuarios():
        treeview_usuarios.delete(*treeview_usuarios.get_children())
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("""SELECT * FROM USUARIOS""")
                datos = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion)
                
                for fila in datos:
                    treeview_usuarios.insert("", "end", values=fila)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al insertar datos: " + str(ex))
                
    def cerrar_ventana_usuarios():
        ventana_usuarios.destroy()
        root.deiconify()
        root.grab_set()
        actualizar_usuarios()
        actualizar_usuarios_filtro()
        actualizar()
        
    ventana_usuarios.protocol("WM_DELETE_WINDOW", cerrar_ventana_usuarios)
    ventana_usuarios.grab_set()
    
    tree_user()
    tabla_usuarios()
    center_window(ventana_usuarios)
    
    ventana_usuarios.mainloop()
    

# VENTANA BANCOS #
def ventana_bancos(parent_style):
    ventana_bancos = tk.Toplevel()
    ventana_bancos.title("Configuración de bancos")
    ventana_bancos.resizable(0, 0)
    
    # Corrige el tamaño del treeview
    if treeview:
        treeview.destroy()
    tree()
    actualizar()
    
    def seleccion_bancos(event):
        seleccion = treeview_bancos.selection()
        
        if seleccion:
            item = seleccion[0]
            banco = treeview_bancos.item(item, "values")
            
            entry_bank.delete(0, tk.END)
            entry_bank.insert(0, banco[1])
    
    def registrar_banco():
        banco = entry_bank.get()
        if banco == "":
            messagebox.showwarning("Error de registro", "ERROR: FALTAN COMPLETAR ESPACIOS OBLIGATORIOS.")
            return
        else:
            id = generar_id_banco()
        
            conexion = conectar_bd()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    cursor.execute(
                        """
                        INSERT INTO BANCOS (banco, nombre_banco) VALUES (:id, :banco)
                        """, 
                        (
                            id, 
                            banco
                        )
                    )
                    conexion.commit()
                    cursor.close()
                    cerrar_bd(conexion)
                    tabla_bancos()
                    
                    entry_bank.delete(0, tk.END)
                    
                    messagebox.showinfo("banco Registrado", "El banco se registro correctamente.")

                except Exception as ex:
                    cerrar_bd(conexion)
                    messagebox.showerror("Error", "Error al insertar datos: " + str(ex))
                    
    def editar_banco():
        seleccion = treeview_bancos.selection()
        if len(seleccion) == 0:
            messagebox.showwarning("Sin Selección", "ERROR: SE DEBE SELECCIONAR UNA FILA.")
            return
        respuesta = messagebox.askyesno("Confirmar Edición", "ADVERTENCIA: Modificar un banco afecta toda la información relacionada a este. ¿Deseas continuar?")
        if respuesta:
            editar_banco_seleccionado(seleccion)

    def editar_banco_seleccionado(seleccion):
        item_values = treeview_bancos.item(seleccion, "values")
        id = item_values[0]
        banco = entry_bank.get()
        
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    UPDATE BANCOS
                    SET
                        NOMBRE_BANCO = :banco
                    WHERE BANCO = :id
                    """,
                    (banco, id)
                )
                conexion.commit()
                cursor.close()
                cerrar_bd(conexion)
                messagebox.showinfo("Cambios Guardados", "El banco se modificó correctamente.",)
                tabla_bancos()
                
                entry_bank.delete(0, tk.END)

            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al modificar banco: " + str(ex))
                
    def eliminar_banco():
        seleccion = treeview_bancos.selection()
        if len(seleccion) == 0:
            messagebox.showwarning("Sin selección", "ERROR: SE DEBE SELECCIONAR UNA FILA.")
            return
        respuesta = messagebox.askyesno("Confirmar Eliminación", "ADVERTENCIA: Eliminar un banco afecta toda la información relacionada a este. ¿Deseas continuar?")
        if respuesta:
            eliminar_banco_seleccionado(seleccion)
            
    def eliminar_banco_seleccionado(seleccion):
        item_values = treeview_bancos.item(seleccion, "values")
        id = item_values[0]
        
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    DELETE FROM GASTOS
                    WHERE TARJETAS_NRO_TARJETA IN (
                        SELECT G.TARJETAS_NRO_TARJETA
                        FROM GASTOS G
                        JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
                        JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                        WHERE B.BANCO = :id
                    )
                    """, 
                    (id)
                )
                conexion.commit()
                cursor.close()
                
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    DELETE FROM TARJETAS WHERE BANCOS_BANCO = :id
                    """, 
                    (id)
                )
                conexion.commit()
                cursor.close()
                
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    DELETE FROM BANCOS WHERE BANCO = :id
                    """, 
                    (id)
                )
                conexion.commit()
                cursor.close()
                
                cerrar_bd(conexion)

                treeview_bancos.delete(seleccion)
                messagebox.showinfo("Eliminación Confirmada", "El banco se eliminó correctamente.")
                tabla_bancos()

            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al eliminar banco: " + str(ex))
                
    ventana_style = ttk.Style(ventana_bancos)
    ventana_style.theme_use(parent_style.theme_use())
    
    frame = ttk.Frame(ventana_bancos)
    frame.pack()
    
    label_bank = ttk.Label(frame, text="Nombre del banco:")
    label_bank.grid(row=0, column=0, padx=(15, 5), pady=(12, 5), sticky="nsew")
    entry_bank = ttk.Entry(frame, state="normal")
    entry_bank.grid(row=1, column=0, padx=(15, 5), pady=(0, 5), sticky="nsew")
    
    separador = ttk.Separator(frame)
    separador.grid(row=2, column=0, padx=(15, 5), pady=(5, 5), sticky="nsew")
    
    boton_crear_bank = ttk.Button(frame, text="Crear banco", command=registrar_banco)
    boton_crear_bank.grid(row=3, column=0, padx=(15, 5), pady=(5, 5), sticky="nsew")

    boton_editar_bank = ttk.Button(frame, text="Editar banco", command=editar_banco)
    boton_editar_bank.grid(row=4, column=0, padx=(15, 5), pady=(5, 5), sticky="nsew")

    boton_eliminar_bank = ttk.Button(frame, text="Eliminar banco", command=eliminar_banco)
    boton_eliminar_bank.grid(row=5, column=0, padx=(15, 5), pady=(5, 12), sticky="nsew")
    
    separador = ttk.Separator(frame)
    separador.grid(row=0, column=1, rowspan=10, padx=(5, 5), pady=(5, 5), sticky="nsew")
    
    def tree_bank():
        frame_tabla_bancos = ttk.Frame(frame)
        frame_tabla_bancos.grid(row=0, column=2, rowspan=10, padx=(5, 15), pady=(5, 5), sticky="nsew")
        
        scroll_tabla = ttk.Scrollbar(frame_tabla_bancos)
        scroll_tabla.pack(side="right", fill="y")
        
        encabezados = ("ID", "BANCO")
        global treeview_bancos
        treeview_bancos = ttk.Treeview(
            frame_tabla_bancos,
            show="headings",
            yscrollcommand=scroll_tabla.set,
            columns=encabezados,
            height=7,
        )
        treeview_bancos.column("ID", width=20)
        treeview_bancos.column("BANCO", width=150)

        for encabezado in encabezados:
            treeview_bancos.heading(encabezado, text=encabezado)
            
        treeview_bancos.pack()
        treeview_bancos.configure()
        scroll_tabla.configure(command=treeview_bancos.yview)
        treeview_bancos.bind("<ButtonRelease-1>", seleccion_bancos)
        
    def tabla_bancos():
        treeview_bancos.delete(*treeview_bancos.get_children())
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("""SELECT * FROM BANCOS""")
                datos = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion)
                
                for fila in datos:
                    treeview_bancos.insert("", "end", values=fila)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al insertar datos: " + str(ex))
                
    def cerrar_ventana_bancos():
        ventana_bancos.destroy()
        root.deiconify()
        root.grab_set()
        actualizar()
        
    ventana_bancos.protocol("WM_DELETE_WINDOW", cerrar_ventana_bancos)
    ventana_bancos.grab_set()
    
    tree_bank()
    tabla_bancos()
    center_window(ventana_bancos)
    
    ventana_bancos.mainloop()


# VENTANA ESTABLECIMIENTOS #
def ventana_establecimientos(parent_style):
    ventana_establecimientos = tk.Toplevel()
    ventana_establecimientos.title("Configuración de establecimientos")
    ventana_establecimientos.resizable(0, 0)
    
    # Corrige el tamaño del treeview
    if treeview:
        treeview.destroy()
    tree()
    actualizar()
    
    def seleccion_establecimientos(event):
        seleccion = treeview_establecimientos.selection()

        if seleccion:
            item = seleccion[0]
            establecimiento = treeview_establecimientos.item(item, "values")
            
            entry_estab.delete(0, tk.END)
            entry_estab.insert(0, establecimiento[1])
            
    def registrar_establecimiento():
        establecimiento = entry_estab.get()
        if establecimiento == "":
            messagebox.showwarning("Error de registro", "ERROR: FALTAN COMPLETAR ESPACIOS OBLIGATORIOS.")
            return
        else:
            id = generar_id_establecimiento()
        
            conexion = conectar_bd()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    cursor.execute(
                        """
                        INSERT INTO ESTABLECIMIENTOS (establecimiento, nombre_est) VALUES (:id, :establecimiento)
                        """, 
                        (
                            id, 
                            establecimiento
                        )
                    )
                    conexion.commit()
                    cursor.close()
                    cerrar_bd(conexion)
                    tabla_establecimientos()
                    
                    entry_estab.delete(0, tk.END)
                    
                    messagebox.showinfo("establecimiento Registrado", "El establecimiento se registro correctamente.")
                    
                except Exception as ex:
                    cerrar_bd(conexion)
                    messagebox.showerror("Error", "Error al insertar datos: " + str(ex))
                    
    def editar_establecimiento():
        seleccion = treeview_establecimientos.selection()
        if len(seleccion) == 0:
            messagebox.showwarning("Sin Selección", "ERROR: SE DEBE SELECCIONAR UNA FILA.")
            return
        respuesta = messagebox.askyesno("Confirmar Edición", "ADVERTENCIA: Modificar un establecimiento afecta toda la información relacionada a este. ¿Deseas continuar?")
        if respuesta:
            editar_establecimiento_seleccionado(seleccion)
            
    def editar_establecimiento_seleccionado(seleccion):
        item_values = treeview_establecimientos.item(seleccion, "values")
        id = item_values[0]
        establecimiento = entry_estab.get()
        
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    UPDATE ESTABLECIMIENTOS
                    SET
                        NOMBRE_EST = :establecimiento
                    WHERE ESTABLECIMIENTO = :id
                    """,
                    (establecimiento, id)
                )
                conexion.commit()
                cursor.close()
                cerrar_bd(conexion)
                messagebox.showinfo("Cambios Guardados", "El establecimiento se modificó correctamente.",)
                tabla_establecimientos()
                
                entry_estab.delete(0, tk.END)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al modificar establecimiento: " + str(ex))
                
    def eliminar_establecimiento():
        seleccion = treeview_establecimientos.selection()
        if len(seleccion) == 0:
            messagebox.showwarning("Sin selección", "ERROR: SE DEBE SELECCIONAR UNA FILA.")
            return
        respuesta = messagebox.askyesno("Confirmar Eliminación", "ADVERTENCIA: Eliminar un establecimiento afecta toda la información relacionada a este. ¿Deseas continuar?")
        if respuesta:
            eliminar_establecimiento_seleccionado(seleccion)
            
    def eliminar_establecimiento_seleccionado(seleccion):
        item_values = treeview_establecimientos.item(seleccion, "values")
        id = item_values[0]
        
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    DELETE FROM GASTOS WHERE ESTABLECIMIENTOS_ESTABLECIMIENTO = :id
                    """, 
                    (id,)
                )
                conexion.commit()
                cursor.close()

                cursor = conexion.cursor()
                cursor.execute(
                    """
                    DELETE FROM ESTABLECIMIENTOS WHERE ESTABLECIMIENTO = :id
                    """, 
                    (id,)
                )
                conexion.commit()
                cursor.close()
                
                cerrar_bd(conexion)

                treeview_establecimientos.delete(seleccion)
                messagebox.showinfo("Eliminación Confirmada", "El establecimiento se eliminó correctamente.",)
                tabla_establecimientos()

            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al eliminar establecimiento: " + str(ex))
                
    ventana_style = ttk.Style(ventana_establecimientos)
    ventana_style.theme_use(parent_style.theme_use())
    
    frame = ttk.Frame(ventana_establecimientos)
    frame.pack()
    
    label_estab = ttk.Label(frame, text="Nombre del establecimiento:")
    label_estab.grid(row=0, column=0, padx=(15, 5), pady=(12, 5), sticky="nsew")
    entry_estab = ttk.Entry(frame, state="normal")
    entry_estab.grid(row=1, column=0, padx=(15, 5), pady=(0, 5), sticky="nsew")
    
    separador = ttk.Separator(frame)
    separador.grid(row=2, column=0, padx=(15, 5), pady=(5, 5), sticky="nsew")
    
    boton_crear_estab = ttk.Button(frame, text="Crear establecimiento", command=registrar_establecimiento)
    boton_crear_estab.grid(row=3, column=0, padx=(15, 5), pady=(5, 5), sticky="nsew")

    boton_editar_estab = ttk.Button(frame, text="Editar establecimiento", command=editar_establecimiento)
    boton_editar_estab.grid(row=4, column=0, padx=(15, 5), pady=(5, 5), sticky="nsew")

    boton_eliminar_estab = ttk.Button(frame, text="Eliminar establecimiento", command=eliminar_establecimiento)
    boton_eliminar_estab.grid(row=5, column=0, padx=(15, 5), pady=(5, 12), sticky="nsew")
    
    separador = ttk.Separator(frame)
    separador.grid(row=0, column=1, rowspan=10, padx=(5, 5), pady=(5, 5), sticky="nsew")
    
    def tree_estab():
        frame_tabla_establecimientos = ttk.Frame(frame)
        frame_tabla_establecimientos.grid(row=0, column=2, rowspan=10, padx=(5, 15), pady=(5, 5), sticky="nsew")

        scroll_tabla = ttk.Scrollbar(frame_tabla_establecimientos)
        scroll_tabla.pack(side="right", fill="y")
        
        encabezados = ("ID", "ESTABLECIMIENTO")
        global treeview_establecimientos
        treeview_establecimientos = ttk.Treeview(
            frame_tabla_establecimientos,
            show="headings",
            yscrollcommand=scroll_tabla.set,
            columns=encabezados,
            height=7,
        )
        treeview_establecimientos.column("ID", width=20)
        treeview_establecimientos.column("ESTABLECIMIENTO", width=150)

        for encabezado in encabezados:
            treeview_establecimientos.heading(encabezado, text=encabezado)
            
        treeview_establecimientos.pack()
        treeview_establecimientos.configure()
        scroll_tabla.configure(command=treeview_establecimientos.yview)
        treeview_establecimientos.bind("<ButtonRelease-1>", seleccion_establecimientos)
        
    def tabla_establecimientos():
        treeview_establecimientos.delete(*treeview_establecimientos.get_children())
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("""SELECT * FROM ESTABLECIMIENTOS""")
                datos = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion)
                
                for fila in datos:
                    treeview_establecimientos.insert("", "end", values=fila)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al insertar datos: " + str(ex))
                
    def cerrar_ventana_establecimientos():
        ventana_establecimientos.destroy()
        root.deiconify()
        root.grab_set()
        actualizar_establecimientos()
        actualizar()
        
    ventana_establecimientos.protocol("WM_DELETE_WINDOW", cerrar_ventana_establecimientos)
    ventana_establecimientos.grab_set()
    
    tree_estab()
    tabla_establecimientos()
    center_window(ventana_establecimientos)
    
    ventana_establecimientos.mainloop()


# VENTANA TARJETAS #
def ventana_tarjetas(parent_style):
    ventana_tarjetas = tk.Toplevel()
    ventana_tarjetas.title("Configuración de tarjetas")
    ventana_tarjetas.resizable(0, 0)
    
    if treeview:
        treeview.destroy()
    tree()
    actualizar()
    
    def seleccion_tarjetas(event):
        seleccion = treeview_tarjetas.selection()
        
        if seleccion:
            item = seleccion[0]
            tarjeta = treeview_tarjetas.item(item, "values")
            
            entry_card.delete(0, tk.END)
            entry_card.insert(0, tarjeta[0])
            if tarjeta[1] == "Titular":
                a.set(1)
            elif tarjeta[1] == "Adicional":
                a.set(2)
            entry_cierre.delete(0, tk.END)
            entry_cierre.insert(0, tarjeta[2])
            entry_venci.delete(0, tk.END)
            entry_venci.insert(0, tarjeta[3])
            selected_usuario
            if tarjeta[4] in combobox_usuarios["values"]:
                selected_usuario.set(tarjeta[4])
                index = combobox_usuarios["values"].index(tarjeta[4])
                combobox_usuarios.current(index)
            selected_banco
            if tarjeta[5] in combobox_bancos["values"]:
                selected_banco.set(tarjeta[5])
                index = combobox_bancos["values"].index(tarjeta[5])
                combobox_bancos.current(index)
    
    def obtener_user_id():
        usuario = combobox_usuarios.get()
        consulta = """
            SELECT 
                USUARIO
            FROM USUARIOS
            WHERE NOMBRE_USUARIO = :usuario
            """
        parametros = {"usuario": usuario}
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(consulta, parametros)
                result = cursor.fetchall()
                cursor.close()
                return result[0][0]

            except Exception as ex:
                print("Error al ejecutar la consulta:", ex)
                
    def obtener_banco_id():
        banco = combobox_bancos.get()
        consulta = """
            SELECT 
                BANCO
            FROM BANCOS
            WHERE NOMBRE_BANCO = :banco
            """
        parametros = {"banco": banco}
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(consulta, parametros)
                result = cursor.fetchall()
                cursor.close()
                return result[0][0]
            
            except Exception as ex:
                print("Error al ejecutar la consulta:", ex)
    
    def registrar_tarjeta():
        usuario = combobox_usuarios.get()
        banco = combobox_bancos.get()
        tarjeta = entry_card.get()
        if a.get() == 1:
            tipo = "Titular"
        elif a.get() == 2:
            tipo = "Adicional"
        cierre = entry_cierre.get()
        vencimiento = entry_venci.get()
        
        if tarjeta == "" or usuario == "Seleccionar" or banco == "Seleccionar" or cierre == "" or vencimiento == "":
            messagebox.showwarning("Error de registro", "ERROR: FALTAN COMPLETAR ESPACIOS OBLIGATORIOS.")
            return
        elif len(tarjeta) != 4 or not tarjeta.isdigit():
            messagebox.showwarning("Error de registro", "ERROR: El nro de tarjeta de ser un número entero de 4 dígitos.")
            return
        elif cierre.count('.') == 1 and all(char.isdigit() or char == '.' for char in cierre):
            messagebox.showwarning("Error de registro", "ERROR: El cierre de facturación debe ser un número entero.")
            return
        elif vencimiento.count('.') == 1 and all(char.isdigit() or char == '.' for char in vencimiento):
            messagebox.showwarning("Error de registro", "ERROR: El día de vencimiento debe ser un número entero.")
            return
        elif int(cierre)>27 or int(cierre) <=0:
            messagebox.showwarning("Error de registro", "ERROR: El cierre de facturación debe estar entre 1 y 27.")
            return
        elif int(vencimiento)>27 or int(vencimiento) <=0:
            messagebox.showwarning("Error de registro", "ERROR: El día de vencimiento debe estar entre 1 y 27.")
            return
        else:
            usuarios_usuario = obtener_user_id()
            bancos_banco = obtener_banco_id()
            
            conexion = conectar_bd()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    cursor.execute(
                        """
                        INSERT INTO TARJETAS (NRO_TARJETA, TIPO, CIERRE, VENCIMIENTO, USUARIOS_USUARIO, BANCOS_BANCO) VALUES (:tarjeta, :tipo, :cierre, :vencimiento, :usuarios_usuario, :bancos_banco)
                        """, 
                        (
                            tarjeta, 
                            tipo,
                            cierre,
                            vencimiento,
                            usuarios_usuario,
                            bancos_banco
                        )
                    )
                    conexion.commit()
                    cursor.close()
                    cerrar_bd(conexion)
                    tabla_tarjetas()
                    
                    entry_card.delete(0, tk.END)
                    
                    messagebox.showinfo("tarjeta Registrado", "La tarjeta se registro correctamente.")
                    
                except Exception as ex:
                    cerrar_bd(conexion)
                    messagebox.showerror("Error", "Error al insertar datos: " + str(ex))
                    
    def editar_tarjeta():
        seleccion = treeview_tarjetas.selection()
        if len(seleccion) == 0:
            messagebox.showwarning("Sin Selección", "ERROR: SE DEBE SELECCIONAR UNA FILA.")
            return
        respuesta = messagebox.askyesno("Confirmar Edición", "ADVERTENCIA: Modificar una tarjeta afecta toda la información relacionada a esta. ¿Deseas continuar?")
        if respuesta:
            editar_tarjeta_seleccionado(seleccion)
            
    def editar_tarjeta_seleccionado(seleccion):
        item_values = treeview_tarjetas.item(seleccion, "values")
        tarjeta = item_values[0]
        nueva_tarjeta = entry_card.get()
        if a.get() == 1:
            tipo = "Titular"
        elif a.get() == 2:
            tipo = "Adicional"
        cierre = entry_cierre.get()
        vencimiento = entry_venci.get()
        usuarios_usuario = obtener_user_id()
        bancos_banco = obtener_banco_id()
        
        if nueva_tarjeta == "" or cierre == "" or vencimiento == "":
            messagebox.showwarning("Error de registro", "ERROR: FALTAN COMPLETAR ESPACIOS OBLIGATORIOS.")
            return
        elif len(nueva_tarjeta) != 4 or not nueva_tarjeta.isdigit():
            messagebox.showwarning("Error de registro", "ERROR: El nro de tarjeta de ser un número entero de 4 dígitos.")
            return
        elif cierre.count('.') == 1 and all(char.isdigit() or char == '.' for char in cierre):
            messagebox.showwarning("Error de registro", "ERROR: El cierre de facturación debe ser un número entero.")
            return
        elif vencimiento.count('.') == 1 and all(char.isdigit() or char == '.' for char in vencimiento):
            messagebox.showwarning("Error de registro", "ERROR: El día de vencimiento debe ser un número entero.")
            return
        elif int(cierre)>27 or int(cierre) <=0:
            messagebox.showwarning("Error de registro", "ERROR: El cierre de facturación debe estar entre 1 y 27.")
            return
        elif int(vencimiento)>27 or int(vencimiento) <=0:
            messagebox.showwarning("Error de registro", "ERROR: El día de vencimiento debe estar entre 1 y 27.")
            return
            
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    UPDATE TARJETAS
                    SET
                        NRO_TARJETA = :nueva_tarjeta,
                        TIPO = :tipo,
                        CIERRE = :cierre,
                        VENCIMIENTO = :vencimiento,
                        USUARIOS_USUARIO = :usuarios_usuario,
                        BANCOS_BANCO = :bancos_banco
                    WHERE NRO_TARJETA = :tarjeta
                    """,
                    (
                        nueva_tarjeta,
                        tipo,
                        cierre,
                        vencimiento,
                        usuarios_usuario,
                        bancos_banco,
                        tarjeta
                    )
                )
                conexion.commit()
                cursor.close()
                
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    UPDATE GASTOS
                    SET
                        USUARIOS_USUARIO = :usuarios_usuario,
                        TARJETAS_NRO_TARJETA = :nueva_tarjeta
                    WHERE TARJETAS_NRO_TARJETA = :tarjeta
                    """,
                    (
                        usuarios_usuario,
                        nueva_tarjeta,
                        tarjeta
                    )
                )
                conexion.commit()
                cursor.close()
                
                cerrar_bd(conexion)
                messagebox.showinfo("Cambios Guardados", "La tarjeta se modificó correctamente.")
                tabla_tarjetas()
                
                entry_card.delete(0, tk.END)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al modificar tarjeta: " + str(ex))
                
    def eliminar_tarjeta():
        seleccion = treeview_tarjetas.selection()
        if len(seleccion) == 0:
            messagebox.showwarning("Sin selección", "ERROR: SE DEBE SELECCIONAR UNA FILA.")
            return
        respuesta = messagebox.askyesno("Confirmar Eliminación", "ADVERTENCIA: Eliminar una tarjeta afecta toda la información relacionada a esta. ¿Deseas continuar?")
        if respuesta:
            eliminar_tarjeta_seleccionado(seleccion)
            
    def eliminar_tarjeta_seleccionado(seleccion):
        id = treeview_tarjetas.item(seleccion, "values")
        
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    DELETE FROM GASTOS WHERE TARJETAS_NRO_TARJETA = :id
                    """, 
                    (id[0],)
                )
                conexion.commit()
                cursor.close()
                
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    DELETE FROM TARJETAS WHERE NRO_TARJETA = :id
                    """, 
                    (id[0],)
                )
                conexion.commit()
                cursor.close()
                
                cerrar_bd(conexion)
                
                treeview_tarjetas.delete(seleccion)
                messagebox.showinfo("Eliminación Confirmada", "La tarjeta se eliminó correctamente.")
                tabla_tarjetas()
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al eliminar tarjeta: " + str(ex))
                
    ventana_style = ttk.Style(ventana_tarjetas)
    ventana_style.theme_use(parent_style.theme_use())
    
    frame = ttk.Frame(ventana_tarjetas)
    frame.pack()
    
    label_card = ttk.Label(frame, text="Nro tarjeta:")
    label_card.grid(row=0, column=0, padx=(15, 5), pady=(12, 5), sticky="w")
    entry_card = ttk.Entry(frame, state="normal", width=13)
    entry_card.grid(row=1, column=0, padx=(15, 5), pady=(0, 5), sticky="w")
    
    label_usuario = ttk.Label(frame, text="Usuario:")
    label_usuario.grid(row=0, column=1, padx=(15, 5), pady=(12, 5), sticky="w")
    selected_usuario = tk.StringVar(frame)
    selected_usuario.set("Seleccionar")
    combobox_usuarios = ttk.Combobox(
        frame,
        textvariable=selected_usuario,
        state="readonly",
        width=10,
    )
    combobox_usuarios.grid(row=1, column=1, padx=(15, 5), pady=(0, 5), sticky="w")
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""SELECT NOMBRE_USUARIO FROM USUARIOS""")
            nombres_usuarios = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)
            
            opciones_usuarios = [nombre[0] for nombre in nombres_usuarios]
            combobox_usuarios["values"] = opciones_usuarios
            combobox_usuarios.set("Seleccionar")
            
        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
            
    label_banco = ttk.Label(frame, text="Banco:")
    label_banco.grid(row=0, column=2, columnspan=2, padx=(15, 0), pady=(12, 5), sticky="w")
    selected_banco = tk.StringVar(frame)
    selected_banco.set("Seleccionar")
    combobox_bancos = ttk.Combobox(
        frame,
        textvariable=selected_banco,
        state="readonly",
        width=11,
    )
    combobox_bancos.grid(row=1, column=2, columnspan=2, padx=(15, 0), pady=(0, 5), sticky="w")
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""SELECT NOMBRE_BANCO FROM BANCOS""")
            nombres_bancos = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)
            
            opciones_bancos = [nombre[0] for nombre in nombres_bancos]
            combobox_bancos["values"] = opciones_bancos
            combobox_bancos.set("Seleccionar")
            
        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al obtener datos: " + str(ex))
            
    label_cierre = ttk.Label(frame, text="Día de cierre:")
    label_cierre.grid(row=2, column=0, padx=(15, 5), pady=(12, 5), sticky="nsew")
    entry_cierre = ttk.Entry(frame, state="normal", width=13)
    entry_cierre.grid(row=3, column=0, padx=(15, 5), pady=(0, 5), sticky="w")
    
    label_venci = ttk.Label(frame, text="Día vencimiento:")
    label_venci.grid(row=2, column=1, padx=(15, 5), pady=(12, 5), sticky="nsew")
    entry_venci = ttk.Entry(frame, state="normal", width=13)
    entry_venci.grid(row=3, column=1, padx=(15, 5), pady=(0, 5), sticky="w")
    
    label_tipo = ttk.Label(frame, text="Tipo:")
    label_tipo.grid(row=2, column=2, rowspan=2, padx=(15, 0), pady=(12, 5), sticky="nsew")
    
    a = tk.IntVar(value=1)
    check_titular = ttk.Radiobutton(frame, text="Titular", variable=a, value=1)
    check_titular.grid(row=2, column=3, padx=(0, 0), pady=(0, 0), sticky="w")
    check_adicional = ttk.Radiobutton(frame, text="Adicional", variable=a, value=2)
    check_adicional.grid(row=3, column=3, padx=(0, 0), pady=(0, 0), sticky="w")
    
    separador = ttk.Separator(frame)
    separador.grid(row=4, column=0, columnspan=4, padx=(15, 15), pady=(5, 5), sticky="nsew")
    
    boton_crear_card = ttk.Button(frame, text="Crear tarjeta", command=registrar_tarjeta)
    boton_crear_card.grid(row=5, column=0, padx=(15, 5), pady=(5, 12), sticky="nsew")

    boton_editar_card = ttk.Button(frame, text="Editar tarjeta", command=editar_tarjeta)
    boton_editar_card.grid(row=5, column=1, padx=(15, 5), pady=(5, 12), sticky="nsew")

    boton_eliminar_card = ttk.Button(frame, text="Eliminar tarjeta", command=eliminar_tarjeta)
    boton_eliminar_card.grid(row=5, column=2, columnspan=2, padx=(15, 15), pady=(5, 12), sticky="nsew")
    
    separador = ttk.Separator(frame)
    separador.grid(row=0, column=4, rowspan=10, padx=(5, 5), pady=(5, 5), sticky="nsew")
    
    def tree_card():
        frame_tabla_tarjetas = ttk.Frame(frame)
        frame_tabla_tarjetas.grid(row=0, column=5, rowspan=10, padx=(5, 15), pady=(5, 10), sticky="nsew")
        
        scroll_tabla = ttk.Scrollbar(frame_tabla_tarjetas)
        scroll_tabla.pack(side="right", fill="y")
        
        encabezados = ("NRO", "TIPO", "CIERRE", "VENCIMIENTO", "USUARIO", "BANCO")
        global treeview_tarjetas
        treeview_tarjetas = ttk.Treeview(
            frame_tabla_tarjetas,
            show="headings",
            yscrollcommand=scroll_tabla.set,
            columns=encabezados,
            height=7,
        )
        treeview_tarjetas.column("NRO", width=40)
        treeview_tarjetas.column("TIPO", width=60)
        treeview_tarjetas.column("CIERRE", width=70)
        treeview_tarjetas.column("VENCIMIENTO", width=100)
        treeview_tarjetas.column("USUARIO", width=70)
        treeview_tarjetas.column("BANCO", width=110)
        
        for encabezado in encabezados:
            treeview_tarjetas.heading(encabezado, text=encabezado)
            
        treeview_tarjetas.pack()
        treeview_tarjetas.configure()
        scroll_tabla.configure(command=treeview_tarjetas.yview)
        treeview_tarjetas.bind("<ButtonRelease-1>", seleccion_tarjetas)
        
    def tabla_tarjetas():
        treeview_tarjetas.delete(*treeview_tarjetas.get_children())
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    SELECT
                        T.NRO_TARJETA,
                        T.TIPO,
                        T.CIERRE,
                        T.VENCIMIENTO,
                        U.NOMBRE_USUARIO,
                        B.NOMBRE_BANCO
                    FROM TARJETAS T
                    JOIN USUARIOS U ON U.USUARIO = T.USUARIOS_USUARIO
                    JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
                    """
                )
                datos = cursor.fetchall()
                cursor.close()
                cerrar_bd(conexion)
                
                for fila in datos:
                    treeview_tarjetas.insert("", "end", values=fila)
                
            except Exception as ex:
                cerrar_bd(conexion)
                messagebox.showerror("Error", "Error al insertar datos: " + str(ex))
                
    def cerrar_ventana_tarjetas():
        ventana_tarjetas.destroy()
        root.deiconify()
        root.grab_set()
        actualizar()
        
    ventana_tarjetas.protocol("WM_DELETE_WINDOW", cerrar_ventana_tarjetas)
    ventana_tarjetas.grab_set()
    
    tree_card()
    tabla_tarjetas()
    center_window(ventana_tarjetas)
    
    ventana_tarjetas.mainloop()
    
actualizar()

center_window(root)
root.mainloop()
