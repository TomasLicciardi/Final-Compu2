import socket
import threading
import hashlib
from models import Session, Usuario, Pelicula

# Hashear contraseña
def hashear_contrasena(contrasena):
    return hashlib.sha256(contrasena.encode()).hexdigest()

# Manejar las solicitudes del cliente
def manejar_cliente(cliente_socket):
    session = Session()

    usuario_activo = None

    try:
        while True:
            # Recibir datos del cliente
            datos = cliente_socket.recv(1024).decode('utf-8')
            if not datos:
                break

            # Procesar la solicitud del cliente (registro, inicio de sesión, o acciones del menú)
            tipo_solicitud, *params = datos.split(',')

            if tipo_solicitud == 'registrar':
                nombre, apellido, alias, contrasena = params
                contrasena_hasheada = hashear_contrasena(contrasena)

                # Verificar si el alias ya está en uso
                if session.query(Usuario).filter_by(alias=alias).first():
                    cliente_socket.send(b'Alias ya en uso')
                else:
                    # Crear nuevo usuario
                    nuevo_usuario = Usuario(nombre=nombre, apellido=apellido, alias=alias, contrasena=contrasena_hasheada)
                    session.add(nuevo_usuario)
                    session.commit()
                    cliente_socket.send(b'Registro exitoso')

            elif tipo_solicitud == 'iniciar_sesion':
                alias, contrasena = params
                contrasena_hasheada = hashear_contrasena(contrasena)

                # Verificar las credenciales del usuario
                usuario = session.query(Usuario).filter_by(alias=alias, contrasena=contrasena_hasheada).first()
                if usuario:
                    usuario_activo = usuario
                    cliente_socket.send(b'Inicio de sesion exitoso')
                else:
                    cliente_socket.send(b'Credenciales invalidas')

            elif tipo_solicitud == '1' and usuario_activo:  # Agregar Película
                nombre_pelicula = params[0]
                genero_pelicula = params[1]

                # Verificar si la película ya existe
                if session.query(Pelicula).filter_by(nombre=nombre_pelicula).first():
                    cliente_socket.send(b'La pelicula ya existe')
                else:
                    # Crear nueva película
                    nueva_pelicula = Pelicula(nombre=nombre_pelicula, genero=genero_pelicula)
                    session.add(nueva_pelicula)
                    session.commit()
                    cliente_socket.send(b'Pelicula agregada exitosamente')

            elif tipo_solicitud == '2' and usuario_activo:  # Ver Listado de Películas
                peliculas = session.query(Pelicula).all()
                if peliculas:
                    respuesta = "\n".join([f"{pelicula.id}. {pelicula.nombre} - {pelicula.genero}" for pelicula in peliculas])
                else:
                    respuesta = "No hay peliculas disponibles"
                cliente_socket.send(respuesta.encode('utf-8'))

            elif tipo_solicitud == '4' and usuario_activo:  # Cerrar sesión
                cliente_socket.send(b'Sesion cerrada')
                usuario_activo = None
    finally:
        session.close()
        cliente_socket.close()

# Iniciar servidor
def iniciar_servidor():
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind(('0.0.0.0', 9999))
    servidor_socket.listen(5)
    print("Servidor escuchando en el puerto 9999")

    while True:
        cliente_socket, addr = servidor_socket.accept()
        print(f"Conexión establecida con {addr}")
        manejador_cliente = threading.Thread(target=manejar_cliente, args=(cliente_socket,))
        manejador_cliente.start()

if __name__ == '__main__':
    iniciar_servidor()
