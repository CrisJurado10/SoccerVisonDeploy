import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import contextlib

def create_db_engine():
    DATABASE_URL = "mysql+pymysql://root:HSyAtIJhRXuHjDZiCmfLdrrbXXrrQrVY@autorack.proxy.rlwy.net:58591/railway"
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )
        return engine
    except SQLAlchemyError as e:
        print(f"Database connection error: {str(e)}")
        return None

@contextlib.contextmanager
def get_db_connection():
    engine = create_db_engine()
    if not engine:
        raise RuntimeError("Failed to create database engine")
    try:
        yield engine
    finally:
        engine.dispose()

def cargar_tabla(nombre_tabla):
    try:
        with get_db_connection() as engine:
            return pd.read_sql(f"SELECT * FROM {nombre_tabla}", engine)
    except SQLAlchemyError as e:
        print(f"Error loading table {nombre_tabla}: {str(e)}")
        return pd.DataFrame()

def obtener_datos_equipo(id_equipo, jugadores_df, campeonatos_df):
    jugadores_equipo = jugadores_df[jugadores_df["id_equipo"] == id_equipo]
    campeonatos_equipo = campeonatos_df[campeonatos_df["id_equipo"] == id_equipo]
    
    return {
        "goles_totales": jugadores_equipo["goles"].sum(),
        "asistencias_totales": jugadores_equipo["asistencias"].sum(),
        "max_goleador": jugadores_equipo["goles"].max(),
        "copas_nacionales": campeonatos_equipo["copas_nacionales"].sum(),
        "copas_internacionales": campeonatos_equipo["copas_internacionales"].sum()
    }

def predecir_partido(equipo_local, equipo_visitante):
    try:
        # Tablas necesarias para analizar la data
        equipos = cargar_tabla("equipos")
        partidos = cargar_tabla("partidos")
        jugadores = cargar_tabla("jugadores")
        campeonatos = cargar_tabla("campeonatos")

        if equipos.empty or partidos.empty or jugadores.empty or campeonatos.empty:
            return "Error: No se pudieron cargar los datos necesarios"

        # Get team statistics
        datos_local = obtener_datos_equipo(equipo_local, jugadores, campeonatos)
        datos_visitante = obtener_datos_equipo(equipo_visitante, jugadores, campeonatos)

        # Create performance DataFrame
        historial_local = partidos[partidos['equipo_local'] == equipo_local]
        historial_visitante = partidos[partidos['equipo_visitante'] == equipo_visitante]

        # Calculate team metrics using pandas
        metricas_local = pd.Series({
            'promedio_goles': historial_local['goles_local'].mean(),
            'efectividad_gol': datos_local['goles_totales'] / max(len(historial_local), 1),
            'ratio_asistencias': datos_local['asistencias_totales'] / max(datos_local['goles_totales'], 1),
            'indice_titulos': datos_local['copas_nacionales'] * 1.5 + datos_local['copas_internacionales'] * 2
        })

        metricas_visitante = pd.Series({
            'promedio_goles': historial_visitante['goles_visitante'].mean(),
            'efectividad_gol': datos_visitante['goles_totales'] / max(len(historial_visitante), 1),
            'ratio_asistencias': datos_visitante['asistencias_totales'] / max(datos_visitante['goles_totales'], 1),
            'indice_titulos': datos_visitante['copas_nacionales'] * 1.5 + datos_visitante['copas_internacionales'] * 2
        })

        # Calculate weighted performance scores
        pesos = {
            'promedio_goles': 0.35,
            'efectividad_gol': 0.25,
            'ratio_asistencias': 0.20,
            'indice_titulos': 0.20
        }

        score_local = sum(metricas_local[metric] * weight for metric, weight in pesos.items()) * 1.1  # Home advantage
        score_visitante = sum(metricas_visitante[metric] * weight for metric, weight in pesos.items())

        # Normalize scores
        total_score = score_local + score_visitante
        prob_local = score_local / total_score
        prob_visitante = score_visitante / total_score

        # Calculate expected goals using historical data
        goles_esperados_local = round(metricas_local['promedio_goles'] * 1.1)  # Home advantage
        goles_esperados_visitante = round(metricas_visitante['promedio_goles'])

        # Generate detailed prediction
        return {
            "resultado": "Victoria Local" if prob_local > prob_visitante else "Victoria Visitante" if prob_visitante > prob_local else "Empate",
            "probabilidad_local": f"{prob_local * 100:.2f}%",
            "probabilidad_visitante": f"{prob_visitante * 100:.2f}%",
            "marcador_probable": f"{goles_esperados_local}-{goles_esperados_visitante}",
            "estadisticas": {
                "local": metricas_local.to_dict(),
                "visitante": metricas_visitante.to_dict()
            }
        }

    except Exception as e:
        return f"Error al predecir: {str(e)}"



if __name__ == "__main__":
    try:
        equipos = cargar_tabla("equipos")
        if not equipos.empty:
            print("Equipos disponibles:")
            print(equipos["nombre"].tolist())

            equipo_local = input("Ingresa el nombre del equipo local: ")
            equipo_visitante = input("Ingresa el nombre del equipo visitante: ")

            id_local = equipos[equipos["nombre"] == equipo_local]["id_equipo"].values[0]
            id_visitante = equipos[equipos["nombre"] == equipo_visitante]["id_equipo"].values[0]

            pronostico = predecir_partido(id_local, id_visitante)
            print(pronostico)
        else:
            print("Error: No se pudieron cargar los equipos de la base de datos")
    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")