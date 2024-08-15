import socket
import threading
import hashlib
from models import Session, Usuario, Pelicula

# Funciones de hashing
def hashear_contrasena(contrasena):
    return hashlib.sha256(contrasena.encode()).hexdigest()

# Diccionario para sesiones activas
sesiones_activas = {}

def manejar_cliente(cliente_socket, direccion):
    session = Session()
    usuario_actual = None  # Usuario actualmente autenticado en este cliente

    try:
        while True:
            if usuario_actual is None:
                # Si no hay usuario autenticado, esperar a que se registre o inicie sesión
                datos = cliente_socket.recv(1024).decode('utf-8')
                if not datos:
                    break

                tipo_solicitud, *params = datos.split(',')

                if tipo_solicitud == 'registrar':
                    nombre, apellido, alias, contrasena = params
                    contrasena_hasheada = hashear_contrasena(contrasena)

                    if session.query(Usuario).filter_by(alias=alias).first():
                        cliente_socket.send(b'Alias ya en uso')
                    else:
                        nuevo_usuario = Usuario(nombre=nombre, apellido=apellido, alias=alias, contrasena=contrasena_hasheada)
                        session.add(nuevo_usuario)
                        session.commit()
                        cliente_socket.send(b'Registro exitoso')
                        usuario_actual = nuevo_usuario
                        sesiones_activas[direccion] = nuevo_usuario.alias

                elif tipo_solicitud == 'iniciar_sesion':
                    alias, contrasena = params
                    contrasena_hasheada = hashear_contrasena(contrasena)

                    usuario = session.query(Usuario).filter_by(alias=alias, contrasena=contrasena_hasheada).first()
                    if usuario:
                        cliente_socket.send(b'Inicio de sesion exitoso')
                        usuario_actual = usuario
                        sesiones_activas[direccion] = usuario.alias
                    else:
                        cliente_socket.send(b'Credenciales invalidas')

            else:
                # Usuario autenticado: mostrar opciones de menú
                cliente_socket.send(b'\n1. Agregar Pelicula\n2. Ver Listado de Peliculas\n3. Ver Reviews\n4. Cerrar sesion\nElige una opcion (1/2/3/4):')
                datos = cliente_socket.recv(1024).decode('utf-8')

                if datos == '1':  # Agregar Película
                    cliente_socket.send(b'Ingresa el nombre de la pelicula: ')
                    nombre_pelicula = cliente_socket.recv(1024).decode('utf-8')
                    cliente_socket.send(b'Ingresa el genero de la pelicula: ')
                    genero_pelicula = cliente_socket.recv(1024).decode('utf-8')

                    nueva_pelicula = Pelicula(nombre=nombre_pelicula, genero=genero_pelicula)
                    session.add(nueva_pelicula)
                    session.commit()
                    cliente_socket.send(b'Pelicula agregada exitosamente')

                elif datos == '2':  # Ver Listado de Películas
                    peliculas = session.query(Pelicula).all()
                    if peliculas:
                        peliculas_list = "\n".join([f"{pelicula.id}. {pelicula.nombre} ({pelicula.genero})" for pelicula in peliculas])
                        cliente_socket.send(peliculas_list.encode('utf-8'))
                    else:
                        cliente_socket.send(b'No hay peliculas disponibles.')

                elif datos == '3':  # Ver Reviews (puede extenderse más adelante)
                    cliente_socket.send(b'Feature no implementada')

                elif datos == '4':  # Cerrar sesión
                    cliente_socket.send(b'Cerrando sesion...')
                    usuario_actual = None
                    sesiones_activas.pop(direccion, None)

                else:
                    cliente_socket.send(b'Opcion invalida. Intentalo de nuevo.')

    finally:
        session.close()
        cliente_socket.close()

def iniciar_servidor():
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind(('0.0.0.0', 9999))
    servidor_socket.listen(5)
    print("Servidor escuchando en el puerto 9999")

    while True:
        cliente_socket, addr = servidor_socket.accept()
        print(f"Conexión establecida con {addr}")
        manejador_cliente = threading.Thread(target=manejar_cliente, args=(cliente_socket, addr))
        manejador_cliente.start()

if __name__ == '__main__':
    iniciar_servidor()
