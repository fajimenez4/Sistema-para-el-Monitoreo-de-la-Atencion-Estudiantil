from database import crear_db,conexion_db

# Crear base de datos y establecer conexió
crear_db()
connection = conexion_db()
cursor = connection.cursor()

# Creacion tabla Usuarios
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
            connection.commit()
    except Exception as e:
        print(f"❌ Error creando la tabla 'Usuarios': {e}")

tabla_usuarios(connection)

# Iniciar sesión 
from login import iniciar_login
iniciar_login()