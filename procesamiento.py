# Importación de las bibliotecas necesarias
import cv2
import time
import tkinter as tk
from tkinter import messagebox
from gaze_tracking import GazeTracking
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from database import conexion_db

# Inicialización de variables globales
cap = None  # Variable para la cámara
camera_active = False  # Estado de la cámara
gaze = GazeTracking()  # Instancia para el seguimiento ocular

# Función para iniciar la cámara y procesar los movimientos oculares
def iniciar_camara(canvas_camara, fixation_label, saccade_label, attention_label, time_label, tiempos_fijacion, tiempos_sacadicos):
    global cap, camera_active, gaze

    # Libera la cámara si está abierta
    if cap is not None:
        cap.release()

    # Inicia la cámara
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "No se pudo abrir la cámara")
        return

    # Activa la cámara y restablece variables
    camera_active = True
    previous_gaze = None
    fixation_start = None
    fixations = 0
    saccades = 0
    tiempos_fijacion.clear()
    tiempos_sacadicos.clear()
    total_fixation_time = 0
    total_saccade_time = 0

    # Función interna para procesar cada frame de la cámara
    def procesar_frame():
        nonlocal previous_gaze, fixation_start, fixations, saccades, total_fixation_time, total_saccade_time

        if camera_active:
            ret, frame = cap.read()
            if ret:
                # Actualiza la información de la mirada
                gaze.refresh(frame)
                frame_rgb = gaze.annotated_frame()
                frame_rgb = cv2.cvtColor(frame_rgb, cv2.COLOR_BGR2RGB)

                # Compara los movimientos de la mirada y calcula fijaciones y sacadas
                if gaze.is_right() or gaze.is_left() or gaze.is_center():
                    current_gaze = gaze.horizontal_ratio()
                    if previous_gaze is not None:
                        movement = abs(current_gaze - previous_gaze)
                        current_time = time.time()
                        # Condiciones para detectar fijaciones y sacadas
                        if movement < 0.05:
                            if fixation_start is None:
                                fixation_start = current_time
                            elif (current_time - fixation_start) > 0.2:
                                if (current_time - fixation_start) < 0.3:
                                    fixations += 1
                                    tiempos_fijacion.append(current_time - fixation_start)
                                    total_fixation_time += (current_time - fixation_start)
                                fixation_start = None
                        else:
                            if fixation_start is not None:
                                if 0.1 < (current_time - fixation_start) < 0.2:
                                    saccades += 1
                                    tiempos_sacadicos.append(current_time - fixation_start)
                                    total_saccade_time += (current_time - fixation_start)
                    previous_gaze = current_gaze

                # Calcula el porcentaje de atención
                total_time = total_fixation_time + total_saccade_time
                attention_percentage = (total_fixation_time / total_time) * 100 if total_time > 0 else 0

                # Muestra los resultados en la interfaz gráfica
                minutos = int(total_time // 60)
                segundos = int(total_time % 60)
                tiempo_formateado = f"{minutos} min {segundos} seg" if minutos > 0 else f"{segundos} seg"

                # Redimensiona la imagen y la muestra en el canvas
                frame_resized = cv2.resize(frame_rgb, (200, 150))
                img = Image.fromarray(frame_resized)
                photo = ImageTk.PhotoImage(img)
                canvas_camara.create_image(0, 0, anchor=tk.NW, image=photo)
                canvas_camara.image = photo

                # Actualiza las etiquetas con la información de fijaciones, sacadas, atención y tiempo
                fixation_label.config(text=f"Fijaciones: {fixations}")
                saccade_label.config(text=f"Sacadas: {saccades}")
                attention_label.config(text=f"Atención: {attention_percentage:.2f}%")
                time_label.config(text=f"Tiempo: {tiempo_formateado}")
            # Llama a la función procesar_frame nuevamente después de 10ms
            canvas_camara.after(10, procesar_frame)

    # Inicia el procesamiento de los frames
    procesar_frame()

# Función para analizar los resultados de los movimientos oculares
def analizar_movimientos_oculares(tiempos_fijacion, tiempos_sacadicos):
    if not tiempos_fijacion or not tiempos_sacadicos:
        return None

    # Detiene la cámara y procesa los resultados
    global cap, camera_active
    camera_active = False
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

    # Calcula los promedios y la atención
    promedio_fijacion = sum(tiempos_fijacion) / len(tiempos_fijacion) if tiempos_fijacion else 0
    promedio_sacadas = sum(tiempos_sacadicos) / len(tiempos_sacadicos) if tiempos_sacadicos else 0
    tiempo_total = sum(tiempos_fijacion) + sum(tiempos_sacadicos)
    atencion = (sum(tiempos_fijacion) / tiempo_total) * 100 if tiempo_total > 0 else 0

    # Retorna un diccionario con los resultados
    return {
        "fijaciones": len(tiempos_fijacion),
        "sacadas": len(tiempos_sacadicos),
        "promedio_fijacion": promedio_fijacion,
        "promedio_sacadas": promedio_sacadas,
        "tiempo_total": tiempo_total,
        "atencion": atencion
    }

# Función para mostrar los resultados analizados en una ventana emergente
def mostrar_resultados(resultados):
    if not resultados:
        messagebox.showerror("Error", "No hay resultados para mostrar.")
        return

    # Formatea el tiempo total y muestra los resultados
    minutos = int(resultados["tiempo_total"] // 60)
    segundos = int(resultados["tiempo_total"] % 60)
    tiempo_formateado = f"{minutos} min {segundos} seg" if minutos > 0 else f"{segundos} seg"

    mensaje = (
        f"Fijaciones: {resultados['fijaciones']}\n"
        f"Sacadas: {resultados['sacadas']}\n"
        f"Promedio de fijación: {resultados['promedio_fijacion']:.2f} seg\n"
        f"Promedio de sacadas: {resultados['promedio_sacadas']:.2f} seg\n"
        f"Tiempo total: {tiempo_formateado}\n"
        f"Atención: {resultados['atencion']:.2f}%"
    )
    messagebox.showinfo("Resultados del Análisis", mensaje)

# Función para graficar los resultados de atención
def graficar_atencion(resultados):
    if not resultados:
        return

    # Crea una gráfica de barras para fijaciones y sacadas
    labels = ["Fijaciones", "Sacadas"]
    valores = [resultados["fijaciones"], resultados["sacadas"]]

    plt.bar(labels, valores, color=["blue", "red"])
    plt.title("Distribución de Fijaciones y Sacadas")
    plt.ylabel("Cantidad")
    plt.show()

# Función para guardar los resultados en la base de datos
def guardar_datos_atencion(correo, resultados):
    connection = conexion_db()
    cursor = connection.cursor()
    if connection is None:
        print("❌ No se pudo conectar a la base de datos.")
        return

    # Inserta los resultados en la base de datos
    query = """
    INSERT INTO atencion (correo, fijaciones, sacadas, promedio_fijacion, promedio_sacadas, tiempo_total, atencion)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (
                correo,
                resultados["fijaciones"],
                resultados["sacadas"],
                resultados["promedio_fijacion"],
                resultados["promedio_sacadas"],
                resultados["tiempo_total"],
                resultados["atencion"]
            ))
            connection.commit()
    except Exception as e:
        print(f"❌ Error al guardar los datos en 'atencion': {e}")
    finally:
        connection.close()

# Función para finalizar el análisis y cerrar la ventana
def finalizar_analisis(ventana_camara, correo, tiempos_fijacion, tiempos_sacadicos):
    global cap, camera_active
    if not camera_active:
        return

    # Detiene la cámara y procesa los resultados
    camera_active = False
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

    resultados = analizar_movimientos_oculares(tiempos_fijacion, tiempos_sacadicos)
    if resultados:
        mostrar_resultados(resultados)
        graficar_atencion(resultados)
        guardar_datos_atencion(correo, resultados)  
        ventana_camara.destroy()
    else:
        messagebox.showerror("Error", "No se pudieron analizar los resultados.")
