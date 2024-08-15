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
        print("\nMenú Principal:")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Salir")

        eleccion = input("Elige una opción (1/2/3): ")

        if eleccion == '1':
            solicitud = cliente_registro()
            cliente_socket.send(solicitud.encode('utf-8'))
        elif eleccion == '2':
            solicitud = cliente_inicio_sesion()
            cliente_socket.send(solicitud.encode('utf-8'))
        elif eleccion == '3':
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida. Inténtalo de nuevo.")
            continue

        respuesta = cliente_socket.recv(1024).decode('utf-8')
        print(f"Respuesta del servidor: {respuesta}")

        # Si el usuario se registra o inicia sesión correctamente, mostrar el menú adicional
        if "exitoso" in respuesta:
            while True:
                print("\nMenú de Usuario:")
                print("1. Agregar Película")
                print("2. Ver Listado de Películas")
                print("3. Ver Reviews (No implementado)")
                print("4. Cerrar sesión")

                opcion = input("Elige una opción (1/2/3/4): ")
                cliente_socket.send(opcion.encode('utf-8'))

                respuesta_menu = cliente_socket.recv(1024).decode('utf-8')
                print(f"Respuesta del servidor: {respuesta_menu}")

                if opcion == '4':
                    print("Sesión cerrada.")
                    break

    cliente_socket.close()

if __name__ == '__main__':
    iniciar_cliente()
