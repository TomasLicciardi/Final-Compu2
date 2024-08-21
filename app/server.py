import socket
import threading
import hashlib
from models import Session, Usuario, Pelicula, Review
import multiprocessing
from logs import log_writer
import select

def hashear_contrasena(contrasena):
    return hashlib.sha256(contrasena.encode()).hexdigest()

def manejar_cliente(cliente_socket, log_queue):
    session = Session()

    try:
        id_usuario = None
        alias = None

        while True:
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
                    log_queue.put(f"Nuevo usuario registrado: {alias}")

            elif tipo_solicitud == 'iniciar_sesion':
                alias, contrasena = params
                contrasena_hasheada = hashear_contrasena(contrasena)

                usuario = session.query(Usuario).filter_by(alias=alias, contrasena=contrasena_hasheada).first()
                if usuario:
                    id_usuario = usuario.id
                    cliente_socket.send(b'Inicio de sesion exitoso')
                    log_queue.put(f"Usuario inicio sesion: {alias}")
                else:
                    cliente_socket.send(b'Credenciales invalidas')

            elif tipo_solicitud == 'agregar_pelicula':
                nombre, genero = params
                nueva_pelicula = Pelicula(nombre=nombre, genero=genero)
                session.add(nueva_pelicula)
                session.commit()
                cliente_socket.send(b'Pelicula agregada exitosamente')
                log_queue.put(f"Se ha agregado la película '{nombre}' por el usuario {alias}")

            elif tipo_solicitud == 'ver_peliculas':
                peliculas = session.query(Pelicula).all()
                response = '\n'.join([f"{pelicula.id}. {pelicula.nombre} ({pelicula.genero})" for pelicula in peliculas])
                cliente_socket.send(response.encode('utf-8'))

            elif tipo_solicitud == 'agregar_review':
                id_pelicula, texto, calificacion = params
                nueva_review = Review(texto=texto, calificacion=int(calificacion), id_usuario=id_usuario, id_pelicula=int(id_pelicula))
                session.add(nueva_review)
                session.commit()
                cliente_socket.send(b'Review agregada exitosamente')
                pelicula = session.query(Pelicula).filter_by(id=id_pelicula).first()
                log_queue.put(f"Se ha agregado una nueva review a la película '{pelicula.nombre}' por el usuario {alias}")

            elif tipo_solicitud == 'ver_reviews':
                id_pelicula = params[0]
                reviews = session.query(Review).filter_by(id_pelicula=id_pelicula).all()
                
                response = '\n'.join([f"{review.id}. {review.texto} - Calificación: {review.calificacion}/10 - Por: {review.usuario.alias}" for review in reviews])
                cliente_socket.send(response.encode('utf-8'))

            elif tipo_solicitud == 'cerrar_sesion':
                cliente_socket.send(b'Sesion cerrada')
                log_queue.put(f"Usuario cerro sesion: {alias}")
                break

    finally:
        session.close()
        cliente_socket.close()

def iniciar_servidor():
    # Inicializar la cola y el proceso para manejar los logs
    log_queue = multiprocessing.Queue()
    log_process = multiprocessing.Process(target=log_writer, args=(log_queue,))
    log_process.start()

    # Obtener información de direcciones para todas las interfaces (IPv4 e IPv6)
    addrinfos = socket.getaddrinfo(None, 9999, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)

    # Lista para almacenar los sockets del servidor
    server_sockets = []

    # Crear y configurar los sockets basados en la información de direcciones obtenida
    for addrinfo in addrinfos:
        family, socktype, proto, canonname, sockaddr = addrinfo
        try:
            server_socket = socket.socket(family, socktype, proto)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            if family == socket.AF_INET6:
                # Configurar el socket IPv6 para que solo acepte conexiones IPv6
                server_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)

            # Vincular el socket a la dirección y puerto especificados
            server_socket.bind(sockaddr)
            server_socket.listen(5)
            server_sockets.append(server_socket)

            # Determinar el tipo de dirección y mostrar un mensaje
            if family == socket.AF_INET6:
                address_type = "IPv6"
            else: 
                address_type = "IPv4"
            print(f"Servidor escuchando en {sockaddr[0]}:{sockaddr[1]} ({address_type})")

        except Exception as e:
            print(f"Error al crear el socket para {sockaddr}: {e}")

    # Verificar si al menos un socket se creó correctamente
    if not server_sockets:
        raise RuntimeError("No se pudieron crear sockets para ninguna de las direcciones")

    try:
        while True:
            # Esperar conexiones en cualquiera de los sockets disponibles
            readable, _, _ = select.select(server_sockets, [], [])
            for s in readable:
                cliente_socket, cliente_direccion = s.accept()
                print(f"Conexión establecida desde {cliente_direccion}")

                # Crear un nuevo hilo para manejar la conexión del cliente
                client_thread = threading.Thread(target=manejar_cliente, args=(cliente_socket, log_queue))
                client_thread.start()

    except KeyboardInterrupt:
        print("Cerrando servidor...")

    finally:
        # Cerrar todos los sockets y el proceso de logs
        for server_socket in server_sockets:
            server_socket.close()

        log_process.terminate()
        log_process.join()

if __name__ == "__main__":
    iniciar_servidor()
