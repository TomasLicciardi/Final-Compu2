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

def menu_pelicula(cliente_socket, id_pelicula):
    while True:
        print("\nSubmenú de Película:")
        print("1. Agregar Review")
        print("2. Ver Reviews")
        print("3. Volver")
        eleccion = input("Elige una opción (1/2/3): ")
        if eleccion == '1':
            texto = input("Escribe tu review: ")
            calificacion = input("Califica la película del 1 al 10: ")
            solicitud = f"agregar_review,{id_pelicula},{texto},{calificacion}"
            cliente_socket.send(solicitud.encode('utf-8'))
            respuesta = cliente_socket.recv(1024).decode('utf-8')
            print(f"Respuesta del servidor: {respuesta}")
        elif eleccion == '2':
            solicitud = f"ver_reviews,{id_pelicula}"
            cliente_socket.send(solicitud.encode('utf-8'))
            respuesta = cliente_socket.recv(1024).decode('utf-8')
            print(f"Reviews:\n{respuesta}")
        elif eleccion == '3':
            break
        else:
            print("Opción inválida. Inténtalo de nuevo.")

def iniciar_cliente():
    # Preguntar al usuario qué tipo de conexión desea usar
    eleccion = input("¿Deseas usar IPv4 (1) o IPv6 (2)? ")

    if eleccion == '1':
        family = socket.AF_INET
    elif eleccion == '2':
        family = socket.AF_INET6
    else:
        print("Opción inválida. Usando IPv4 por defecto.")
        family = socket.AF_INET

    # Obtener información de direcciones para el tipo de conexión seleccionado
    direccion_info = socket.getaddrinfo(None, 9999, family, socket.SOCK_STREAM)

    cliente_socket = None

    for res in direccion_info:
        af, socktype, proto, canonname, sa = res
        try:
            cliente_socket = socket.socket(af, socktype, proto)
            cliente_socket.connect(sa)
            print(f"Conectado a {sa}")
            break
        except OSError as e:
            if cliente_socket:
                cliente_socket.close()
            cliente_socket = None

    if cliente_socket is None:
        print("No se pudo establecer conexión con el servidor.")
        return

    while True:
        print("\nMenú Principal:")
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

        if "exitoso" in respuesta:
            while True:
                print("\nMenú Principal:")
                print("1. Agregar Película")
                print("2. Ver Películas")
                print("3. Cerrar Sesión")

                eleccion = input("Elige una opción (1/2/3): ")

                if eleccion == '1':
                    nombre = input("Ingresa el nombre de la película: ")
                    
                    print("Selecciona el género de la película:")
                    print("1. Drama")
                    print("2. Acción")
                    print("3. Comedia")
                    print("4. Ciencia Ficción")
                    print("5. Terror")
                    
                    opcion_genero = input("Ingresa el número de la opción deseada: ")
                    
                    if opcion_genero == '1':
                        genero = "Drama"
                    elif opcion_genero == '2':
                        genero = "Acción"
                    elif opcion_genero == '3':
                        genero = "Comedia"
                    elif opcion_genero == '4':
                        genero = "Ciencia Ficción"
                    elif opcion_genero == '5':
                        genero = "Terror"
                    else:
                        print("Opción no válida.")
                        genero = None
                    
                    if genero:
                        solicitud = f"agregar_pelicula,{nombre},{genero}"
                        cliente_socket.send(solicitud.encode('utf-8'))
                        respuesta = cliente_socket.recv(1024).decode('utf-8')
                        print(f"Respuesta del servidor: {respuesta}")

                elif eleccion == '2':
                    solicitud = "ver_peliculas"
                    cliente_socket.send(solicitud.encode('utf-8'))
                    respuesta = cliente_socket.recv(1024).decode('utf-8')
                    print(f"Películas disponibles:\n{respuesta}")
                    
                    id_pelicula = input("Selecciona una película por número: ")
                    menu_pelicula(cliente_socket, id_pelicula)
                elif eleccion == '3':
                    solicitud = "cerrar_sesion"
                    cliente_socket.send(solicitud.encode('utf-8'))
                    respuesta = cliente_socket.recv(1024).decode('utf-8')
                    print(f"Respuesta del servidor: {respuesta}")
                    break
                else:
                    print("Opción inválida. Inténtalo de nuevo.")

    cliente_socket.close()

if __name__ == '__main__':
    iniciar_cliente()
