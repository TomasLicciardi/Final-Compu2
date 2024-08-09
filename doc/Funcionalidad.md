# Funcionalidades:

### Client:

- Conexión con el Servidor: Establece una conexión de socket con el servidor para enviar y recibir datos en tiempo real.
- Registro e Inicio de Sesión: Permite a los usuarios registrarse y loguearse para acceder a la aplicación.
- Interfaz de Usuario: Proporciona una interfaz para que los usuarios interactúen con el sistema, como agregar películas, escribir reseñas y ver reviews de otros usuarios.
- Envío de Solicitudes: Permite a los usuarios enviar solicitudes al servidor para realizar diversas acciones, como agregar una película, escribir una reseña y ver la lista de películas.

### Server:

- Gestión de Conexiones: Acepta conexiones con sockets y usa hilos para manejar múltiples clientes simultáneamente.
- Autenticación y Autorización: Valida las credenciales de los usuarios para permitir el acceso seguro a la aplicación.
- Manejo de Películas: Controla la lógica para agregar nuevas películas a la base de datos y gestionar la información de las películas existentes.
- Manejo de Reviews: Controla la lógica para agregar y visualizar reseñas de películas, asegurando que las reviews estén vinculadas correctamente a los usuarios y películas correspondientes.
- Consultas SQL: Realiza consultas SQL para recuperar y actualizar datos en la base de datos, como información de usuarios, películas y reviews.
- Manejo de Errores: Captura excepciones como datos inválidos, errores de conexión y problemas de autenticación, informando a los usuarios a través de mensajes.

### Models (ORM):

- Mapeo de Clases a Tablas: Mapea las clases de Python a las tablas de la base de datos.
- Gestión de Relaciones: Define y gestiona las relaciones entre las entidades de la base de datos (usuarios, películas y reviews).
- Consultas y Actualizaciones: Permite realizar consultas y actualizaciones en la base de datos de manera sencilla y eficiente.

### DataBase:

- Almacenamiento de Datos: Almacena datos de usuarios, películas y reviews de manera estructurada.
- Persistencia: Garantiza que los datos permanezcan almacenados de forma persistente, permitiendo su recuperación en futuros inicios de sesión.
- Consultas y Actualizaciones: Permite la ejecución de consultas y actualizaciones a través del ORM para mantener la información actualizada.