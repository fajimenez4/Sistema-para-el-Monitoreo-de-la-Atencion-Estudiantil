import tkinter as tk
from tkinter import Frame, messagebox
from calibrar import iniciar_calibracion
from procesamiento import iniciar_camara, finalizar_analisis
from pdf import mostrar_pdf
from database import conexion_db

# Establecer conexión a la base de datos
connection = conexion_db()
cursor = connection.cursor()

# Crear tabla de atención en la base de datos si no existe
def tabla_atencion(connection):
    query = """
    CREATE TABLE IF NOT EXISTS atencion (
        id SERIAL PRIMARY KEY,
        correo VARCHAR(50) NOT NULL REFERENCES Usuarios(correo) ON DELETE CASCADE,
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

# Llamada para crear la tabla de atención
tabla_atencion(connection)

# Función para cerrar la ventana de cámara, mostrando advertencia si es necesario
def cerrar_ventana(ventana_camara):
    ventana_camara.destroy()

# Función principal para abrir la ventana de cámara y resultados
def abrir_ventana_camara(correo_usuario):
    ventana_camara = tk.Toplevel()
    ventana_camara.title("Ventana de Cámara y Resultados")
    ventana_camara.attributes('-fullscreen', True)  # Pantalla completa

    # Frame principal que contendrá todo el contenido
    frame_principal = Frame(ventana_camara, bg='#F0F0F0')
    frame_principal.pack(fill=tk.BOTH, expand=True)

    # Canvas donde se mostrará el PDF
    canvas_pdf = tk.Canvas(frame_principal, bg='white')
    canvas_pdf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Frame de la cámara donde se mostrará la imagen
    frame_camara = Frame(frame_principal, width=200, height=150, bg='black')
    frame_camara.pack_propagate(False)  # Impide que el tamaño cambie
    frame_camara.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=10)
    canvas_camara = tk.Canvas(frame_camara, bg='black', width=200, height=150)
    canvas_camara.pack()

    # Etiquetas para mostrar las métricas de fijaciones, sacadas, atención y tiempo
    fixation_label = tk.Label(frame_principal, text="Fijaciones: 0", bg='#BCB6FF', font=("Arial", 16, "bold"))
    fixation_label.pack(side=tk.TOP, pady=10)
    saccade_label = tk.Label(frame_principal, text="Sacadas: 0", bg='#BCB6FF', font=("Arial", 16, "bold"))
    saccade_label.pack(side=tk.TOP, pady=10)
    attention_label = tk.Label(frame_principal, text="Atención: 0%", bg='#BCB6FF', font=("Arial", 16, "bold"))
    attention_label.pack(side=tk.TOP, pady=10)
    time_label = tk.Label(frame_principal, text="Tiempo: 00:00", bg='#BCB6FF', font=("Arial", 16, "bold"))
    time_label.pack(side=tk.TOP, pady=10)

    # Frame donde se colocarán los botones de acción
    frame_botones = Frame(ventana_camara, bg='#BCB6FF', padx=20, pady=20)
    frame_botones.pack(side=tk.BOTTOM, pady=20)

    tiempos_fijacion = []  # Lista para almacenar tiempos de fijación
    tiempos_sacadicos = []  # Lista para almacenar tiempos de sacadas

    # Botón para iniciar la calibración
    boton_calibrar = tk.Button(frame_botones, text="Calibrar",
        command=lambda: iniciar_calibracion(ventana_camara, lambda puntos: boton_pdf.config(state=tk.NORMAL)),
        bg="#5A4FCF", fg="white", font=("Arial", 14, "bold"), width=15)
    boton_calibrar.pack(side=tk.LEFT, padx=10)

    # Botón para mostrar el PDF, que se habilita tras la calibración
    boton_pdf = tk.Button(frame_botones, text="Mostrar PDF", state=tk.DISABLED,
        command=lambda: [mostrar_pdf(canvas_pdf), boton_pdf.config(state=tk.DISABLED), boton_iniciar.config(state=tk.NORMAL) ],
        bg="#5A4FCF", fg="white", font=("Arial", 14, "bold"), width=15)
    boton_pdf.pack(side=tk.LEFT, padx=10)

    # Botón para iniciar la cámara, que se habilita tras la calibración
    boton_iniciar = tk.Button(frame_botones, text="Iniciar Cámara", state=tk.DISABLED,
        command=lambda: iniciar_camara(canvas_camara, fixation_label, saccade_label, attention_label, time_label, tiempos_fijacion, tiempos_sacadicos),
        bg="#5A4FCF", fg="white", font=("Arial", 14, "bold"), width=15)
    boton_iniciar.pack(side=tk.LEFT, padx=10)

    # Botón para finalizar el análisis
    boton_finalizar = tk.Button(frame_botones, text="Finalizar Análisis",
        command=lambda: finalizar_analisis(ventana_camara, correo_usuario, tiempos_fijacion, tiempos_sacadicos),
        bg="#5A4FCF", fg="white", font=("Arial", 14, "bold"), width=15)
    boton_finalizar.pack(side=tk.LEFT, padx=10)

    # Botón para cerrar la ventana de cámara
    boton_cerrar = tk.Button(frame_botones, text="Cerrar", command=lambda: cerrar_ventana(ventana_camara),
        bg="#FF0000", fg="white", font=("Arial", 14, "bold"), width=15)
    boton_cerrar.pack(side=tk.LEFT, padx=10)

    # Configura la acción de cerrar ventana con la X
    ventana_camara.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(ventana_camara, boton_finalizar))

    # Mantener la ventana abierta hasta que se cierre
    ventana_camara.mainloop()
