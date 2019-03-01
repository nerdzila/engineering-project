# engineering-project
Engineering Project

## Aplicación de Rastreo

El objetivo es construir una applicación web donde se administre una flotilla de vehiculos y se pueda ver su posición.
Cada vehiculo tiene los siguientes datos:

1. Id de Vehiculo
2. Placas
3. Ultima posición conocida (lat,lon)

## Requerimientos

1. Construir un API HTTP Rest con  en la que se pueda a) Insertar, b) Actualizar, c) Borrar cada Vehículo.
2. La aplicación web y el API deben de contar con autenticación de usuario. (Con nombre de usuario y contraseña es suficiente)
3. La Aplicación web debe de contar con una sola vista, en esta vista debe haber un mapa en donde se muestren los vehiculos de cada usuario.
4. Cada Usuario solo debe de poder interactuar con los vehiculos creados por él mismo.
5. Proveer ejemplos con CURL  para a) Insertar, b) Actualizar, c) Borrar cada Vehículo.
6. Proveer instrucciones para instalar y levantar en ambiente local la APP.

## Instrucciones

Crea un repositorio en tu cuenta de github. Te recomendamos que uses Flask o Django para hacer tu app. Bonus points si agregas Unit Tests. En el README.md del repo provee instrucciones de como instalar y levantar tu API en un ambiente local. Bonus points si levantas esta API en un servicio como Amazon Web Services o Google Cloud. 

La evaluación tendra la siguiente forma:

1. Back End: 35%
2. Front End: 35%
3. Estructura y legilibilidad del código, incluyendo el uso de buenas prácticas: 30%
4. Bonus points: 10% extra.
