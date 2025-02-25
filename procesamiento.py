import cv2
import time
import tkinter as tk
from tkinter import messagebox
from gaze_tracking import GazeTracking
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from database import conexion_db

# Variables globales para la cámara
cap = None
camera_active = False

# Instancia de GazeTracking
gaze = GazeTracking()

def iniciar_camara(canvas_camara, fixation_label, saccade_label, attention_label,time_label, tiempos_fijacion, tiempos_sacadicos):
    global cap, camera_active, gaze

    if cap is not None:
        cap.release()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "No se pudo abrir la cámara")
        return

    camera_active = True
    previous_gaze = None
    fixation_start = None
    fixations = 0
    saccades = 0
    tiempos_fijacion.clear()
    tiempos_sacadicos.clear()
    total_fixation_time = 0
    total_saccade_time = 0

    def procesar_frame():
        nonlocal previous_gaze, fixation_start, fixations, saccades, total_fixation_time, total_saccade_time

        if camera_active:
            ret, frame = cap.read()
            if ret:
                gaze.refresh(frame)
                frame_rgb = gaze.annotated_frame()
                frame_rgb = cv2.cvtColor(frame_rgb, cv2.COLOR_BGR2RGB)

                if gaze.is_right() or gaze.is_left() or gaze.is_center():
                    current_gaze = gaze.horizontal_ratio()
                    if previous_gaze is not None:
                        movement = abs(current_gaze - previous_gaze)
                        current_time = time.time()
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

                total_time = total_fixation_time + total_saccade_time
                attention_percentage = (total_fixation_time / total_time) * 100 if total_time > 0 else 0

                minutos = int(total_time // 60)
                segundos = int(total_time % 60)
                tiempo_formateado = f"{minutos} min {segundos} seg" if minutos > 0 else f"{segundos} seg"

                frame_resized = cv2.resize(frame_rgb, (200, 150))
                img = Image.fromarray(frame_resized)
                photo = ImageTk.PhotoImage(img)
                canvas_camara.create_image(0, 0, anchor=tk.NW, image=photo)
                canvas_camara.image = photo

                fixation_label.config(text=f"Fijaciones: {fixations}")
                saccade_label.config(text=f"Sacadas: {saccades}")
                attention_label.config(text=f"Atención: {attention_percentage:.2f}%")
                time_label.config(text=f"Tiempo: {tiempo_formateado}")
            canvas_camara.after(10, procesar_frame)

    procesar_frame()

def analizar_movimientos_oculares(tiempos_fijacion, tiempos_sacadicos):
    if not tiempos_fijacion or not tiempos_sacadicos:
        return None

    global cap, camera_active
    camera_active = False
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

    promedio_fijacion = sum(tiempos_fijacion) / len(tiempos_fijacion) if tiempos_fijacion else 0
    promedio_sacadas = sum(tiempos_sacadicos) / len(tiempos_sacadicos) if tiempos_sacadicos else 0
    tiempo_total = sum(tiempos_fijacion) + sum(tiempos_sacadicos)
    atencion = (sum(tiempos_fijacion) / tiempo_total) * 100 if tiempo_total > 0 else 0

    return {
        "fijaciones": len(tiempos_fijacion),
        "sacadas": len(tiempos_sacadicos),
        "promedio_fijacion": promedio_fijacion,
        "promedio_sacadas": promedio_sacadas,
        "tiempo_total": tiempo_total,
        "atencion": atencion
    }

def mostrar_resultados(resultados):
    if not resultados:
        messagebox.showerror("Error", "No hay resultados para mostrar.")
        return

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

def graficar_atencion(resultados):
    if not resultados:
        return

    labels = ["Fijaciones", "Sacadas"]
    valores = [resultados["fijaciones"], resultados["sacadas"]]

    plt.bar(labels, valores, color=["blue", "red"])
    plt.title("Distribución de Fijaciones y Sacadas")
    plt.ylabel("Cantidad")
    plt.show()

def guardar_datos_atencion(resultados):
    connection = conexion_db()
    if connection is None:
        print("❌ No se pudo conectar a la base de datos.")
        return

    query = """
    INSERT INTO atencion (fijaciones, sacadas, promedio_fijacion, promedio_sacadas, tiempo_total, atencion)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (
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

def finalizar_analisis(ventana_camara, tiempos_fijacion, tiempos_sacadicos):
    global cap, camera_active
    if not camera_active:
        messagebox.showwarning("Advertencia", "La cámara no está activa.")
        return

    camera_active = False
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

    resultados = analizar_movimientos_oculares(tiempos_fijacion, tiempos_sacadicos)
    if resultados:
        mostrar_resultados(resultados)
        graficar_atencion(resultados)
        guardar_datos_atencion(resultados)
        ventana_camara.destroy()
    else:
        messagebox.showerror("Error", "No se pudieron analizar los resultados.")
