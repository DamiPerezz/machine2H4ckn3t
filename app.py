from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3 
import hashlib
import os
import signal
app = Flask(__name__)

clave = "clavesecretisima"
################################################################
def CrearDB():
    conn = sqlite3.connect("usuarios.db")
    conn.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT NOT NULL,password TEXT NOT NULL);''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mensaje TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS flag (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flag TEXT NOT NULL
        );
    ''')
    conn.close()
def Conectar():
    return sqlite3.connect("usuarios.db")
def Insertar_FLAG(flag):
    conn = Conectar()
    cursor = conn.cursor()
    query = "INSERT INTO flag (flag) VALUES ('" + flag+ "')"
    cursor.execute(query)
    conn.commit() 
    cursor.close()
    conn.close()
def InsertarMensaje(mensaje, user_id):
    conn = Conectar()
    cursor = conn.cursor()
    query = "INSERT INTO mensajes (user_id,mensaje) VALUES ('"+str(user_id)+"','"+mensaje+"')"
    cursor.execute(query)
    conn.commit()
    mensaje_id = cursor.lastrowid    
    cursor.close()
    conn.close()
    return mensaje_id
def ConfirmarMensaje(id_msj):
    conn = Conectar()
    cursor = conn.cursor()
    query = "SELECT mensaje FROM mensajes WHERE id ='" +str(id_msj) +"';"
    cursor.execute(query)
    respuesta = cursor.fetchall()[0][0]
    cursor.close()
    conn.close()
    return respuesta
def ObtenerMensajesDeUsuario(user_id):
    conn = Conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT mensaje FROM mensajes WHERE user_id = ?", (user_id,))
    mensajes = cursor.fetchall()
    cursor.close()
    conn.close()

    # Inicializamos la variable respuesta como lista
    respuesta = []

    # Iteramos sobre las tuplas y extraemos el mensaje
    for mensaje in mensajes:
        respuesta.append(mensaje[0])  # mensaje[0] es el contenido del mensaje
    
    # Devolvemos los mensajes como una lista
    return respuesta
def InsertarUsuario(usuario,contraseña):
    conn = Conectar()
    cursor = conn.cursor()
    contraseña_hasheada = hashlib.sha256(contraseña.encode('utf-8')).hexdigest()
    query = "INSERT INTO users (username,password) VALUES ('" + usuario + "', '" + contraseña_hasheada + "')"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
def DevolverMensajes(user_id):
    conn = Conectar()
    cursor = conn.cursor()
    
    # Selecciona solo los mensajes del usuario con user_id
    cursor.execute("SELECT mensaje FROM mensajes WHERE user_id = ?", (user_id,))
    resultado = cursor.fetchall()
    
    # Extraer los mensajes de las tuplas y unirlos con un salto de línea
    lista = [mensaje[0] for mensaje in resultado]  # Extrae el contenido del mensaje desde cada tupla
    
    cursor.close()
    conn.close()
    
    # Unir los mensajes en una sola cadena separados por saltos de línea
    cadena = "\n".join(lista)
    return cadena
def CrearUsuariosUniciales():
    InsertarUsuario("dpm","Hacknet")
    InsertarUsuario("root","pedro.")
def IniciarSesion(usuario,contraseña):
    conn = Conectar()
    cursor = conn.cursor()
    contraseña_hasheada = hashlib.sha256(contraseña.encode('utf-8')).hexdigest()
    cursor.execute("SELECT id, username FROM users WHERE username='"+ usuario+ "' and password='" + contraseña_hasheada+ "'")
    inicio = cursor.fetchall()
    if inicio:    
        print(inicio[0][0])
        return inicio[0][0]
    else:
        return 0
#################################################################
def CifrarID(id):
    global clave
    i = 0
    while i < len(clave):
        id = id * ord(clave[i])  # Multiplicar por el valor ASCII del carácter
        i = i + 1
    return str(id)  # Devolver el resultado como cadena para transportarlo
def DescifrarID(encrypted_id):
    global clave
    id = int(encrypted_id)  # Convertir el ID cifrado de vuelta a un entero
    i = len(clave) - 1
    while i >= 0:
        id = id // ord(clave[i])  # Dividir de forma entera por el valor ASCII
        i = i - 1
    return id  # Devolver el ID original
@app.route('/')
def index():
    return '''
        <h1>Iniciar Sesión</h1>
        <form action="/login" method="POST">
            <label for="username">Usuario:</label><br>
            <input type="text" id="username" name="username"><br><br>
            <label for="password">Contraseña:</label><br>
            <input type="password" id="password" name="password"><br><br>
            <input type="submit" value="Iniciar Sesión">
        </form>
    '''
@app.route('/login', methods=['POST'])
def login():
    global clave
    username = request.form['username']
    password = request.form['password']
    
    if username and password:
        user_id = IniciarSesion(username, password)
        if user_id > 0:
            # Guardar la sesión del usuario
            encripted_id = CifrarID(user_id)
            # Redirigir a la página de mensajes con el ID del usuario
            return redirect(url_for('mensajes', username=username,encrypted_id=encripted_id))
        else:
            return "Error: Usuario o contraseña incorrectos.<br><a href='/'>Intentar de nuevo</a>"
    else:
        return "Error: Usuario o contraseña no pueden estar vacíos.<br><a href='/'>Intentar de nuevo</a>"
@app.route('/mensajes/<encrypted_id>', methods=['GET', 'POST'])
def mensajes(encrypted_id):
    global clave
    # Extraer el username de los parámetros de consulta
    username = request.args.get('username')
    
    # Verificar que el usuario está logueado
    id = DescifrarID(encrypted_id)
    print("Login pasado")
    print(id)
    confDB = ""
    
    if request.method == 'POST':
        # Verificar qué formulario se está enviando basado en el nombre del botón
        if 'añadir_mensaje' in request.form:
            # Si el método es POST para añadir un nuevo mensaje
            nuevo_mensaje = request.form['mensaje']
            if nuevo_mensaje:
                print("Añadiendo mensaje")
                id_msj = InsertarMensaje(nuevo_mensaje, int(id))
                confDB = f"Mensaje {ConfirmarMensaje(id_msj)} añadido con éxito"
            else:
                confDB = "Error: El mensaje no puede estar vacío."

        elif 'buscar_mensaje' in request.form:
            # Si el método es POST para buscar un mensaje
            try:
                busqueda = request.form.get("busqueda")
                if busqueda:
                    print("Buscando mensaje")
                    conn = Conectar()
                    cursor = conn.cursor()
                    query = "SELECT mensaje FROM mensajes WHERE user_id ='" + str(id) + "' AND mensaje LIKE '%"+ busqueda + "%'"
                    cursor.execute(query)
                    mensajes = cursor.fetchall()
                    cursor.close()
                    conn.close()
                    print(mensajes)                    
                    mensajes_html = '<br>'.join([mensaje[0] for mensaje in mensajes])
                    return f'''
                        <h1>Búsqueda de mensajes</h1>
                        <h2>Resultados para: "{busqueda}"</h2>
                        <pre>{mensajes_html}</pre>
                        <br><a href="/mensajes/{encrypted_id}?username={username}">Volver</a>
                        <br><a href="/">Cerrar sesión</a>
                    '''
                else:
                    confDB = "Error: El campo de búsqueda no puede estar vacío."
            except Exception as e:
                print(f"Error en la búsqueda: {e}")
                return "Ocurrió un error al buscar el mensaje.<br><a href='/mensajes'>Regresar</a>"

    # Mostrar los mensajes del usuario si no hay búsqueda
    mensajes = ObtenerMensajesDeUsuario(int(id))
    print(mensajes)
    
    # Convertir los saltos de línea a <br> para HTML
    mensajes_html = '<br>'.join(mensajes)
    
    return f'''
        <h1>Bienvenido {username}</h1>
        <p>{confDB}</p>
        <h2>Tus mensajes:</h2>
        <pre>{mensajes_html}</pre>
        
        <h2>Agregar un nuevo mensaje:</h2>
        <form action="/mensajes/{encrypted_id}?username={username}" method="POST">
            <label for="mensaje">Mensaje:</label><br>
            <input type="text" id="mensaje" name="mensaje"><br><br>
            <input type="submit" name="añadir_mensaje" value="Añadir Mensaje">
        </form>
        
        <h2>Buscar mensaje:</h2>
        <form action="/mensajes/{encrypted_id}?username={username}" method="POST">
            <label for="busqueda">Buscar:</label><br>
            <input type="text" id="busqueda" name="busqueda"><br><br>
            <input type="submit" name="buscar_mensaje" value="Buscar">
        </form>
        
        <br><a href="/">Cerrar sesión</a>
    '''
def eliminar_base_datos():
    if os.path.exists("usuarios.db"):
        os.remove("usuarios.db")
        print("Base de datos 'usuarios.db' eliminada.")
    else:
        print("La base de datos no existe.")
def signal_handler(sig, frame):
    print("\nInterceptada señal Ctrl+C, eliminando base de datos...")
    eliminar_base_datos()
    os._exit(0)
signal.signal(signal.SIGINT, signal_handler)
if __name__ == '__main__':
    CrearDB()
    CrearUsuariosUniciales()
    InsertarMensaje("Bien hecho, primera flag\nFLAG{1Ny3c10n3s_A_La5_DBs}\nObtener la siguiente no sera tan facil",1)
    InsertarMensaje("¿Has enumerado bien la DB?",2)
    Insertar_FLAG("Decodifica y la flag sera tuya --> OzE8OgYwTStODxNNSCJOEwkPTiI5Pw4A")
    app.run(host='0.0.0.0', port=80)
    
