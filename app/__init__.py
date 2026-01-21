from flask import Flask
from config import Config

# On initialise l'extension DB ici (on la liera plus tard)
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialisation des extensions (à décommenter plus tard)
    # db.init_app(app)

    # Enregistrement du Blueprint "Main" (pour la page d'accueil)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # On teste juste une route simple pour voir si ça marche
    @app.route('/test')
    def test_page():
        return '<h1>L architecture fonctionne ! 🚀</h1>'

    return app