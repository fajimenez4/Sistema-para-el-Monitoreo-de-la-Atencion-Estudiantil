import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import fitz  
import os

# Función que maneja la carga y visualización de un archivo PDF en un lienzo (canvas)
def mostrar_pdf(canvas):
    pdf_path = "documento/lectura.pdf"  # Ruta del archivo PDF
    if not os.path.exists(pdf_path):  # Verifica si el archivo PDF existe
        messagebox.showerror("Error", f"El archivo PDF no existe: {pdf_path}")
        return
    
    try:
        # Intenta abrir el archivo PDF y cargar la primera página
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)  # Carga la primera página del documento
        pix = page.get_pixmap()  # Convierte la página a una imagen
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # Convierte el mapa de píxeles a una imagen

        # Obtiene las dimensiones del canvas
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
       
        # Ajusta las dimensiones mínimas del canvas si es necesario
        if canvas_width < 100 or canvas_height < 100:
            canvas_width, canvas_height = 800, 600

        # Calcula el tamaño adecuado de la imagen para ajustarse al canvas
        original_width, original_height = img.size
        new_width = canvas_width
        new_height = int(original_height * (new_width / original_width))

        # Redimensiona la imagen manteniendo su relación de aspecto
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_resized)

        # Limpia el canvas y coloca la imagen redimensionada en él
        canvas.delete("all")
        x = canvas_width // 2  # Centra la imagen en el canvas
        y = 0
        canvas.create_image(x, y, anchor=tk.N, image=photo)
        canvas.image = photo  # Mantiene una referencia a la imagen para evitar que sea recolectada por el recolector de basura
    except Exception as e:
        # Muestra un mensaje de error si ocurre algún problema al abrir el archivo PDF
        messagebox.showerror("Error", f"Error al abrir el archivo PDF: {e}")
