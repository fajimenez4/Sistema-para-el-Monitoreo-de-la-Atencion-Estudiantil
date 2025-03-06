import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import psycopg2
import re
from inicio import abrir_ventana_principal
from database import conexion_db

# Establecer conexión a la base de datos
connection = conexion_db()
cursor = connection.cursor()

# Clase principal que maneja la interfaz gráfica para el inicio de sesión y registro
class LoginRegisterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inicio de Sesión")  # Título de la ventana
        self.root.attributes("-fullscreen", True)  # Hacer la ventana de pantalla completa
        self.usuario_email = None 
        try:
            # Intentar cargar la imagen de fondo
            self.bg_image = Image.open("imagenes/fondo.png")
            self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
        except Exception as e:
            # Mostrar error si no se puede cargar la imagen
            messagebox.showerror("Error", f"No se pudo cargar la imagen de fondo: {e}")
            self.bg_image_tk = None
        # Crear un label con la imagen de fondo
        self.bg_label = tk.Label(self.root, image=self.bg_image_tk)
        self.bg_label.image = self.bg_image_tk
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        # Vincular la función de redimensionar la imagen con el evento de redimensionado de la ventana
        self.root.bind("<Configure>", self.resize_background)
        # Asignar la función de salir a la tecla Escape
        self.root.bind("<Escape>", self.salir)  
        # Crear los widgets para el inicio de sesión
        self.create_login_widgets()
        # Asignar la tecla Enter para iniciar sesión o registro
        self.root.bind("<Return>", self.on_enter)

    # Función que redimensiona la imagen de fondo cuando cambia el tamaño de la ventana
    def resize_background(self, event=None):
        new_width = self.root.winfo_width()
        new_height = self.root.winfo_height()
        resized_image = self.bg_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.bg_image_tk = ImageTk.PhotoImage(resized_image)
        self.bg_label.config(image=self.bg_image_tk)

    # Función para limpiar los widgets existentes antes de crear nuevos
    def clear_frame(self):
        for widget in self.root.winfo_children():
            if widget != self.bg_label:
                widget.destroy()

    # Crear los widgets del inicio de sesión
    def create_login_widgets(self):
        self.clear_frame()
        # Frame que contiene los widgets del formulario de inicio de sesión
        login_frame = tk.Frame(self.root, bg="white", padx=40, pady=30)
        login_frame.place(relx=0.3, rely=0.5, anchor="center")
        tk.Label(login_frame, text="Iniciar Sesión", font=("Arial", 20, "bold"), bg="white", fg="#0078D7").pack(pady=(0, 20))
        tk.Label(login_frame, text="Correo Electrónico", font=("Arial", 12, "bold"), bg="white").pack()
        # Campo de entrada para el correo electrónico
        self.email_entry = tk.Entry(login_frame, font=("Arial", 12), width=30)
        self.email_entry.pack(pady=(0, 10))
        tk.Label(login_frame, text="Contraseña", font=("Arial", 12, "bold"), bg="white").pack()
        # Campo de entrada para la contraseña (oculta)
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), width=30, show="*")
        self.password_entry.pack(pady=(0, 20))
        # Botón de "Entrar" que ejecuta la función de login
        tk.Button(login_frame, text="Entrar", font=("Arial", 12), bg="#0078D7", fg="white", width=15, command=self.login).pack()
        # Frame para el registro de nuevo usuario
        register_frame = tk.Frame(self.root, bg="#0078D7", padx=40, pady=30)
        register_frame.place(relx=0.7, rely=0.5, anchor="center")
        tk.Label(register_frame, text="¿Aún no tienes una cuenta?", font=("Arial", 16, "bold"), bg="#0078D7", fg="white").pack(pady=(0, 10))
        tk.Label(register_frame, text="Regístrate para iniciar sesión", font=("Arial", 12), bg="#0078D7", fg="white").pack()
        # Botón para redirigir a la vista de registro
        tk.Button(register_frame, text="Registrarse", font=("Arial", 12), fg="white", bg="#005bb5", width=15, command=self.create_register_widgets).pack(pady=20)

    # Crear los widgets para el registro de un nuevo usuario
    def create_register_widgets(self):
        self.clear_frame()
        # Frame para los widgets del registro (lado izquierdo)
        left_frame = tk.Frame(self.root, bg="#0078D7", padx=40, pady=30)
        left_frame.place(relx=0.3, rely=0.5, anchor="center")
        tk.Label(left_frame, text="¿Ya tienes cuenta?", font=("Arial", 16, "bold"), bg="#0078D7", fg="white").pack(pady=(0, 10))
        tk.Label(left_frame, text="Inicia sesión", font=("Arial", 12), bg="#0078D7", fg="white").pack()
        # Botón para regresar al inicio de sesión
        tk.Button(left_frame, text="Iniciar Sesión", font=("Arial", 12), fg="white", bg="#005bb5", width=15, command=self.create_login_widgets).pack(pady=20)
        # Frame para el formulario de registro (lado derecho)
        register_frame = tk.Frame(self.root, bg="white", padx=40, pady=30)
        register_frame.place(relx=0.7, rely=0.5, anchor="center")
        tk.Label(register_frame, text="Registro de Usuario", font=("Arial", 20, "bold"), bg="white", fg="#0078D7").pack(pady=(0, 20))
        # Campos de entrada para el registro
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
        # Botón para registrar al usuario
        tk.Button(register_frame, text="Registrar", font=("Arial", 12), bg="#0078D7", fg="white", width=15, command=self.register_user).pack(pady=10)

    # Función para registrar al nuevo usuario en la base de datos
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
            # Insertar el usuario en la base de datos
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

    # Función para iniciar sesión
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
            # Verificar las credenciales del usuario en la base de datos
            cursor = connection.cursor()  
            cursor.execute("SELECT * FROM Usuarios WHERE correo=%s AND password=%s", (email, password))
            user = cursor.fetchone()
            if user:
                messagebox.showinfo("Éxito", f"Bienvenido {user[1]} {user[2]}!")
                self.root.destroy()
                abrir_ventana_principal(email)
            else:
                messagebox.showerror("Error", "Credenciales incorrectas.")
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Problema con la base de datos: {e}")

    # Función para manejar el evento de presionar Enter
    def on_enter(self, event=None):
        if self.email_entry.get() and self.password_entry.get():
            self.login()
        elif self.nombre_entry.get() and self.apellido_entry.get():
            self.register_user()

    # Validar formato de correo electrónico
    def validar_email(self, email):
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

    # Limpiar los campos de entrada
    def clear_fields(self):
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
    
    # Función para salir de la aplicación
    def salir(self, event=None):
        self.root.quit()

# Función para iniciar la aplicación de inicio de sesión
def iniciar_login():
    root = tk.Tk()
    app = LoginRegisterApp(root)
    root.mainloop()
