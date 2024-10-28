﻿# SoccerVisonDeploy
# Descripción
SoccerVisonDeploy es una aplicación web que usa inteligencia artificial para analizar  datos, procesarlos y realizar predicciones en base a estadísticas de partidos de fútbol y generar estadísticas visuales. Implementado en Flask, el sistema permite despliegue en la nube, facilitando el acceso a entrenadores y aficionados que buscan datos de rendimiento y predicciones fundamentadas en data del fútbol ecuatoriano.

# Características
Análisis de Videos de Fútbol: La aplicación permite subir videos de partidos para realizar análisis automáticos, generando estadísticas basadas en los eventos detectados.
Visualización de Estadísticas: Muestra gráficos e información visual sobre el rendimiento de los jugadores o el equipo.
Interfaz Amigable: La interfaz está diseñada para facilitar la navegación y el análisis de datos para usuarios técnicos y no técnicos.
Inteligencia Artificial: Utiliza modelos de IA para procesar la data extraida de API FOOTBALL y tenga la capacidad de predecir resultados del la liga pro ecuador.

# Instalación
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

Uso
Accede a la aplicación en http://localhost:5000.

# Requisitos previos
Python 3.x
MySQL
Pip #Los demás requerimientos están en: requirements.txt.

# Despliegue en Railway
La aplicación recupera datos de una base de datos MySQL alojada en un servidor de Railway.

# Despliegue en Render
Este proyecto está configurado para ejecutarse en Render con un archivo Procfile que define el comando de inicio para la aplicación.

# Licencia
Este proyecto está bajo la Licencia MIT.
