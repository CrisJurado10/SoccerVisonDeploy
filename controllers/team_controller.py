from flask import render_template, session
from models.models import get_teams, get_team_details

def index():
    """Controlador para la página principal que muestra la lista de equipos."""
    teams = get_teams()  # Obtiene la lista de equipos desde el modelo
    return render_template('teams.html', teams=teams, usuario=session.get('usuario'), correo=session.get('correo'))

def team_details(team_id):
    team_data = get_team_details(team_id)
    print(team_data)  # Esto te mostrará qué estás recibiendo

    if team_data is None:
        return "Datos del equipo no encontrados", 404

    return render_template('team_details.html', team=team_data['team'], results=team_data['results'])
