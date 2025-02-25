import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import psycopg2
import re
from inicio import App
from database import conexion_db

connection = conexion_db()
cursor = connection.cursor()

def tabla_usuarios(connection):
    query = """
    CREATE TABLE IF NOT EXISTS Usuarios (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(30) NOT NULL,
        apellido VARCHAR(30) NOT NULL,
        correo VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(30) NOT NULL
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
    except Exception as e:
        print(f"❌ Error creando la tabla 'Usuarios': {e}")

tabla_usuarios(connection)
    
class LoginRegisterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inicio de Sesión")
        self.root.attributes("-fullscreen", True)  
        self.usuario_email = None 
        try:
            self.bg_image = Image.open("imagenes/fondo.png")  
            self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen de fondo: {e}")
            self.bg_image_tk = None
        self.bg_label = tk.Label(self.root, image=self.bg_image_tk)
        self.bg_label.image = self.bg_image_tk  
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.bind("<Configure>", self.resize_background)
        self.root.bind("<Escape>", self.salir)  
        self.create_login_widgets()
        self.root.bind("<Return>", self.on_enter)

    def resize_background(self, event=None):
        new_width = self.root.winfo_width()
        new_height = self.root.winfo_height()
        resized_image = self.bg_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.bg_image_tk = ImageTk.PhotoImage(resized_image)
        self.bg_label.config(image=self.bg_image_tk)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            if widget != self.bg_label:
                widget.destroy()

    def create_login_widgets(self):
        self.clear_frame()
        login_frame = tk.Frame(self.root, bg="white", padx=40, pady=30)
        login_frame.place(relx=0.3, rely=0.5, anchor="center")
        tk.Label(login_frame, text="Iniciar Sesión", font=("Arial", 20, "bold"), bg="white", fg="#0078D7").pack(pady=(0, 20))
        tk.Label(login_frame, text="Correo Electrónico", font=("Arial", 12, "bold"), bg="white").pack()
        self.email_entry = tk.Entry(login_frame, font=("Arial", 12), width=30)
        self.email_entry.pack(pady=(0, 10))
        tk.Label(login_frame, text="Contraseña", font=("Arial", 12, "bold"), bg="white").pack()
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), width=30, show="*")
        self.password_entry.pack(pady=(0, 20))
        tk.Button(login_frame, text="Entrar", font=("Arial", 12), bg="#0078D7", fg="white", width=15, command=self.login).pack()
        register_frame = tk.Frame(self.root, bg="#0078D7", padx=40, pady=30)
        register_frame.place(relx=0.7, rely=0.5, anchor="center")
        tk.Label(register_frame, text="¿Aún no tienes una cuenta?", font=("Arial", 16, "bold"), bg="#0078D7", fg="white").pack(pady=(0, 10))
        tk.Label(register_frame, text="Regístrate para iniciar sesión", font=("Arial", 12), bg="#0078D7", fg="white").pack()
        tk.Button(register_frame, text="Registrarse", font=("Arial", 12), fg="white", bg="#005bb5", width=15, command=self.create_register_widgets).pack(pady=20)

    def create_register_widgets(self):
        self.clear_frame()
        left_frame = tk.Frame(self.root, bg="#0078D7", padx=40, pady=30)
        left_frame.place(relx=0.3, rely=0.5, anchor="center")
        tk.Label(left_frame, text="¿Ya tienes cuenta?", font=("Arial", 16, "bold"), bg="#0078D7", fg="white").pack(pady=(0, 10))
        tk.Label(left_frame, text="Inicia sesión", font=("Arial", 12), bg="#0078D7", fg="white").pack()
        tk.Button(left_frame, text="Iniciar Sesión", font=("Arial", 12), fg="white", bg="#005bb5", width=15, command=self.create_login_widgets).pack(pady=20)
        register_frame = tk.Frame(self.root, bg="white", padx=40, pady=30)
        register_frame.place(relx=0.7, rely=0.5, anchor="center")
        tk.Label(register_frame, text="Registro de Usuario", font=("Arial", 20, "bold"), bg="white", fg="#0078D7").pack(pady=(0, 20))
        tk.Label(register_frame, text="Nombre", font=("Arial", 12, "bold"), bg="white").pack()
        self.nombre_entry = tk.Entry(register_frame, font=("Arial", 12), width=30)
        self.nombre_entry.pack(pady=(0, 10))
        tk.Label(register_frame, text="Apellido", font=("Arial", 12, "bold"), bg="white").pack()
        self.apellido_entry = tk.Entry(register_frame, font=("Arial", 12), width=30)
        self.apellido_entry.pack(pady=(0, 10))
        tk.Label(register_frame, text="Correo Electrónico", font=("Arial", 12, "bold"), bg="white").pack()
        self.email_reg_entry = tk.Entry(register_frame, font=("Arial", 12), width=30)
        self.email_reg_entry.pack(pady=(0, 10))
        tk.Label(register_frame, text="Contraseña", font=("Arial", 12, "bold"), bg="white").pack()
        self.password_reg_entry = tk.Entry(register_frame, font=("Arial", 12), width=30, show="*")
        self.password_reg_entry.pack(pady=(0, 20))
        tk.Button(register_frame, text="Registrar", font=("Arial", 12), bg="#0078D7", fg="white", width=15, command=self.register_user).pack(pady=10)

    def register_user(self):
        nombre = self.nombre_entry.get()
        apellido = self.apellido_entry.get()
        correo = self.email_reg_entry.get()
        password = self.password_reg_entry.get()

        if not nombre or not apellido or not correo or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if not self.validar_email(correo):
            messagebox.showerror("Error", "Correo electrónico no válido.")
            return

        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO Usuarios (nombre, apellido, correo, password) VALUES (%s, %s, %s, %s)",
                (nombre, apellido, correo, password)
            )
            connection.commit()  
            cursor.close()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            self.create_login_widgets() 
        except psycopg2.IntegrityError:
            messagebox.showerror("Error", "El correo electrónico ya está registrado.")
        except Exception as e:
            messagebox.showerror("Error", f"Hubo un error con la base de datos: {e}")

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if not email or not password:
            messagebox.showerror("Error", "Ingrese su correo y contraseña.")
            return
        
        if not self.validar_email(email):
            messagebox.showerror("Error", "Correo inválido.")
            return
        
        try:
            cursor = connection.cursor()  
            cursor.execute("SELECT * FROM Usuarios WHERE correo=%s AND password=%s", (email, password))
            user = cursor.fetchone()
            cursor.close()
            if user:
                messagebox.showinfo("Éxito", f"Bienvenido {user[1]} {user[2]}!")
                self.clear_frame()
                self.root.withdraw()
                app_window = tk.Toplevel(self.root)
                app = App(app_window) 
            else:
                messagebox.showerror("Error", "Credenciales incorrectas.")
        except Exception as e:
            messagebox.showerror("Error", f"Problema con la base de datos: {e}")

    def on_enter(self, event=None):
        if self.email_entry.get() and self.password_entry.get():  
            self.login()
        elif self.nombre_entry.get() and self.apellido_entry.get(): 
            self.register_user()

    def validar_email(self, email):
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

    def clear_fields(self):
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
    
    def salir(self, event=None):
        self.root.quit()

def iniciar_login():
    root = tk.Tk()
    app = LoginRegisterApp(root)
    root.mainloop()
