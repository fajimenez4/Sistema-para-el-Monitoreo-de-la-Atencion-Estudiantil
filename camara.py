import tkinter as tk
from tkinter import Frame, messagebox
from calibrar import iniciar_calibracion
from procesamiento import iniciar_camara, finalizar_analisis
from pdf import mostrar_pdf
from database import conexion_db

# Establecer conexión a la base de datos
connection = conexion_db()
cursor = connection.cursor()

#Crear tala de atencion
def tabla_atencion(connection):
    query = """
    CREATE TABLE IF NOT EXISTS atencion (
        id SERIAL PRIMARY KEY,
        fijaciones INT NOT NULL,
        sacadas INT NOT NULL,
        promedio_fijacion FLOAT NOT NULL,
        promedio_sacadas FLOAT NOT NULL,
        tiempo_total FLOAT NOT NULL,
        atencion FLOAT NOT NULL
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)

    except Exception as e:
        print(f"❌ Error creando la tabla 'atencion': {e}")

tabla_atencion(connection)

# Función para habilitar el botón de mostrar PDF después de calibrar
def habilitar_boton_pdf(boton_calibrar, boton_pdf, puntos):
    boton_calibrar.config(state=tk.DISABLED)
    boton_pdf.config(state=tk.NORMAL)
    messagebox.showinfo("Calibración Completada", f"Calibración completada con los puntos: {puntos}")

# Función para habilitar el botón de iniciar cámara después de mostrar el PDF
def habilitar_boton_iniciar_camara(boton_iniciar):
    boton_iniciar.config(state=tk.NORMAL)

# Función para manejar el clic en "Mostrar PDF"
def manejar_boton_pdf(boton_pdf, boton_iniciar, canvas_pdf):
    # Mostrar el PDF
    mostrar_pdf(canvas_pdf)
    # Deshabilitar el botón de mostrar PDF
    boton_pdf.config(state=tk.DISABLED)
    # Habilitar el botón de iniciar cámara
    habilitar_boton_iniciar_camara(boton_iniciar)

# Función para mostrar advertencia si se intenta realizar una acción sin los pasos anteriores
def advertencia_sin_calibracion():
    messagebox.showwarning("Advertencia", "Por favor, realiza la calibración primero.")

def abrir_ventana_camara():
    ventana_camara = tk.Toplevel()
    ventana_camara.title("Ventana de Cámara y Resultados")
    ventana_camara.attributes('-fullscreen', True)

    frame_principal = Frame(ventana_camara, bg='#F0F0F0')
    frame_principal.pack(fill=tk.BOTH, expand=True)

    canvas_pdf = tk.Canvas(frame_principal, bg='white')
    canvas_pdf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    frame_camara = Frame(frame_principal, width=200, height=150, bg='black')
    frame_camara.pack_propagate(False)
    frame_camara.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=10)

    canvas_camara = tk.Canvas(frame_camara, bg='black', width=200, height=150)
    canvas_camara.pack()

    # Definir las etiquetas
    fixation_label = tk.Label(frame_principal, text="Fijaciones: 0", bg='#BCB6FF', font=("Arial", 16, "bold"))
    fixation_label.pack(side=tk.TOP, pady=10)

    saccade_label = tk.Label(frame_principal, text="Sacadas: 0", bg='#BCB6FF', font=("Arial", 16, "bold"))
    saccade_label.pack(side=tk.TOP, pady=10)

    attention_label = tk.Label(frame_principal, text="Atención: 0%", bg='#BCB6FF', font=("Arial", 16, "bold"))
    attention_label.pack(side=tk.TOP, pady=10)

    time_label = tk.Label(frame_principal, text="Tiempo: 00:00", bg='#BCB6FF', font=("Arial", 16, "bold"))
    time_label.pack(side=tk.TOP, pady=10)

    frame_botones = Frame(ventana_camara, bg='#BCB6FF', padx=20, pady=20)
    frame_botones.pack(side=tk.BOTTOM, pady=20)

    # Definir las listas de análisis en este ámbito
    tiempos_fijacion = []
    tiempos_sacadicos = []

    # Botón para calibrar
    boton_calibrar = tk.Button(
        frame_botones, text="Calibrar",
        command=lambda: iniciar_calibracion(ventana_camara, lambda puntos: habilitar_boton_pdf(boton_calibrar, boton_pdf, puntos)),
        bg="#5A4FCF", fg="white", font=("Arial", 14, "bold"),
        padx=20, pady=10, relief="raised", bd=5, width=15
    )
    boton_calibrar.pack(side=tk.LEFT, padx=10)

    # Botón para mostrar el PDF
    boton_pdf = tk.Button(
        frame_botones, text="Mostrar PDF", command=lambda: manejar_boton_pdf(boton_pdf, boton_iniciar, canvas_pdf),
        bg="#5A4FCF", fg="white", font=("Arial", 14, "bold"),
        padx=20, pady=10, relief="raised", bd=5, width=15, state=tk.DISABLED
    )
    boton_pdf.pack(side=tk.LEFT, padx=10)

    # Botón para iniciar la cámara
    boton_iniciar = tk.Button(
        frame_botones, text="Iniciar Cámara",
        command=lambda: iniciar_camara(canvas_camara, fixation_label, saccade_label, attention_label, time_label, tiempos_fijacion, tiempos_sacadicos),
        bg="#5A4FCF", fg="white", font=("Arial", 14, "bold"),
        padx=20, pady=10, relief="raised", bd=5, width=15, state=tk.DISABLED
    )
    boton_iniciar.pack(side=tk.LEFT, padx=10)

    # Botón para finalizar el análisis y mostrar los resultados
    boton_finalizar = tk.Button(
        frame_botones, text="Finalizar Análisis",
        command=lambda: finalizar_analisis(ventana_camara, tiempos_fijacion, tiempos_sacadicos),
        bg="#5A4FCF", fg="white", font=("Arial", 14, "bold"),
        padx=20, pady=10, relief="raised", bd=5, width=15
    )
    boton_finalizar.pack(side=tk.LEFT, padx=10)

    # Botón para cerrar la ventana
    boton_cerrar = tk.Button(
        frame_botones, text="Cerrar", command=ventana_camara.destroy,
        bg="#FF0000", fg="white", font=("Arial", 14, "bold"),
        padx=20, pady=10, relief="raised", bd=5, width=15
    )
    boton_cerrar.pack(side=tk.LEFT, padx=10)

    ventana_camara.mainloop()
