import tkinter as tk

class Calibrar:
    def __init__(self):  
        self.calibration_points = []
        self.reference_points = [(0.2, 0.2), (0.8, 0.2), (0.5, 0.5), (0.2, 0.8), (0.8, 0.8)]
        self.index = 0  

    def iniciar_calibracion(self, root, callback):
        self.calibration_points = []
        self.index = 0

        self.ventana_calibracion = tk.Toplevel(root)
        self.ventana_calibracion.attributes('-fullscreen', True)
        self.ventana_calibracion.bind('<Button-1>', self.on_click)

        self.canvas = tk.Canvas(self.ventana_calibracion, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.callback = callback  

        self.mostrar_siguiente_punto()

        self.ventana_calibracion.protocol("WM_DELETE_WINDOW", self.ventana_calibracion.destroy)

    def mostrar_siguiente_punto(self):
        self.canvas.delete("all")
        if self.index < len(self.reference_points):
            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            x, y = int(self.reference_points[self.index][0] * w), int(self.reference_points[self.index][1] * h)
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="red")
        else:
            self.ventana_calibracion.destroy()
            self.callback(self.calibration_points)

    def on_click(self, event):
        
        if self.index < len(self.reference_points):
            self.calibration_points.append((event.x, event.y))
            self.index += 1
            self.mostrar_siguiente_punto()

def iniciar_calibracion(root, callback):
    calibrador = Calibrar()
    calibrador.iniciar_calibracion(root, callback)
