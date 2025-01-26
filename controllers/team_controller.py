from flask import render_template, request, session, jsonify
from models.models import get_teams, get_team_details

# Factory for creating controllers
def index():
    """Controlador para la página principal que muestra la lista de equipos."""
    teams = get_teams()  # Obtiene la lista de equipos desde el modelo
    return render_template('teams.html', teams=teams, usuario=session.get('usuario'), correo=session.get('correo'))

def team_details(team_id):
    team_data = get_team_details(team_id)
    print(team_data)  # Esto mostrará qué estás recibiendo

    if team_data is None:
        return "Datos del equipo no encontrados", 404

    return render_template('team_details.html', team=team_data['team'], results=team_data['results'])

# New function for statistics page
def statics():
    """Controlador para la página de estadísticas."""
    teams = get_teams()  # Obtiene la lista de equipos desde el modelo
    return render_template('statics.html', teams=teams)

# New function to fetch team data via AJAX
def fetch_team_statistics():
    """Controlador para obtener estadísticas de un equipo específico."""
    team_id = request.args.get('team_id')
    
    if not team_id:
        return jsonify({'error': 'No se proporcionó ID del equipo'}), 400
    
    team_data = get_team_details(team_id)
    
    if not team_data:
        return jsonify({'error': 'Datos del equipo no encontrados'}), 404
    
    # Return the match results as JSON for frontend processing
    return jsonify({
        'team': team_data['team'],
        'results': team_data['results']
    })
