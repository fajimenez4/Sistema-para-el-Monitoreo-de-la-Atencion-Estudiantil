import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import fitz  
import os

def mostrar_pdf(canvas):
    pdf_path = "documento/lectura.pdf"
    if not os.path.exists(pdf_path):
        messagebox.showerror("Error", f"El archivo PDF no existe: {pdf_path}")
        return
    
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
       
        if canvas_width < 100 or canvas_height < 100:
            canvas_width, canvas_height = 800, 600

        original_width, original_height = img.size
        new_width = canvas_width
        new_height = int(original_height * (new_width / original_width))

        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_resized)

        canvas.delete("all")
        x = canvas_width // 2
        y = 0
        canvas.create_image(x, y, anchor=tk.N, image=photo)
        canvas.image = photo
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir el archivo PDF: {e}")
