import tkinter as tk
from tkinter import messagebox
from database import conexion_db

connection = conexion_db()
cursor = connection.cursor()

def obtener_id_usuario(correo):
    cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
    id = cursor.fetchone()
    return id[0] if id else None

def datos_tabla_test(id):
    cursor.execute("SELECT * FROM test WHERE id = %s", (id,))
    datos_test = cursor.fetchall()
    if datos_test:
        ic = datos_test[0][4] 
        resultado = "\n".join([f"ID: {dato[0]}\nTotal: {dato[1]}\nAciertos: {dato[2]}\nErrores: {dato[3]}\nIC: {ic}%" for dato in datos_test])
        return f"{resultado}", ic
    return "No hay datos de test.", None

def datos_tabla_atencion(id):
    cursor.execute("SELECT * FROM atencion WHERE id= %s", (id,))
    datos_atencion = cursor.fetchall()
    if datos_atencion:
        porcentaje_atencion = datos_atencion[0][6]  
        resultado = "\n".join([f"ID: {dato[0]}\nFijaciones: {dato[1]}\nSacadas: {dato[2]}\nTiempo Total: {dato[5]}s\nAtención: {porcentaje_atencion}%" for dato in datos_atencion])
        return f"{resultado}", porcentaje_atencion
    return "No hay datos de atención.", None

def calcular_porcentaje_atencion_real(ic, porcentaje_atencion):
    return (ic + porcentaje_atencion) / 2 if ic is not None and porcentaje_atencion is not None else None

def clasificar_atencion(porcentaje_atencion):
    if porcentaje_atencion < 20:
        return "Atención mínima"
    elif 20 <= porcentaje_atencion <= 50:
        return "Atención moderada"
    elif 51 <= porcentaje_atencion <= 80:
        return "Atención adecuada"
    else:
        return "Atención óptima"

def mostrar_resultados():
    correo = entry_correo.get()
    if correo:
        id_usuario = obtener_id_usuario(correo)
        if id_usuario:
            datos_test, ic = datos_tabla_test(id_usuario)
            datos_atencion, porcentaje_atencion = datos_tabla_atencion(id_usuario)
            porcentaje_real = calcular_porcentaje_atencion_real(ic, porcentaje_atencion)

            # Clasificación de la atención
            clasificacion = clasificar_atencion(porcentaje_atencion) if porcentaje_atencion is not None else "No disponible"

            text_test.config(state=tk.NORMAL)
            text_test.delete(1.0, tk.END)
            text_test.insert(tk.END, datos_test)
            text_test.config(state=tk.DISABLED)

            text_atencion.config(state=tk.NORMAL)
            text_atencion.delete(1.0, tk.END)
            text_atencion.insert(tk.END, datos_atencion)
            text_atencion.config(state=tk.DISABLED)

            # Mostrar porcentaje y clasificación juntos
            text_porcentaje_clasificacion.config(state=tk.NORMAL)
            text_porcentaje_clasificacion.delete(1.0, tk.END)
            if porcentaje_real is not None:
                text_porcentaje_clasificacion.insert(tk.END, f"Porcentaje de Atención: {porcentaje_real:.2f}%\n{clasificacion}")
            else:
                text_porcentaje_clasificacion.insert(tk.END, "No se pudo calcular el porcentaje de atención real.\nClasificación no disponible.")
            text_porcentaje_clasificacion.config(state=tk.DISABLED)
        else:
            messagebox.showerror("Error", "No se encontró un usuario con ese correo.")
    else:
        messagebox.showwarning("Advertencia", "Ingrese un correo.")

def salir():
    root.destroy()

def iniciar_busqueda_datos_usuario():
    global root, entry_correo, text_test, text_atencion, text_porcentaje_clasificacion

    root = tk.Tk()
    root.title("Resultados del Usuario")
    root.attributes("-fullscreen", True)
    root.configure(bg="#f0f0f0")

    label_titulo = tk.Label(root, text="RESULTADOS", font=("Arial", 24, "bold"), bg="#f0f0f0")
    label_titulo.pack(pady=20)

    frame_correo = tk.Frame(root, bg="#f0f0f0")
    frame_correo.pack(pady=10)

    label_correo = tk.Label(frame_correo, text="Ingrese su correo:", font=("Arial", 14), bg="#f0f0f0")
    label_correo.pack(side=tk.LEFT, padx=5)

    entry_correo = tk.Entry(frame_correo, width=40, font=("Arial", 14))
    entry_correo.pack(side=tk.LEFT, padx=5)

    button_buscar = tk.Button(frame_correo, text="Buscar Datos", font=("Arial", 12, "bold"), command=mostrar_resultados, bg="#4CAF50", fg="white")
    button_buscar.pack(side=tk.LEFT, padx=10)

    frame_resultados = tk.Frame(root, bg="#f0f0f0")
    frame_resultados.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

    frame_test = tk.Frame(frame_resultados, bg="white", bd=2, relief=tk.GROOVE)
    frame_test.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.BOTH, expand=True)

    label_test = tk.Label(frame_test, text="Resultados del Test", font=("Arial", 14, "bold"), bg="white")
    label_test.pack(pady=5)

    text_test = tk.Text(frame_test, height=10, width=40, font=("Arial", 12), state=tk.DISABLED, wrap="word")
    text_test.pack(pady=5, padx=5)

    frame_atencion = tk.Frame(frame_resultados, bg="white", bd=2, relief=tk.GROOVE)
    frame_atencion.pack(side=tk.RIGHT, padx=20, pady=10, fill=tk.BOTH, expand=True)

    label_atencion = tk.Label(frame_atencion, text="Resultados de Atención", font=("Arial", 14, "bold"), bg="white")
    label_atencion.pack(pady=5)

    text_atencion = tk.Text(frame_atencion, height=10, width=40, font=("Arial", 12), state=tk.DISABLED, wrap="word")
    text_atencion.pack(pady=5, padx=5)

    # Frame para porcentaje y clasificación juntos
    frame_porcentaje_clasificacion = tk.Frame(root, bg="white", bd=2, relief=tk.GROOVE)
    frame_porcentaje_clasificacion.pack(pady=10, padx=20, fill=tk.X)

    label_porcentaje_clasificacion = tk.Label(frame_porcentaje_clasificacion, text="Porcentaje y Clasificación de Atención", font=("Arial", 14, "bold"), bg="white")
    label_porcentaje_clasificacion.pack(pady=5)

    text_porcentaje_clasificacion = tk.Text(frame_porcentaje_clasificacion, height=4, width=50, font=("Arial", 14), state=tk.DISABLED, wrap="word")
    text_porcentaje_clasificacion.pack(pady=5)

    button_salir = tk.Button(root, text="Salir", font=("Arial", 14, "bold"), command=salir, bg="red", fg="white")
    button_salir.pack(pady=20)

    root.mainloop()
    connection.close()
