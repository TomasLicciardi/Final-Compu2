import socket
import threading
import hashlib
from models import Session, Usuario, Pelicula, Review
import multiprocessing
from logs import log_writer


lock = threading.Lock()

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

            tipo_solicitud, *params = datos.split('|')
            if tipo_solicitud == 'registrar':
                nombre, apellido, alias, contrasena = params
                contrasena_hasheada = hashear_contrasena(contrasena)

                with lock:
                    if session.query(Usuario).filter_by(alias=alias).first():
                        cliente_socket.send(b'Alias ya en uso')
                    else:
                        nuevo_usuario = Usuario(nombre=nombre, apellido=apellido, alias=alias, contrasena=contrasena_hasheada)
                        session.add(nuevo_usuario)
                        session.commit()
                        cliente_socket.send(b'Registro exitoso')
                        id_usuario = nuevo_usuario.id
                        if id_usuario is not None:
                            log_queue.put(f"Nuevo usuario registrado: {alias}")
                        else:
                            cliente_socket.send(b'Error al registrar')

            elif tipo_solicitud == 'iniciar_sesion':
                alias, contrasena = params
                contrasena_hasheada = hashear_contrasena(contrasena)

                with lock:
                    usuario = session.query(Usuario).filter_by(alias=alias, contrasena=contrasena_hasheada).first()
                    if usuario:
                        id_usuario = usuario.id
                        if id_usuario is not None:
                            cliente_socket.send(b'Inicio de sesion exitoso')
                            log_queue.put(f"Usuario inicio sesion: {alias}")
                        else:
                            cliente_socket.send(b'Error al iniciar sesion')
                    else:
                        cliente_socket.send(b'Credenciales invalidas')

            elif tipo_solicitud == 'agregar_pelicula':
                nombre, genero = params
                with lock:
                    nueva_pelicula = Pelicula(nombre=nombre, genero=genero)
                    session.add(nueva_pelicula)
                    session.commit()
                cliente_socket.send(b'Pelicula agregada exitosamente')
                log_queue.put(f"Se ha agregado la película '{nombre}' por el usuario {alias}")

            elif tipo_solicitud == 'ver_peliculas':
                genero = params[0]
                with lock:
                    peliculas = session.query(Pelicula).filter_by(genero=genero).all()
                if not peliculas:
                    cliente_socket.send(f"No hay películas disponibles en el género {genero}.".encode('utf-8'))
                else:
                    response = '\n'.join([f"{pelicula.id}. {pelicula.nombre} ({pelicula.genero})" for pelicula in peliculas])
                    cliente_socket.send(response.encode('utf-8'))

            elif tipo_solicitud == 'agregar_review':
                id_pelicula, texto, calificacion = params
                with lock:
                    nueva_review = Review(texto=texto, calificacion=int(calificacion), id_usuario=id_usuario, id_pelicula=int(id_pelicula))
                    session.add(nueva_review)
                    session.commit()
                cliente_socket.send(b'Review agregada exitosamente')
                pelicula = session.query(Pelicula).filter_by(id=id_pelicula).first()
                log_queue.put(f"Se ha agregado una nueva review a la película '{pelicula.nombre}' por el usuario {alias}")

            elif tipo_solicitud == 'ver_reviews':
                id_pelicula = params[0]
                with lock:
                    reviews = session.query(Review).filter_by(id_pelicula=id_pelicula).all()
                if not reviews:
                    cliente_socket.send(b'No hay reviews de esta pelicula.')
                else:
                    response = '\n'.join([f"{review.id}. {review.texto} - Calificación: {review.calificacion}/10 - Por: {review.usuario.alias}" for review in reviews])
                    cliente_socket.send(response.encode('utf-8'))

            elif tipo_solicitud == 'cerrar_sesion':
                cliente_socket.send(b'Sesion cerrada')
                log_queue.put(f"Usuario cerro sesion: {alias}")
                break

    finally:
        session.close()
        cliente_socket.close()


def obtener_direccion_info(host, port, familia):
    for res in socket.getaddrinfo(host, port, familia, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        return af, socktype, proto, sa
    return None

def servidor_ipv4(log_queue, stop_event):
    af, socktype, proto, sa = obtener_direccion_info('0.0.0.0', 9999, socket.AF_INET)
    server_socket_ipv4 = socket.socket(af, socktype, proto)
    server_socket_ipv4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket_ipv4.bind(sa)  # IPv4
    server_socket_ipv4.listen(5)
    print("Servidor IPv4 escuchando en el puerto 9999")

    while not stop_event.is_set():
        try:
            server_socket_ipv4.settimeout(1.0)
            cliente_socket, cliente_direccion = server_socket_ipv4.accept()
            print(f"Conexión establecida desde {cliente_direccion} (IPv4)")
            client_thread = threading.Thread(target=manejar_cliente, args=(cliente_socket, log_queue))
            client_thread.start()
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            break

    server_socket_ipv4.close()

def servidor_ipv6(log_queue, stop_event):
    af, socktype, proto, sa = obtener_direccion_info('::', 9999, socket.AF_INET6)
    server_socket_ipv6 = socket.socket(af, socktype, proto)
    server_socket_ipv6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket_ipv6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1) 
    server_socket_ipv6.bind(sa)  
    server_socket_ipv6.listen(5)
    print("Servidor IPv6 escuchando en el puerto 9999")

    while not stop_event.is_set():
        try:
            server_socket_ipv6.settimeout(1.0)
            cliente_socket, cliente_direccion = server_socket_ipv6.accept()
            print(f"Conexión establecida desde {cliente_direccion} (IPv6)")
            client_thread = threading.Thread(target=manejar_cliente, args=(cliente_socket, log_queue))
            client_thread.start()
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            break

    server_socket_ipv6.close()

def iniciar_servidor():
    log_queue = multiprocessing.Queue()
    log_process = multiprocessing.Process(target=log_writer, args=(log_queue,))
    log_process.start()

    stop_event = threading.Event()

    soporte_ipv4 = False
    soporte_ipv6 = False

    for res in socket.getaddrinfo(None, 9999, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        if af == socket.AF_INET:
            soporte_ipv4 = True
        elif af == socket.AF_INET6:
            soporte_ipv6 = True

    try:
        if soporte_ipv4:
            hilo_ipv4 = threading.Thread(target=servidor_ipv4, args=(log_queue, stop_event))
            hilo_ipv4.start()

        if soporte_ipv6:
            hilo_ipv6 = threading.Thread(target=servidor_ipv6, args=(log_queue, stop_event))
            hilo_ipv6.start()

        if soporte_ipv4:
            hilo_ipv4.join()

        if soporte_ipv6:
            hilo_ipv6.join()
            
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
        stop_event.set()
    finally:
        log_process.terminate()
        log_process.join()

if __name__ == "__main__":
    iniciar_servidor()
