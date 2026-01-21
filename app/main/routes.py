from app.main import bp

@bp.route('/')
def index():
    return "Bonjour Hub Esport ! Ceci est la page d'accueil."
