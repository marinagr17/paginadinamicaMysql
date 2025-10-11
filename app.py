from flask import Flask, request, render_template, redirect, url_for, session
from dotenv import load_dotenv
import pymysql, os 
# Cargar variables del archivo .env
load_dotenv('clave.env')

app = Flask(__name__)


app.secret_key=os.getenv('SECRET_KEY')

#login

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        host = request.form['host']
        user = request.form['usuario']
        password = request.form['clave']
        database = request.form['basedatos']

        try:
            #para conectarmos a mysql
            conexion = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            conexion.close()

            # Guardamos los datos en sesión
            session['host'] = host
            session['user'] = user
            session['password'] = password
            session['database'] = database

            return redirect(url_for('mostrar_tablas'))
        except Exception as e:
            return f"Error al conectar con MySQL: {e}"
        
    return render_template('login.html')

#Pagina para las tablas

@app.route('/tablas')
def mostrar_tablas():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conexion = pymysql.connect(
        host=session['host'],
        user=session['user'],
        password=session['password'],
        database=session['database']
    )
    cursor = conexion.cursor()
    cursor.execute("SHOW TABLES;")
    tablas = [t[0] for t in cursor.fetchall()]
    conexion.close()

    return render_template('tablas.html', tablas=tablas)

# --- Página que muestra registros de una tabla ---
@app.route('/tabla/<nombre>')
def mostrar_registros(nombre):
    if 'user' not in session:
        return redirect(url_for('login'))

    conexion = pymysql.connect(
        host=session['host'],
        user=session['user'],
        password=session['password'],
        database=session['database']
    )
    cursor = conexion.cursor()
    cursor.execute(f"SELECT * FROM {nombre} LIMIT 20;")
    registros = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    conexion.close()

    return render_template('registros.html', nombre=nombre, columnas=columnas, registros=registros)

if __name__ == '__main__':
    app.run(debug=True)