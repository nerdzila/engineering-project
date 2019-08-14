# engineering-project
Engineering Project

## Instalación local

Requerimientos:

* Python 3
* `make`
* [pipenv](https://docs.pipenv.org/en/latest/install/#installing-pipenv)

Creación de entorno local (instala dependencias y crea base de datos de ejemplo):

```make devenvironment```

Ejecutar pruebas:

```make test```

Iniciar servidor:

```make server```

Ésto levanta la aplicación web en http://127.0.0.1:5000/, y el API en http://127.0.0.1:5000/api/ las credenciales de los usuarios de ejemplo están en la siguiente sección.

## Credenciales

Por defecto se inicializa una base de datos con dos usuarios, uno es `user1:password1` y tiene algunos autos registrados.

El otro es `user2:password2` y no tiene ningún auto registrado.

## Organización del proyecto

`model.py` contiene el código de manejo de autos y usuarios, `test_model.py` contiene las pruebas para dicho código.

`app.py` contiene la aplicación de `flask`, ahí se encuentran tanto la aplicación web como el API.

En `/data` se guardan las bases de datos SQLite del proyecto.


## API
El API presenta los siguientes endpoints:

| Endpoint            | Método | Acción                                |
|---------------------|--------|---------------------------------------|
| `/api/cars`         | GET    | Lista de autos para el usuario actual |
| `/api/cars`         | POST   | Crea un nuevo auto                    |
| `/api/cars/[placa]` | PUT    | Actualiza la ubicación de un auto     |
| `/api/cars/[placa]` | DELETE | Borra un auto                         |

El API utiliza autenticación simple, el caso básico de uso sería:

```curl -u [user]:[password] http://127.0.0.1:5000/[endpoint]```

Las respuestas siempre son JSON y tienen el siguiente formato:

```
{
    success: [bool]
    result: [datos solicitados o mensaje de error]
}
```

### Ejemplos de uso

Listar autos:

```curl -u user1:password1 http://127.0.0.1:5000/api/cars```

Crear nuevo auto:

```curl -u user1:password1 -i -H "Content-Type: application/json" -X POST -d '{"license_plate":"7357THIS", "latitude": 19.286864, "longitude": -99.655724}' http://127.0.0.1:5000/api/cars```

Actualizar ubicación:

```curl -u user1:password1 -i -H "Content-Type: application/json" -X PUT -d '{"latitude": 19.286492, "longitude": -98.997679}' http://127.0.0.1:5000/api/cars/LOL1337```

Borrar auto:
```curl -u user1:password1 -X DELETE http://127.0.0.1:5000/api/cars/LOL1337```


## Especificación
### Aplicación de Rastreo

El objetivo es construir una applicación web donde se administre una flotilla de vehiculos y se pueda ver su posición.
Cada vehiculo tiene los siguientes datos:

1. Id de Vehiculo
2. Placas
3. Ultima posición conocida (lat,lon)

### Requerimientos

1. Construir un API HTTP Rest con  en la que se pueda
 - Insertar un vehiculo.
 - Actualizar un vehiculo.
 - Borrar cada Vehículo.
2. La aplicación web y el API deben de contar con autenticación de usuario. (Con nombre de usuario y contraseña es suficiente)
3. La Aplicación web debe de contar con una sola vista, en esta vista debe haber un mapa en donde se muestren los vehiculos de cada usuario.
4. Cada Usuario solo debe de poder interactuar con los vehiculos creados por él mismo.

### Instrucciones

1. Crea un repositorio publico en tu cuenta de github.
2. Proveer instrucciones para instalar y levantar en ambiente local la APP.
3. Proveer ejemplos con CURL  para Insertar, actualizar y borrar cada vehículo.

 - Te recomendamos que uses Flask o Django para hacer tu app.
 - Bonus points si agregas Unit Tests.
 - Bonus points si levantas esta API en un servicio como Amazon Web Services o Google Cloud.

La evaluación tendra la siguiente forma:

1. Back End: 35%
2. Front End: 35%
3. Estructura y legilibilidad del código, incluyendo el uso de buenas prácticas: 30%
4. Bonus points: 20% extra (10% unit tests, 10% deployment en la nube).

Suerte!
