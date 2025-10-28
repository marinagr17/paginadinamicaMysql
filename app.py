# Importamos las librerías necesarias de Flask y otros módulos
from flask import Flask, request, render_template, redirect, url_for, session
from dotenv import load_dotenv   # Para leer variables de entorno desde un archivo .env
import pymysql, os               # pymysql para conectar con MySQL, os para acceder a variables del sistema

# --- Cargar variables de entorno ---
# Carga las variables definidas en el archivo ".clave.env"
# Esto permite guardar información sensible (como claves) fuera del código fuente
load_dotenv('.clave.env')

# --- Crear la aplicación Flask ---
app = Flask(__name__)

# Asignar la clave secreta desde el archivo de entorno
# Esta clave se usa para firmar las sesiones (cookies seguras)
app.secret_key = os.getenv('SECRET_KEY')

# ============================================================
#                   RUTA PRINCIPAL: LOGIN
# ============================================================

@app.route('/', methods=['GET', 'POST'])  # Esta ruta acepta tanto peticiones GET como POST
def login():
    # Si el método es POST significa que el usuario ha enviado el formulario
    if request.method == 'POST':
        # Recuperamos los valores enviados desde el formulario de login
        host = request.form['host']
        user = request.form['usuario']
        password = request.form['clave']
        database = request.form['basedatos']

        try:
            # Intentamos conectar a la base de datos MySQL con los datos proporcionados
            conexion = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )

            # Si la conexión fue exitosa, la cerramos
            conexion.close()

            # Guardamos los datos de conexión en la sesión
            # Esto permite acceder a ellos desde otras páginas sin volver a pedirlos
            session['host'] = host
            session['user'] = user
            session['password'] = password
            session['database'] = database

            # Redirigimos a la ruta que muestra las tablas disponibles en la base de datos
            return redirect(url_for('mostrar_tablas'))

        except Exception as e:
            # Si ocurre un error al conectar, mostramos el mensaje de error
            # (por ejemplo: usuario incorrecto, contraseña errónea o base de datos inexistente)
            return f"Error al conectar con MySQL: {e}"

    # Si el método es GET (el usuario accede por primera vez o hubo error),
    # se renderiza la plantilla del formulario de login
    return render_template('login.html')

# ============================================================
#                   RUTA: MOSTRAR TABLAS
# ============================================================

@app.route('/tablas')
def mostrar_tablas():
    # Si el usuario no tiene sesión iniciada, se redirige al login
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Nos conectamos a MySQL usando los datos guardados en sesión
    conexion = pymysql.connect(
        host=session['host'],
        user=session['user'],
        password=session['password'],
        database=session['database']
    )

    # Creamos un cursor para ejecutar sentencias SQL
    cursor = conexion.cursor()

    # Ejecutamos la consulta para mostrar todas las tablas del esquema actual
    cursor.execute("SHOW TABLES;")

    # fetchall() devuelve una lista de tuplas. Extraemos solo el nombre de la tabla (posición [0])
    tablas = [t[0] for t in cursor.fetchall()]

    # Cerramos la conexión
    conexion.close()

    # Renderizamos la plantilla 'tablas.html' y le pasamos la lista de tablas
    return render_template('tablas.html', tablas=tablas)

# ============================================================
#           RUTA: MOSTRAR REGISTROS DE UNA TABLA
# ============================================================

@app.route('/tabla/<nombre>')  # El nombre de la tabla llega como parámetro dinámico en la URL
def mostrar_registros(nombre):
    # Si el usuario no está autenticado, se redirige al login
    if 'user' not in session:
        return redirect(url_for('login'))

    # Conexión a MySQL usando los datos almacenados en sesión
    conexion = pymysql.connect(
        host=session['host'],
        user=session['user'],
        password=session['password'],
        database=session['database']
    )

    # Creamos un cursor para ejecutar la consulta
    cursor = conexion.cursor()

    # Ejecutamos una consulta SQL para obtener todos los registros de la tabla seleccionada
    cursor.execute(f"SELECT * FROM {nombre} ;")

    # fetchall() obtiene todas las filas del resultado de la consulta
    registros = cursor.fetchall()

    # Obtenemos los nombres de las columnas de la tabla (para mostrarlos como cabecera en la tabla HTML)
    columnas = [desc[0] for desc in cursor.description]

    # Cerramos la conexión con MySQL
    conexion.close()

    # Renderizamos la plantilla 'registros.html' pasando:
    # - el nombre de la tabla
    # - las columnas
    # - los registros obtenidos
    return render_template('registros.html', nombre=nombre, columnas=columnas, registros=registros)

# ============================================================
#                   EJECUCIÓN DE LA APLICACIÓN
# ============================================================

# Si ejecutamos este archivo directamente (no importado), arranca el servidor Flask
if __name__ == '__main__':
    # debug=True permite ver errores detallados y recargar la app automáticamente al guardar cambios
    app.run(debug=True)
