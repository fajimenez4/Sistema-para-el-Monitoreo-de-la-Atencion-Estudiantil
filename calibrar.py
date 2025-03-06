import tkinter as tk

# Clase que maneja el proceso de calibración del sistema de seguimiento ocular
class Calibrar:
    def __init__(self):  
        # Inicializa las variables necesarias para la calibración
        self.calibration_points = []
        self.reference_points = [(0.2, 0.2), (0.8, 0.2), (0.5, 0.5), (0.2, 0.8), (0.8, 0.8)]
        self.index = 0  

    # Inicia la calibración creando una ventana de calibración a pantalla completa
    def iniciar_calibracion(self, root, callback):
        self.calibration_points = [] 
        self.index = 0 

        # Crea una nueva ventana para la calibración
        self.ventana_calibracion = tk.Toplevel(root)
        self.ventana_calibracion.attributes('-fullscreen', True)
        self.ventana_calibracion.bind('<Button-1>', self.on_click)

        # Crea un lienzo donde se dibujarán los puntos de calibración
        self.canvas = tk.Canvas(self.ventana_calibracion, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Define el callback que se ejecutará al finalizar la calibración
        self.callback = callback  

        # Muestra el primer punto de calibración
        self.mostrar_siguiente_punto()

        # Asegura que la ventana se cierre correctamente cuando el usuario la cierre
        self.ventana_calibracion.protocol("WM_DELETE_WINDOW", self.ventana_calibracion.destroy)

    # Muestra el siguiente punto de calibración o finaliza el proceso
    def mostrar_siguiente_punto(self):
        self.canvas.delete("all") 
        # Si hay más puntos de calibración por mostrar, los dibuja
        if self.index < len(self.reference_points):
            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            x, y = int(self.reference_points[self.index][0] * w), int(self.reference_points[self.index][1] * h)
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="red")
        else:
            # Si ya no quedan puntos, cierra la ventana y ejecuta el callback
            self.ventana_calibracion.destroy()
            self.callback(self.calibration_points)

    # Función que se ejecuta cuando el usuario hace clic en el lienzo
    def on_click(self, event):
        # Registra el punto de clic si aún hay puntos de calibración por mostrar
        if self.index < len(self.reference_points):
            self.calibration_points.append((event.x, event.y))
            self.index += 1
            self.mostrar_siguiente_punto()

# Función que inicia el proceso de calibración desde afuera de la clase
def iniciar_calibracion(root, callback):
    calibrador = Calibrar() 
    calibrador.iniciar_calibracion(root, callback)  
