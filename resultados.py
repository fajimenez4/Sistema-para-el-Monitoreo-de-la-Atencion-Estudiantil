import tkinter as tk
from tkinter import messagebox
from database import conexion_db

# Establecer conexión con la base de datos
connection = conexion_db()
cursor = connection.cursor()

# Obtener los datos del test del usuario desde la base de datos
def datos_tabla_test(correo):
    cursor.execute("SELECT * FROM test WHERE correo = %s", (correo,))
    datos_test = cursor.fetchall()
    if datos_test:
        ic = datos_test[0][5] 
        resultado = "\n".join([f"Total de Caracteres: {dato[2]}\nAciertos: {dato[3]}\nErrores: {dato[4]}\nIC: {ic}%" for dato in datos_test])
        return f"{resultado}", ic
    return "No hay datos de test.", None

# Obtener los datos de atención del usuario desde la base de datos
def datos_tabla_atencion(correo):
    cursor.execute("SELECT * FROM atencion WHERE correo = %s", (correo,))
    datos_atencion = cursor.fetchall()
    if datos_atencion:
        porcentaje_atencion = datos_atencion[0][7]  
        resultado = "\n".join([f"Fijaciones: {dato[2]}\nSacadas: {dato[3]}\nTiempo Total: {dato[6]}s\nAtención: {porcentaje_atencion}%" for dato in datos_atencion])
        return f"{resultado}", porcentaje_atencion
    return "No hay datos de atención.", None

# Calcular el porcentaje de atención real combinando IC y porcentaje de atención
def calcular_porcentaje_atencion_real(ic, porcentaje_atencion):
    return (ic + porcentaje_atencion) / 2 if ic is not None and porcentaje_atencion is not None else None

# Clasificar la atención según el porcentaje
def clasificar_atencion(porcentaje_atencion):
    if porcentaje_atencion < 20:
        return "Atención mínima"
    elif 20 <= porcentaje_atencion <= 50:
        return "Atención moderada"
    elif 51 <= porcentaje_atencion <= 80:
        return "Atención adecuada"
    else:
        return "Atención óptima"

# Mostrar los resultados de los test y la atención en la interfaz gráfica
def mostrar_resultados(correo):
    if correo:
        datos_test, ic = datos_tabla_test(correo)
        datos_atencion, porcentaje_atencion = datos_tabla_atencion(correo)
        porcentaje_real = calcular_porcentaje_atencion_real(ic, porcentaje_atencion)

        # Clasificación de la atención
        clasificacion = clasificar_atencion(porcentaje_atencion) if porcentaje_atencion is not None else "No disponible"

        # Mostrar resultados del test en la interfaz gráfica
        text_test.config(state=tk.NORMAL)
        text_test.delete(1.0, tk.END)
        text_test.insert(tk.END, datos_test)
        text_test.config(state=tk.DISABLED)

        # Mostrar resultados de atención en la interfaz gráfica
        text_atencion.config(state=tk.NORMAL)
        text_atencion.delete(1.0, tk.END)
        text_atencion.insert(tk.END, datos_atencion)
        text_atencion.config(state=tk.DISABLED)

        # Mostrar porcentaje y clasificación de atención en la interfaz gráfica
        text_porcentaje_clasificacion.config(state=tk.NORMAL)
        text_porcentaje_clasificacion.delete(1.0, tk.END)
        if porcentaje_real is not None:
            text_porcentaje_clasificacion.insert(tk.END, f"Porcentaje de Atención: {porcentaje_real:.2f}%\n{clasificacion}")
        else:
            text_porcentaje_clasificacion.insert(tk.END, "No se pudo calcular el porcentaje de atención real.\nClasificación no disponible.")
        text_porcentaje_clasificacion.config(state=tk.DISABLED)
    else:
        messagebox.showwarning("Advertencia", "Correo no disponible.")

# Función para cerrar la ventana
def salir():
    root.destroy()

# Iniciar la búsqueda de datos del usuario y mostrar la interfaz gráfica
def iniciar_busqueda_datos_usuario(correo):
    global root, text_test, text_atencion, text_porcentaje_clasificacion

    root = tk.Tk()
    root.title("Resultados del Usuario")
    root.attributes("-fullscreen", True)
    root.configure(bg="#f0f0f0")

    # Configuración de la interfaz gráfica: título y marco de resultados
    label_titulo = tk.Label(root, text="RESULTADOS", font=("Arial", 24, "bold"), bg="#f0f0f0")
    label_titulo.pack(pady=20)

    frame_resultados = tk.Frame(root, bg="#f0f0f0")
    frame_resultados.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

    # Resultados del test en un marco
    frame_test = tk.Frame(frame_resultados, bg="white", bd=2, relief=tk.GROOVE)
    frame_test.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.BOTH, expand=True)

    label_test = tk.Label(frame_test, text="Resultados del Test", font=("Arial", 14, "bold"), bg="white")
    label_test.pack(pady=5)

    text_test = tk.Text(frame_test, height=10, width=40, font=("Arial", 12), state=tk.DISABLED, wrap="word")
    text_test.pack(pady=5, padx=5)

    # Resultados de atención en otro marco
    frame_atencion = tk.Frame(frame_resultados, bg="white", bd=2, relief=tk.GROOVE)
    frame_atencion.pack(side=tk.RIGHT, padx=20, pady=10, fill=tk.BOTH, expand=True)

    label_atencion = tk.Label(frame_atencion, text="Resultados de Atención", font=("Arial", 14, "bold"), bg="white")
    label_atencion.pack(pady=5)

    text_atencion = tk.Text(frame_atencion, height=10, width=40, font=("Arial", 12), state=tk.DISABLED, wrap="word")
    text_atencion.pack(pady=5, padx=5)

    # Marco para mostrar porcentaje y clasificación
    frame_porcentaje_clasificacion = tk.Frame(root, bg="white", bd=2, relief=tk.GROOVE)
    frame_porcentaje_clasificacion.pack(pady=10, padx=20, fill=tk.X)

    label_porcentaje_clasificacion = tk.Label(frame_porcentaje_clasificacion, text="Porcentaje y Clasificación de Atención", font=("Arial", 14, "bold"), bg="white")
    label_porcentaje_clasificacion.pack(pady=5)

    text_porcentaje_clasificacion = tk.Text(frame_porcentaje_clasificacion, height=4, width=50, font=("Arial", 14), state=tk.DISABLED, wrap="word")
    text_porcentaje_clasificacion.pack(pady=5)

    # Botón para salir de la interfaz
    button_salir = tk.Button(root, text="Salir", font=("Arial", 14, "bold"), command=salir, bg="red", fg="white")
    button_salir.pack(pady=20)

    # Llamar a la función que muestra los resultados con el correo proporcionado
    mostrar_resultados(correo)

    root.mainloop()
    connection.close()
