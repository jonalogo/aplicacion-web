import streamlit as st
import requests
import folium
from datetime import datetime
import streamlit.components.v1 as components
import pymysql

# Función para conectar a la base de datos con credenciales dinámicas
def conectar_bd(usuario, contrasena):
    try:
        return pymysql.connect(
            host="localhost",       # Cambia por el host de tu base de datos
            user=usuario,           # Usuario ingresado en el login
            password=contrasena,    # Contraseña ingresada en el login
            database="accesos"      # Base de datos
        )
    except pymysql.MySQLError as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

# Función para obtener la IP y ubicación geográfica
def obtener_ip_y_ubicacion():
    ip_info = requests.get('https://ipinfo.io/json').json()
    ip = ip_info['ip']
    location = ip_info['loc'].split(',')
    latitude = float(location[0])
    longitude = float(location[1])
    return ip, latitude, longitude

# Función para insertar datos en la tabla usuarios
def insertar_usuario(conexion, datos):
    try:
        cursor = conexion.cursor()
        consulta = """
            INSERT INTO usuarios (codigo, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, genero, celular, correo, ip, latitud, longitud)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(consulta, datos)
        conexion.commit()
    except Exception as e:
        st.error(f"Error al insertar datos: {e}")
    finally:
        conexion.close()

# Interfaz de login
st.title('Sistema de Login')
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    with st.form(key='login_form'):
        usuario = st.text_input('Usuario')
        contrasena = st.text_input('Contraseña', type='password')
        login_button = st.form_submit_button('Iniciar Sesión')

    if login_button:
        # Intentar conectar con los credenciales ingresados
        conexion = conectar_bd(usuario, contrasena)
        if conexion:
            st.success('Inicio de sesión exitoso')
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.contrasena = contrasena
        else:
            st.error('Usuario o contraseña inválidos')
else:
    # Mostrar formulario de registro si el usuario ya está autenticado
    st.title('Formulario de Registro con IP y Ubicación')
    with st.form(key='registro_form'):
        codigo = st.text_input('Código')
        nombre = st.text_input('Nombre')
        apellido_paterno = st.text_input('Apellido Paterno')
        apellido_materno = st.text_input('Apellido Materno')
        fecha_nacimiento = st.date_input('Fecha de Nacimiento', min_value=datetime(1900, 1, 1), max_value=datetime.today())
        genero = st.selectbox('Género', ['Masculino', 'Femenino', 'Otro'])
        celular = st.text_input('Celular', placeholder="Ejemplo: +52 123 456 7890")
        correo = st.text_input('Correo Electrónico')
        submit_button = st.form_submit_button(label='Registrar')

    # Acción cuando se envía el formulario
    if submit_button:
        ip, latitude, longitude = obtener_ip_y_ubicacion()
        conexion = conectar_bd(st.session_state.usuario, st.session_state.contrasena)
        if conexion:
            datos = (
                codigo, nombre, apellido_paterno, apellido_materno,
                fecha_nacimiento, genero, celular, correo, ip, latitude, longitude
            )
            insertar_usuario(conexion, datos)

            # Mostrar datos del formulario
            st.write("### Datos del Registro")
            st.write(f"**Código:** {codigo}")
            st.write(f"**Nombre:** {nombre} {apellido_paterno} {apellido_materno}")
            st.write(f"**Fecha de Nacimiento:** {fecha_nacimiento}")
            st.write(f"**Género:** {genero}")
            st.write(f"**Celular:** {celular}")
            st.write(f"**Correo Electrónico:** {correo}")
            st.write(f"**IP Pública:** {ip}")

            # Mostrar mapa de ubicación basado en la IP
            st.write("### Mapa de la Ubicación Aproximada de tu IP")
            mapa = folium.Map(location=[latitude, longitude], zoom_start=12)
            folium.Marker([latitude, longitude], popup=f"IP: {ip}").add_to(mapa)
            mapa_html = mapa._repr_html_()
            components.html(mapa_html, height=500)

            st.success('¡Registro completado exitosamente!')
        else:
            st.error('No se pudo conectar a la base de datos. Verifica tus credenciales.')
