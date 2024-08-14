import socket
import getpass

def cliente_registro():
    alias = input("Elige un alias: ")
    nombre = input("Ingresa tu nombre: ")
    apellido = input("Ingresa tu apellido: ")
    contrasena = getpass.getpass("Ingresa tu contraseña: ")

    solicitud = f"registrar,{nombre},{apellido},{alias},{contrasena}"
    return solicitud

def cliente_inicio_sesion():
    alias = input("Ingresa tu alias: ")
    contrasena = getpass.getpass("Ingresa tu contraseña: ")

    solicitud = f"iniciar_sesion,{alias},{contrasena}"
    return solicitud

def iniciar_cliente():
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.connect(('127.0.0.1', 9999))

    while True:
        print("\nMenú:")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Salir")

        eleccion = input("Elige una opción (1/2/3): ")

        if eleccion == '1':
            solicitud = cliente_registro()
        elif eleccion == '2':
            solicitud = cliente_inicio_sesion()
        elif eleccion == '3':
            break
        else:
            print("Opción inválida. Inténtalo de nuevo.")
            continue

        cliente_socket.send(solicitud.encode('utf-8'))
        respuesta = cliente_socket.recv(1024).decode('utf-8')
        print(f"Respuesta del servidor: {respuesta}")

    cliente_socket.close()

if __name__ == '__main__':
    iniciar_cliente()
