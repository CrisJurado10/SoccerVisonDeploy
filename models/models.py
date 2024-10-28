import requests
from datetime import datetime

API_KEY = 'e1874afd6ca24ed07b43c8322f67245e'  # Reemplaza con tu API Key
LEAGUE_ID = '242'  # ID de la Liga Pro Ecuador
BASE_URL = 'https://v3.football.api-sports.io'
headers = {
    'x-apisports-key': API_KEY  # Header para la autenticación
}

def get_teams(season=2022):
    """Obtiene la lista de equipos de la Liga Pro Ecuador para una temporada específica."""
    url = f'{BASE_URL}/teams?league={LEAGUE_ID}&season={season}'
    response = requests.get(url, headers=headers)
    teams_data = response.json()
    
    return teams_data['response']  # Devuelve la lista de equipos

def get_team_details(team_id):
    """Obtiene los detalles de un equipo específico y sus últimos resultados."""
    
    # Obtener detalles del equipo
    url = f'{BASE_URL}/teams?id={team_id}'
    response = requests.get(url, headers=headers)
    team_details = response.json()

    # Asegúrate de que la respuesta tiene datos
    if not team_details['response']:
        return None  # Manejar el error si no hay datos de equipo

    # Intentar obtener los resultados de la temporada 2024
    season = 2024
    results_url = f'{BASE_URL}/fixtures?team={team_id}&season={season}'
    results_response = requests.get(results_url, headers=headers)
    results_data = results_response.json()

    # Si no hay resultados para la temporada actual (2024), buscar en 2023 y luego 2022
    if not results_data['response']:
        print(f"No se encontraron resultados para la temporada {season}. Intentando con la temporada 2023...")
        season = 2023
        results_url = f'{BASE_URL}/fixtures?team={team_id}&season={season}'
        results_response = requests.get(results_url, headers=headers)
        results_data = results_response.json()
    
    if not results_data['response']:
        print(f"No se encontraron resultados para la temporada {season}. Intentando con la temporada 2022...")
        season = 2022
        results_url = f'{BASE_URL}/fixtures?team={team_id}&season={season}'
        results_response = requests.get(results_url, headers=headers)
        results_data = results_response.json()

    # Convertir las fechas de los resultados
    for match in results_data['response']:
        match['date'] = convert_date(match['fixture']['date'])
        # Imprimir todos los datos del partido
        print("Detalles del partido:")
        print(match)  # Imprime todo lo que puedes extraer de este partido

    # Devolver detalles del equipo y resultados
    return {
        'team': team_details['response'][0],  # Detalles del equipo
        'results': results_data['response'],  # Últimos resultados
        'season': season  # Temporada en la que se encontraron resultados
    }

def convert_date(date_str):
    """Convierte la fecha de un string a un objeto datetime."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        return None  # En caso de error, devuelve None




