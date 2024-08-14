import socket
import threading
import hashlib
from models import Session, Usuario

def hashear_contrasena(contrasena):
    return hashlib.sha256(contrasena.encode()).hexdigest()

def manejar_cliente(cliente_socket):
    session = Session()

    try:
        while True:
            # Recibir datos del cliente
            datos = cliente_socket.recv(1024).decode('utf-8')
            if not datos:
                break

            # Procesar la solicitud del cliente (registro o inicio de sesión)
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
                    cliente_socket.send(b'Inicio de sesion exitoso')
                else:
                    cliente_socket.send(b'Credenciales invalidas')
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
        manejador_cliente = threading.Thread(target=manejar_cliente, args=(cliente_socket,))
        manejador_cliente.start()

if __name__ == '__main__':
    iniciar_servidor()
