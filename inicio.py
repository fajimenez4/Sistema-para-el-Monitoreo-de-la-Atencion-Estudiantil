import tkinter as tk
from PIL import Image, ImageTk
from camara import abrir_ventana_camara
from test_d2r import iniciar_test
from resultados import iniciar_busqueda_datos_usuario
import os
import threading

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Monitoreo")
        self.root.attributes("-fullscreen", True)  
        self.root.configure(bg="white")
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.logo_photo = None 
        logo_path = "imagenes/logo.png"  
        if os.path.exists(logo_path):
            try:
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((1200, 600), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                self.logo_label = tk.Label(self.canvas, image=self.logo_photo, bg="white")
                self.logo_label.image = self.logo_photo  
                self.logo_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
            except Exception as e:
                print(f"Error al cargar la imagen del logo: {e}")
        else:
            print(f"El archivo de imagen no existe: {logo_path}")

        
        self.frame_botones = tk.Frame(self.canvas, bg="#BCB6FF", padx=70, pady=30)
        self.frame_botones.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        botones = [
            ("Iniciar", abrir_ventana_camara),
            ("Test D2R", self.ejecutar_test_d2r),
            ("Resultados", iniciar_busqueda_datos_usuario), 
            ("Salir", self.salir)
        ]

        self.botones_widgets = []  
        for texto, comando in botones:
            boton = tk.Button(
                self.frame_botones, text=texto, command=comando,
                bg="#5A4FCF", fg="white", font=("Arial", 14, "bold"),
                padx=20, pady=10, relief="raised", bd=5, width=15
            )
            boton.pack(side=tk.LEFT, padx=15)
            self.botones_widgets.append(boton)  

    def bloquear_interfaz(self):
        for boton in self.botones_widgets:
            boton.config(state=tk.DISABLED)

    def desbloquear_interfaz(self):
        for boton in self.botones_widgets:
            boton.config(state=tk.NORMAL)

    def ejecutar_test_d2r(self):
        self.bloquear_interfaz()
        
        def ejecutar():
            try:
                iniciar_test()
            except Exception as e:
                print(f"Error al ejecutar Test D2R: {e}")
            finally:
                self.root.after(100, self.desbloquear_interfaz) 

        hilo = threading.Thread(target=ejecutar, daemon=True)
        hilo.start()
    
    def salir(self):
        self.root.attributes("-fullscreen", False) 
        self.root.destroy()
        os._exit(0)

def abrir_ventana_principal():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
