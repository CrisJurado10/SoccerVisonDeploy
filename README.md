
### SOCCERVISON APP WEB
## Índice
- [Descripción](#descripción)
- [Características](#características)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Despliegue en Railway](#despliegue-en-railway)
- [Despliegue en Render](#despliegue-en-render)
- [Licencia](#licencia)
## Descripción
SoccerVisonDeploy es una aplicación web que usa inteligencia artificial para analizar  datos, procesarlos y realizar predicciones en base a estadísticas de partidos de fútbol y generar estadísticas visuales. Implementado en Flask, el sistema permite despliegue en la nube, facilitando el acceso a entrenadores y aficionados que buscan datos de rendimiento y predicciones fundamentadas en data del fútbol ecuatoriano.

## Características
1. Protección de tu información sensible: Constraseñas guardadas en el servidor de la base de datos en formato hash.
2. Análisis de Videos de Fútbol: La aplicación permite subir videos de partidos para realizar análisis automáticos, generando estadísticas basadas en los eventos detectados.
3. Visualización de Estadísticas: Muestra gráficos e información visual sobre el rendimiento de los jugadores o el equipo.
4. Interfaz Amigable: La interfaz está diseñada para facilitar la navegación y el análisis de datos para usuarios técnicos y no técnicos.
5. Inteligencia Artificial: Utiliza modelos de IA para procesar la data extraida de API FOOTBALL y tenga la capacidad de predecir resultados del la liga pro ecuador.

## Requisitos previos
Python 3.x
MySQL
Pip #Los demás requerimientos están en: requirements.txt.

## Instalación
Clona el repositorio:
bash
Copiar código
git clone https://github.com/CrisJurado10/SoccerVisonDeploy.git
cd SoccerVisonDeploy

Instala las dependencias:
bash
Copiar código
pip install -r requirements.txt

Inicia la aplicación:
bash
Copiar código
flask run

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    contraseña VARCHAR(100) NOT NULL
);

Uso
Accede a la aplicación en http://localhost:5000.



## Despliegue en Railway
La aplicación recupera datos de una base de datos MySQL alojada en un servidor de Railway.

## Despliegue en Render
Este proyecto está configurado para ejecutarse en Render con un archivo Procfile que define el comando de inicio para la aplicación.
Link web deployada: https://soccervisondeploy.onrender.com/

## Licencia
Este proyecto está bajo la Licencia MIT.
