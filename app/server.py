import socket
import threading
import hashlib
from models import Session, Usuario, Pelicula, Review
import multiprocessing
from logs import log_writer

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
    log_queue = multiprocessing.Queue()
    log_process = multiprocessing.Process(target=log_writer, args=(log_queue,))
    log_process.start()

    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind(('0.0.0.0', 9999))
    servidor_socket.listen(5)
    print("Servidor escuchando en el puerto 9999")

    while True:
        cliente_socket, addr = servidor_socket.accept()
        print(f"Conexión establecida con {addr}")
        manejador_cliente = threading.Thread(target=manejar_cliente, args=(cliente_socket, log_queue))
        manejador_cliente.start()
    
    log_queue.put("TERMINATE")
    log_process.join()

if __name__ == '__main__':
    iniciar_servidor()
