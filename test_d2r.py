import tkinter as tk
from tkinter import messagebox
import random
from database import conexion_db

connection = conexion_db()
cursor = connection.cursor()

def tabla_test(connection):
    query = """
    CREATE TABLE IF NOT EXISTS Test (
        id SERIAL PRIMARY KEY,
        total INT NOT NULL,
        aciertos INT NOT NULL,
        errores INT NOT NULL,
        indice_concentracion FLOAT NOT NULL
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
    except Exception as e:
        print(f"❌ Error creando la tabla 'ResultadosTest': {e}")

tabla_test(connection)

FILAS = 17
COLUMNAS = 47
SELECCIONADOS = set()
TIEMPO_POR_FILA = 20
TOT = 0
TA = 0
errores_omision = 0
errores_comision = 0

def generar_caracter():
    return random.choice(['d', "d'", "d''"])

def seleccionar(index):
    global TOT
    btn = botones[index]
    
    if btn["state"] == "disabled":
        return
    
    if index not in SELECCIONADOS:
        SELECCIONADOS.add(index)
        btn.config(bg="#808080")  
        TOT += 1

def bloquear_fila(fila):
    global TA, errores_comision, errores_omision
    
    for col in range(COLUMNAS):
        index = fila * COLUMNAS + col
        btn = botones[index]
        btn.config(state="disabled")
        
        if index in SELECCIONADOS:
            if btn["text"] == "d''":
                btn.config(bg="green")
                TA += 1
            else:
                btn.config(bg="red")
                errores_comision += 1
        else:
            if btn["text"] == "d''":
                btn.config(bg="red")
                errores_omision += 1
    
    if fila + 1 < FILAS:
        habilitar_fila(fila + 1)
    else:
        finalizar_btn.config(state="normal")

def habilitar_fila(fila):
    for i in range(FILAS):
        for col in range(COLUMNAS):
            index = i * COLUMNAS + col
            botones[index].config(state="normal" if i == fila else "disabled")
    temporizador_fila(fila, TIEMPO_POR_FILA)

def temporizador_fila(fila, tiempo_restante):
    temporizador_label.config(text=f"Tiempo restante: {tiempo_restante} segundos")
    
    if tiempo_restante > 0:
        root.after(1000, temporizador_fila, fila, tiempo_restante - 1)
    else:
        bloquear_fila(fila)

def guardar_resultados():
    try:
        with connection.cursor() as cursor:
            # Según el manual del test D2-R:
            # total_targets es la cantidad total de d'' que debieron ser marcadas (aciertos + omisiones)
            total_targets = TA + errores_omision
            neto = TA - errores_comision
            if neto < 0:
                neto = 0
            IC = (neto / total_targets * 100) if total_targets > 0 else 0

            query = """
            INSERT INTO Test (total, aciertos, errores, indice_concentracion)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (TOT, TA, errores_comision + errores_omision, IC))
            connection.commit()
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar los resultados: {e}")

def mostrar_resultados():
    global root
    guardar_resultados()
    
    total_targets = TA + errores_omision
    neto = TA - errores_comision
    if neto < 0:
        neto = 0
    IC = (neto / total_targets * 100) if total_targets > 0 else 0
    
    mensaje = (f"Total de caracteres revisados: {TOT}\n"
               f"Total de aciertos: {TA}\n"
               f"Total de errores: {errores_comision + errores_omision}\n"
               f"Índice de concentración: {IC:.2f}%")
    
    messagebox.showinfo("Resultados del Test", mensaje)
    root.destroy()  

def finalizar_test():
    mostrar_resultados()

def iniciar_test():
    global root, botones, finalizar_btn, temporizador_label
    root = tk.Tk()
    root.title("Test D2-R")
    root.attributes('-fullscreen', True)
    root.configure(bg="black")
    main_frame = tk.Frame(root, bg="black")
    main_frame.pack(expand=True, fill=tk.BOTH)

    frame_superior = tk.Frame(main_frame, bg="black")
    frame_superior.pack(pady=5)
    instrucciones = tk.Label(frame_superior, text="Test D2-R: Selecciona todas las d'' ", font=("Arial", 18), fg="white", bg="black")
    instrucciones.pack()

    temporizador_frame = tk.Frame(main_frame, bg="black")
    temporizador_frame.pack(pady=10)
    temporizador_label = tk.Label(temporizador_frame, text="Tiempo restante: 20 segundos", font=("Arial", 16), fg="white", bg="black")
    temporizador_label.pack()

    frame_matriz = tk.Frame(main_frame, bg="black")
    frame_matriz.pack(expand=True, fill=tk.BOTH)

    for i in range(COLUMNAS):
        frame_matriz.grid_columnconfigure(i, weight=1)
    for i in range(FILAS):
        frame_matriz.grid_rowconfigure(i, weight=1)

    botones = []
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            index = fila * COLUMNAS + col
            texto = generar_caracter()
            btn = tk.Button(frame_matriz, text=texto, width=2, height=1, font=("Arial", 11),
                            bg="gray20", fg="white", relief="ridge", bd=2, justify="center",
                            command=lambda i=index: seleccionar(i))
            btn.grid(row=fila, column=col, padx=0.3, pady=0.3, sticky="nsew")
            botones.append(btn)

    # Deshabilitamos todos los botones inicialmente
    for btn in botones:
        btn.config(state="disabled")

    frame_inferior = tk.Frame(main_frame, bg="black")
    frame_inferior.pack(pady=10)
    
    # Botón Iniciar: al hacer clic, se habilita la primera fila y comienza el temporizador
    iniciar_btn = tk.Button(frame_inferior, text="Iniciar", command=lambda: comenzar_test(), font=("Arial", 16), bg="green", fg="white", padx=15, pady=5, relief="ridge", bd=3)
    iniciar_btn.pack(side="left", padx=5)

    finalizar_btn = tk.Button(frame_inferior, text="Finalizar Test", command=finalizar_test, font=("Arial", 16), bg="orange", fg="white", padx=15, pady=5, relief="ridge", bd=3)
    finalizar_btn.pack(side="left", padx=5)
    finalizar_btn.config(state="disabled")

    def comenzar_test():
        iniciar_btn.config(state="disabled")
        habilitar_fila(0)

    root.mainloop()
