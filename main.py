from conexion import conectar_bd
from conexion import ejecutar_query
from conexion import cerrar_bd
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
import ctypes

user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# FUNCIONES #
def center_window(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.update_idletasks()  # Asegurarse de que la ventana tenga las dimensiones correctas
    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"+{x}+{y}")


def actualizar():
    treeview.delete(*treeview.get_children())

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
                WHEN CAST(strftime('%d', G.fecha) AS INTEGER) = T.cierre THEN
                    CASE 
                        WHEN CAST(strftime('%m', G.fecha) AS INTEGER) = 12 THEN
                            date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER)+1, CAST(strftime('%m', G.fecha) AS INTEGER)-11, T.vencimiento))
                    ELSE
                        date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER), CAST(strftime('%m', G.fecha) AS INTEGER)+1, T.vencimiento))
                    END
            ELSE
                CASE 
                    WHEN CAST(strftime('%d', G.fecha) AS INTEGER) >= T.cierre+1 THEN
                        CASE 
                            WHEN CAST(strftime('%m', G.fecha) AS INTEGER) = 12 THEN
                                date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER)+1, CAST(strftime('%m', G.fecha) AS INTEGER)-10, T.vencimiento))
                        ELSE
                            date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER), CAST(strftime('%m', G.fecha) AS INTEGER)+2, T.vencimiento))
                        END
                END
            END "FECHA PAGO",
            G.MONTO "MONTO"
        FROM GASTOS G
        JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
        JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
        JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
        JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
        ORDER BY G.FECHA DESC
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
                fecha_formateada = fecha_obj.strftime("%d-%m-%Y")
                fila[2] = fecha_formateada

                fecha_original = fila[8]
                fecha_obj = datetime.strptime(fecha_original, "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d-%m-%Y")
                fila[8] = fecha_formateada

                treeview.insert("", "end", values=fila)

        except Exception as ex:
            print("Error al ejecutar la consulta:", ex)


def switch_callback():
    global treeview
    if switch.instate(["selected"]):
        style.theme_use("forest-dark")
        # root.configure(bg = "#313131")
        if treeview:
            treeview.destroy()
        tree()
        actualizar()
    else:
        style.theme_use("forest-light")
        # root.configure(bg = "#ffffff")
        if treeview:
            treeview.destroy()
        tree()
        actualizar()


def actualizar_usuario():
    combobox_bancos.set("Seleccionar")
    combobox_nro_tarjeta.set("Seleccionar")


def obtener_fecha():
    fecha_seleccionada = entry_fecha.get_date()
    entry_fecha.config(state=tk.NORMAL)
    entry_fecha.delete(0, tk.END)
    entry_fecha.insert(tk.END, fecha_seleccionada)
    entry_fecha.config(state=tk.DISABLED)


def generar_id_gasto():
    consulta = """ SELECT MAX(ID) FROM GASTOS"""
    result = ejecutar_query(conectar_bd(), consulta)
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
    id = generar_id_gasto()
    fecha = entry_fecha.get()
    fecha_obj = datetime.strptime(fecha, "%d-%m-%Y")
    fecha_formateada = fecha_obj.strftime("%Y-%m-%d")


    detalle = str(entry_detalle.get())
    monto = float(entry_monto.get())
    usuarios_usuario = obtener_usuario_id()
    tarjetas_nro_tarjeta = str(combobox_nro_tarjeta.get())
    establecimientos_establecimiento = obtener_establecimiento_id()

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
            """
            , (id, fecha_formateada, detalle, monto, usuarios_usuario, tarjetas_nro_tarjeta, establecimientos_establecimiento)
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
        entry_fecha.set_date(gasto[2])
        selected_establecimiento.set(gasto[3])
        entry_detalle.delete(0, tk.END)  # Borrar el contenido actual del Entry antes de insertar nuevo valor
        entry_detalle.insert(0, gasto[4])
        selected_banco.set(gasto[5])
        selected_nro_tarjeta.set(gasto[6])
        entry_monto.delete(0, tk.END)  # Borrar el contenido actual del Entry antes de insertar nuevo valor
        entry_monto.insert(0, gasto[9])


def editar_gasto():
    seleccion = treeview.selection()
    if len(seleccion) == 0:
        messagebox.showwarning("Sin Selección", "No se ha seleccionado ningun gasto.")
        return
    respuesta = messagebox.askyesno("Confirmar Edición", "Vas a modificar un gasto. ¿Deseas continuar?")
    if respuesta:
        editar_gasto_seleccionado()


def editar_gasto_seleccionado():
    seleccion = treeview.selection()
    if seleccion:
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
            """
            , (fecha_formateada, detalle, monto, usuarios_usuario, tarjetas_nro_tarjeta, establecimientos_establecimiento, id)
            )
            conexion.commit()
            cursor.close()
            cerrar_bd(conexion)
            messagebox.showinfo("Gasto modificado", "El gasto se modificó correctamente.",)
            actualizar()

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al modificar gasto: " + str(ex))


def eliminar_gasto():
    seleccion = treeview.selection()
    if len(seleccion) == 0:
        messagebox.showwarning("Sin selección", "No se ha seleccionado ningun gasto.")
        return
    respuesta = messagebox.askyesno(
        "Confirmar Eliminación", "Vas a eliminar un gasto. ¿Deseas continuar?"
    )
    if respuesta:
        eliminar_gasto_seleccionado(seleccion)


def eliminar_gasto_seleccionado(seleccion):
    seleccion = treeview.selection()
    if seleccion:
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
            messagebox.showinfo("Gasto eliminado", "El gasto se eliminó correctamente.",)
            actualizar()

        except Exception as ex:
            cerrar_bd(conexion)
            messagebox.showerror("Error", "Error al eliminar gasto: " + str(ex))


def filtrar_datos():
    treeview.delete(*treeview.get_children())

    selected_usuario_filtro = combobox_usuarios_filtro.get()
    selected_banco_filtro = combobox_bancos_filtro.get()
    selected_nro_tarjeta_filtro = combobox_nro_tarjeta_filtro.get()

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
        
    #print(fecha_inicio_str)
    #print(type(fecha_inicio_str))
    #print(fecha_fin_str)
    #print(type(fecha_fin_str))

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
                    WHEN CAST(strftime('%d', G.fecha) AS INTEGER) = T.cierre THEN
                        CASE 
                            WHEN CAST(strftime('%m', G.fecha) AS INTEGER) = 12 THEN
                                date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER)+1, CAST(strftime('%m', G.fecha) AS INTEGER)-11, T.vencimiento))
                        ELSE
                            date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER), CAST(strftime('%m', G.fecha) AS INTEGER)+1, T.vencimiento))
                        END
                ELSE
                    CASE 
                        WHEN CAST(strftime('%d', G.fecha) AS INTEGER) >= T.cierre+1 THEN
                            CASE 
                                WHEN CAST(strftime('%m', G.fecha) AS INTEGER) = 12 THEN
                                    date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER)+1, CAST(strftime('%m', G.fecha) AS INTEGER)-10, T.vencimiento))
                            ELSE
                                date(printf('%04d-%02d-%02d', CAST(strftime('%Y', G.fecha) AS INTEGER), CAST(strftime('%m', G.fecha) AS INTEGER)+2, T.vencimiento))
                            END
                    END
                END "FECHA PAGO",
                G.MONTO "MONTO"
            FROM GASTOS G
            JOIN USUARIOS U ON U.USUARIO = G.USUARIOS_USUARIO
            JOIN ESTABLECIMIENTOS E ON E.ESTABLECIMIENTO = G.ESTABLECIMIENTOS_ESTABLECIMIENTO
            JOIN TARJETAS T ON T.NRO_TARJETA = G.TARJETAS_NRO_TARJETA
            JOIN BANCOS B ON B.BANCO = T.BANCOS_BANCO
            WHERE U.NOMBRE_USUARIO = :selected_usuario_filtro AND B.NOMBRE_BANCO = :selected_banco_filtro AND T.NRO_TARJETA = :selected_nro_tarjeta_filtro AND G.FECHA >= date(printf('%04d-%02d-%02d', :año_inicio, :mes_inicio, T.cierre+1)) AND G.FECHA <= date(printf('%04d-%02d-%02d', :año_cierre, :mes_cierre, T.cierre))
            ORDER BY G.FECHA DESC
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

            for fila in datos:
                fila = list(fila)
                fecha_original = fila[2]
                fecha_obj = datetime.strptime(fecha_original, "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d-%m-%Y")
                fila[2] = fecha_formateada

                fecha_original = fila[8]
                fecha_obj = datetime.strptime(fecha_original, "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d-%m-%Y")
                fila[8] = fecha_formateada

                treeview.insert("", "end", values=fila)

        except Exception as ex:
            print("Error al ejecutar la consulta:", ex)


root = tk.Tk()
style = ttk.Style(root)
root.title("GESTIÓN DE GASTOS")
root.resizable(0, 0)


# Import the tcl file
root.tk.call("source", "forest-dark.tcl")
root.tk.call("source", "forest-light.tcl")
style.theme_use("forest-light")

# FRAMES #
frame = ttk.Frame(root)
frame.pack()

###FRAME_DATOS###
frames_datos = ttk.LabelFrame(frame, text="Datos")
frames_datos.grid(row=0, column=0, columnspan=3, padx=(30, 30), pady=(30, 10), sticky="nsew")

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
entry_fecha.delete(0, "end")
entry_fecha.bind("<<DateEntrySelected>>", obtener_fecha)


label_usuario = ttk.Label(frames_datos, text="Usuario:")
label_usuario.grid(row=0, column=1, padx=(15, 0), sticky="w")
conexion = conectar_bd()
if conexion:
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """SELECT 
        USUARIO
        ,NOMBRE_USUARIO 
        FROM USUARIOS"""
        )
        nombres_usuarios = cursor.fetchall()
        cursor.close()
        cerrar_bd(conexion)

        opciones_usuarios = [nombre[1] for nombre in nombres_usuarios]
        selected_usuario = tk.StringVar(frames_datos)
        selected_usuario.set("Seleccionar")
        combobox_usuarios = ttk.Combobox(
            frames_datos,
            textvariable=selected_usuario,
            values=opciones_usuarios,
            state="readonly",
            width=20,
        )
        combobox_usuarios.grid(row=1, column=1, padx=(15, 0), sticky="w")

    except Exception as ex:
        cerrar_bd(conexion)
        messagebox.showerror("Error", "Error al obtener datos: " + str(ex))


label_banco = ttk.Label(frames_datos, text="Banco:")
label_banco.grid(row=0, column=2, padx=(15, 0), sticky="w")
conexion = conectar_bd()
if conexion:
    try:
        cursor = conexion.cursor()
        nombre_usuario = combobox_usuarios.get()
        cursor.execute(
            """SELECT 
            B.BANCO
            ,B.NOMBRE_BANCO
            FROM BANCOS B
            JOIN TARJETAS T ON T.BANCOS_BANCO = B.BANCO
            JOIN USUARIOS U ON U.USUARIO = T.USUARIOS_USUARIO
            WHERE U.NOMBRE_USUARIO = :nombre""",
            (nombre_usuario,),
        )
        nombres_bancos = cursor.fetchall()
        cursor.close()
        cerrar_bd(conexion)

        opciones_bancos = [nombre[1] for nombre in nombres_bancos]
        selected_banco = tk.StringVar(frames_datos)
        selected_banco.set("Seleccionar")
        combobox_bancos = ttk.Combobox(
            frames_datos,
            textvariable=selected_banco,
            values=opciones_bancos,
            state="disabled",
            width=20,
        )
        combobox_bancos.grid(row=1, column=2, padx=(15, 0), sticky="w")

    except Exception as ex:
        cerrar_bd(conexion)
        messagebox.showerror("Error", "Error al obtener datos: " + str(ex))

label_nro_tarjeta = ttk.Label(frames_datos, text="Nro. Tarjeta:")
label_nro_tarjeta.grid(row=0, column=3, padx=(15, 0), sticky="w")
conexion = conectar_bd()
if conexion:
    try:
        cursor = conexion.cursor()
        nombre_usuario = combobox_usuarios.get()
        nombre_banco = combobox_bancos.get()
        cursor.execute(
            """SELECT 
            B.BANCO
            ,T.NRO_TARJETA
            FROM BANCOS B
            JOIN TARJETAS T ON T.BANCOS_BANCO = B.BANCO
            JOIN USUARIOS U ON U.USUARIO = T.USUARIOS_USUARIO
            WHERE U.NOMBRE_USUARIO = :nombre AND B.NOMBRE_BANCO = :banco""",
            (nombre_usuario,nombre_banco,),
        )
        nro_tarjeta = cursor.fetchall()
        cursor.close()
        cerrar_bd(conexion)

        opciones_nro_tarjeta = [nombre[1] for nombre in nro_tarjeta]
        selected_nro_tarjeta = tk.StringVar(frames_datos)
        selected_nro_tarjeta.set("Seleccionar")
        combobox_nro_tarjeta = ttk.Combobox(
            frames_datos,
            textvariable=selected_nro_tarjeta,
            values=opciones_nro_tarjeta,
            state="disabled",
            width=8,
        )
        combobox_nro_tarjeta.grid(row=1, column=3, padx=(15, 0), sticky="w")

    except Exception as ex:
        cerrar_bd(conexion)
        messagebox.showerror("Error", "Error al obtener datos: " + str(ex))


def actualizar_bancos(event):
    selected_usuario = combobox_usuarios.get()

    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """SELECT 
                B.BANCO
                ,B.NOMBRE_BANCO
                FROM BANCOS B
                JOIN TARJETAS T ON T.BANCOS_BANCO = B.BANCO
                JOIN USUARIOS U ON U.USUARIO = T.USUARIOS_USUARIO
                WHERE U.NOMBRE_USUARIO = :nombre""",
                (selected_usuario,),
            )
            nombres_bancos = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)

            opciones_bancos = [nombre[1] for nombre in nombres_bancos]
            combobox_bancos["values"] = opciones_bancos
            combobox_bancos.set("Seleccionar")  # Limpiar selección de banco
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
                """SELECT 
                B.BANCO
                ,T.NRO_TARJETA
                FROM BANCOS B
                JOIN TARJETAS T ON T.BANCOS_BANCO = B.BANCO
                JOIN USUARIOS U ON U.USUARIO = T.USUARIOS_USUARIO
                WHERE U.NOMBRE_USUARIO = :nombre AND B.NOMBRE_BANCO = :banco""",
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
            combobox_nro_tarjeta.set(
                "Seleccionar"
            )  # Limpiar selección de número de tarjeta

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
label_establecimiento.grid(row=3, column=0, padx=(15, 0), sticky="w")
consulta = """SELECT 
        ESTABLECIMIENTO
        ,NOMBRE_EST
        FROM ESTABLECIMIENTOS"""
nombres_establecimientos = ejecutar_query(conectar_bd(), consulta)
cerrar_bd(conectar_bd())


opciones_establecimientos = [nombre[1] for nombre in nombres_establecimientos]
selected_establecimiento = tk.StringVar(frames_datos)
selected_establecimiento.set("Seleccionar")
combobox_establecimientos = ttk.Combobox(
    frames_datos,
    textvariable=selected_establecimiento,
    values=opciones_establecimientos,
    state="readonly",
    width=20,
)
combobox_establecimientos.grid(row=4, column=0, padx=(15, 0), sticky="w")

label_detalle = ttk.Label(frames_datos, text="Detalle:")
label_detalle.grid(row=3, column=1, columnspan=2, padx=(15, 0), sticky="w")
entry_detalle = ttk.Entry(frames_datos, width=52)
entry_detalle.grid(row=4, column=1, columnspan=2, padx=(15, 0), sticky="w")

label_monto = ttk.Label(frames_datos, text="Monto:")
label_monto.grid(row=3, column=3, padx=(15, 0), sticky="w")
entry_monto = ttk.Entry(frames_datos, width=11)
entry_monto.grid(row=4, column=3, padx=(15, 0), sticky="w")

separador = ttk.Separator(frames_datos)
separador.grid(row=0, column=4, rowspan=6, padx=(10, 10), pady=(0, 10), sticky="nsew")

boton_registrar = ttk.Button(frames_datos, text="Registrar Gasto", width=20, command=registrar_gasto)
boton_registrar.grid(row=1, column=5, padx=(15, 15), pady=(0, 0), sticky="nw")

boton_editar = ttk.Button(frames_datos, text="Guardar Cambios", width=20, command=editar_gasto)
boton_editar.grid(row=2, column=5, padx=(15, 15), pady=(15, 0), sticky="nw")

boton_eliminar = ttk.Button(frames_datos, text="Eliminar Selección", width=20, command=eliminar_gasto)
boton_eliminar.grid(row=4, column=5, padx=(15, 15), pady=(0, 0), sticky="nw")


###FRAME_TABLA###
def tree():
    frame_tabla = ttk.Frame(frame)
    frame_tabla.grid(
        row=1, column=0, columnspan=2, padx=(30, 0), pady=(8, 0), sticky="nsew"
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
    treeview.column("Fecha", width=66)
    treeview.column("Lugar", width=90)
    treeview.column("Detalle", width=135)
    treeview.column("Banco", width=110)
    treeview.column("Nro", width=30)
    treeview.column("Tipo", width=55)
    treeview.column("Fecha Pago", width=66)
    treeview.column("Monto", width=55)

    for encabezado in encabezados:
        treeview.heading(encabezado, text=encabezado)

    treeview.pack()
    treeview.configure()
    scroll_tabla.configure(command=treeview.yview)
    treeview.bind("<ButtonRelease-1>", seleccion)


tree()


###FRAME_FILTROS###
frame_filtros = ttk.LabelFrame(frame, text="Filtrar datos")
frame_filtros.grid(row=1, column=2, padx=(10, 30), pady=(0, 0), sticky="nsew")

label_usuario_filtro = ttk.Label(frame_filtros, text="Usuario:")
label_usuario_filtro.grid(row=0, column=0, columnspan=3, padx=(15, 0), pady=(5, 0), sticky="w")
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
        selected_usuario_filtro = tk.StringVar(frame_filtros)
        selected_usuario_filtro.set("Seleccionar")
        combobox_usuarios_filtro = ttk.Combobox(
            frame_filtros,
            textvariable=selected_usuario_filtro,
            values=opciones_usuarios,
            state="readonly",
            width=18,
        )

        combobox_usuarios_filtro.grid(row=1, column=0, columnspan=3, padx=(15, 15), pady=(0, 0), sticky="w")

    except Exception as ex:
        cerrar_bd(conexion)
        messagebox.showerror("Error", "Error al obtener datos: " + str(ex))

label_banco_filtro = ttk.Label(frame_filtros, text="Banco:")
label_banco_filtro.grid(
    row=2, column=0, columnspan=3, padx=(15, 0), pady=(12, 0), sticky="w"
)
conexion = conectar_bd()
if conexion:
    try:
        cursor = conexion.cursor()
        nombre_usuario = combobox_usuarios_filtro.get()
        cursor.execute(
            """
            SELECT 
                B.BANCO
                ,B.NOMBRE_BANCO
            FROM BANCOS B
            JOIN TARJETAS T ON T.BANCOS_BANCO = B.BANCO
            JOIN USUARIOS U ON U.USUARIO = T.USUARIOS_USUARIO
            WHERE U.NOMBRE_USUARIO = :nombre
            """,
            (nombre_usuario,),
        )
        nombres_bancos = cursor.fetchall()
        cursor.close()
        cerrar_bd(conexion)

        opciones_bancos = [nombre[1] for nombre in nombres_bancos]
        selected_banco_filtro = tk.StringVar(frame_filtros)
        selected_banco_filtro.set("Seleccionar")
        combobox_bancos_filtro = ttk.Combobox(
            frame_filtros,
            textvariable=selected_banco_filtro,
            values=opciones_bancos,
            state="disabled",
            width=18,
        )
        combobox_bancos_filtro.grid(row=3, column=0, columnspan=3, padx=(15, 15), sticky="w")

    except Exception as ex:
        cerrar_bd(conexion)
        messagebox.showerror("Error", "Error al obtener datos: " + str(ex))

label_nro_tarjeta_filtro = ttk.Label(frame_filtros, text="Nro. Tarjeta:")
label_nro_tarjeta_filtro.grid(row=4, column=0, columnspan=3, padx=(15, 0), pady=(12, 0), sticky="w")
conexion = conectar_bd()
if conexion:
    try:
        cursor = conexion.cursor()
        nombre_usuario = combobox_usuarios_filtro.get()
        nombre_banco = combobox_bancos_filtro.get()
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
                nombre_usuario,
                nombre_banco,
            ),
        )
        nro_tarjeta = cursor.fetchall()
        cursor.close()
        cerrar_bd(conexion)

        opciones_nro_tarjeta = [nombre[1] for nombre in nro_tarjeta]
        selected_nro_tarjeta_filtro = tk.StringVar(frame_filtros)
        selected_nro_tarjeta_filtro.set("Seleccionar")
        combobox_nro_tarjeta_filtro = ttk.Combobox(
            frame_filtros,
            textvariable=selected_nro_tarjeta_filtro,
            values=opciones_nro_tarjeta,
            state="disabled",
            width=18,
        )
        combobox_nro_tarjeta_filtro.grid(row=5, column=0, columnspan=3, padx=(15, 15), pady=(0, 12), sticky="w")

    except Exception as ex:
        cerrar_bd(conexion)
        messagebox.showerror("Error", "Error al obtener datos: " + str(ex))


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
                """,
                (selected_usuario_filtro,),
            )
            nombres_bancos = cursor.fetchall()
            cursor.close()
            cerrar_bd(conexion)

            opciones_bancos = [nombre[1] for nombre in nombres_bancos]
            combobox_nro_tarjeta_filtro["values"] = opciones_nro_tarjeta
            combobox_bancos_filtro["values"] = opciones_bancos
            combobox_bancos_filtro.set("Seleccionar")  # Limpiar selección de banco
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
            combobox_nro_tarjeta_filtro.set("Seleccionar")  # Limpiar selección de número de tarjeta

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
                entry_dia["state"] = "disabled"

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
                        (nombre_usuario, nombre_banco, nro_tarjeta),
                    )
                    años = cursor.fetchall()
                    cursor.close()
                    cerrar_bd(conexion)

                    opciones_años = [año[0] for año in años]
                    combobox_año["values"] = opciones_años
                    combobox_año.set(opciones_años[0])  # Limpiar selección de banco

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

combobox_año = ttk.Combobox(frame_filtros, state="normal", width=2)
combobox_año.grid(row=7, column=2, padx=(3, 10), pady=(5, 15), sticky="nsew")
combobox_año.insert(0, "2000")
combobox_año["state"] = "disabled"


boton_filtrar = ttk.Button(frame_filtros, text="Filtrar", width=5, command=filtrar_datos)
boton_filtrar.grid(row=8, column=0, columnspan=2, padx=(15, 0), pady=(0, 11), sticky="nsew")

boton_limpiar = ttk.Button(frame_filtros, text="Limpiar", width=6, command=actualizar)
boton_limpiar.grid(row=8, column=2, columnspan=2, padx=(5, 15), pady=(0, 11), sticky="nsew")


###FRAME_REPORTE###
frame_reporte = ttk.LabelFrame(frame, text="Reporte")
frame_reporte.grid(row=2, column=0, columnspan=2, padx=(30, 0), pady=(5, 30), sticky="nw")

frame_total = ttk.LabelFrame(frame_reporte, text="Resumen General (últimos 3 meses)")
frame_total.grid(row=0, column=0, padx=(25, 15), pady=(5, 15), sticky="nsew")

label_usuario_gastador = ttk.Label(frame_total, text="Usuario con más gastos:")
label_usuario_gastador.grid(row=0, column=0, padx=(15, 0), pady=(10, 0), sticky="w")

entry_usuario_gastador = ttk.Entry(frame_total, state="disabled", width=20)
entry_usuario_gastador.grid(row=1, column=0, padx=(15, 0), pady=(0, 0), sticky="w")

label_usuario_frecuente = ttk.Label(frame_total, text="Usuario más frecuente:")
label_usuario_frecuente.grid(row=0, column=1, padx=(20, 15), pady=(12, 0), sticky="w")

entry_usuario_frecuente = ttk.Entry(frame_total, state="disabled", width=20)
entry_usuario_frecuente.grid(row=1, column=1, padx=(20, 15), pady=(0, 0), sticky="w")


label_banco_gastador = ttk.Label(frame_total, text="Banco con más gastos:")
label_banco_gastador.grid(row=2, column=0, padx=(15, 0), pady=(11, 0), sticky="w")

entry_label_banco_gastador = ttk.Entry(frame_total, state="disabled", width=20)
entry_label_banco_gastador.grid(row=3, column=0, padx=(15, 0), pady=(0, 0), sticky="w")

label_banco_frecuente = ttk.Label(frame_total, text="Banco más frecuente:")
label_banco_frecuente.grid(row=2, column=1, padx=(20, 15), pady=(11, 0), sticky="w")

entry_label_banco_frecuente = ttk.Entry(frame_total, state="disabled", width=20)
entry_label_banco_frecuente.grid(row=3, column=1, padx=(20, 15), pady=(0, 0), sticky="w")


label_estable_gastador = ttk.Label(frame_total, text="Estab. con más gastos:")
label_estable_gastador.grid(row=4, column=0, padx=(15, 0), pady=(11, 0), sticky="w")

entry_estable_gastador = ttk.Entry(frame_total, state="disabled", width=20)
entry_estable_gastador.grid(row=5, column=0, padx=(15, 0), pady=(0, 0), sticky="w")

label_estable_frecuente = ttk.Label(frame_total, text="Estab. más frecuente:")
label_estable_frecuente.grid(row=4, column=1, padx=(20, 15), pady=(11, 0), sticky="w")

entry_estable_frecuente = ttk.Entry(frame_total, state="disabled", width=20)
entry_estable_frecuente.grid(row=5, column=1, padx=(20, 15), pady=(0, 0), sticky="w")


label_estable_gastador = ttk.Label(frame_total, text="Gasto Total:")
label_estable_gastador.grid(row=6, column=0, padx=(15, 0), pady=(11, 0), sticky="w")

entry_estable_gastador = ttk.Entry(frame_total, state="normal", width=20)
entry_estable_gastador.grid(row=7, column=0, padx=(15, 0), pady=(0, 12), sticky="w")
entry_estable_gastador.insert(0, "holaaa")  ####################################################################
entry_estable_gastador["state"] = "disabled"

label_estable_frecuente = ttk.Label(frame_total, text="Gasto Promedio Mensual:")
label_estable_frecuente.grid(row=6, column=1, padx=(20, 15), pady=(11, 0), sticky="w")

entry_estable_frecuente = ttk.Entry(frame_total, state="disabled", width=20)
entry_estable_frecuente.grid(row=7, column=1, padx=(20, 15), pady=(0, 12), sticky="w")


separador = ttk.Separator(frame_reporte)
separador.grid(row=0, column=1, padx=(15, 15), pady=(10, 15), sticky="nsew")


frame_facturacion = ttk.LabelFrame(frame_reporte, text="Periodo de Facturación")
frame_facturacion.grid(row=0, column=2, padx=(15, 25), pady=(5, 15), sticky="nsew")

label_inicio = ttk.Label(frame_facturacion, text="Fecha Inicio:")
label_inicio.grid(row=0, column=0, padx=(15, 0), pady=(5, 5), sticky="e")

entry_inicio = ttk.Entry(frame_facturacion, state="disabled", width=10)
entry_inicio.grid(row=0, column=1, padx=(0, 15), pady=(5, 5), sticky="w")

label_fin = ttk.Label(frame_facturacion, text="Fecha Fin:")
label_fin.grid(row=1, column=0, padx=(15, 0), pady=(5, 5), sticky="e")

entry_fin = ttk.Entry(frame_facturacion, state="disabled", width=10)
entry_fin.grid(row=1, column=1, padx=(0, 15), pady=(5, 5), sticky="w")

label_pago = ttk.Label(frame_facturacion, text="Fecha Pago:")
label_pago.grid(row=2, column=0, padx=(15, 0), pady=(5, 5), sticky="e")

entry_pago = ttk.Entry(frame_facturacion, state="disabled", width=10)
entry_pago.grid(row=2, column=1, padx=(0, 15), pady=(5, 5), sticky="w")

label_total = ttk.Label(frame_facturacion, text="Pago Total del Mes:", font=("Arial", 10, "bold"))
label_total.grid(row=3, column=0, padx=(15, 0), pady=(5, 5), sticky="e")

entry_total = ttk.Entry(frame_facturacion, state="disabled", width=10)
entry_total.grid(row=3, column=1, padx=(0, 15), pady=(5, 5), sticky="w")

label_fin = ttk.Label(frame_facturacion, text="Pago Promedio:")
label_fin.grid(row=4, column=0, padx=(15, 0), pady=(5, 5), sticky="e")

entry_fin = ttk.Entry(frame_facturacion, state="disabled", width=10)
entry_fin.grid(row=4, column=1, padx=(0, 15), pady=(5, 5), sticky="w")

boton_generar_reporte = ttk.Button(frame_facturacion, text="Generar Reporte")
boton_generar_reporte.grid(row=5, column=0, columnspan=2, padx=(15, 15), pady=(5, 12), sticky="nsew")


frame_config = ttk.LabelFrame(frame, text="Configuración")
frame_config.grid(row=2, column=2, padx=(10, 30), pady=(5, 30), sticky="nsew")

boton_usuario = ttk.Button(frame_config, text="Usuarios")
boton_usuario.grid(row=0, column=0, columnspan=2, padx=(15, 15), pady=(12, 12), sticky="nsew")

boton_banco = ttk.Button(frame_config, text="Bancos")
boton_banco.grid(row=1, column=0, columnspan=2, padx=(15, 15), pady=(12, 12), sticky="nsew")

boton_tarjeta = ttk.Button(frame_config, text="Tarjetas")
boton_tarjeta.grid(row=2, column=0, columnspan=2, padx=(15, 15), pady=(12, 12), sticky="nsew")

boton_establecimiento = ttk.Button(frame_config, text="Establecimientos")
boton_establecimiento.grid(row=3, column=0, columnspan=2, padx=(15, 15), pady=(12, 12), sticky="nsew")

separador = ttk.Separator(frame_config)
separador.grid(row=4, column=0, columnspan=2, padx=(15, 15), pady=(12, 12), sticky="nsew")

label_switch = ttk.Label(frame_config, text="Tema Claro/Oscuro")
label_switch.grid(row=5, column=0, padx=(15, 0), pady=(5, 5), sticky="nsew")
# Switch
switch = ttk.Checkbutton(frame_config, style="Switch", command=switch_callback)
switch.grid(row=5, column=1, padx=(10, 15), pady=(5, 5), sticky="nsew")


actualizar()

center_window(root)

root.mainloop()
