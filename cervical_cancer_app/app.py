from flask import Flask
from config import SECRET_KEY
from db.database import init_db
from ml.predictor import load_model
from utils.logging_setup import configure_logging



# ── Blueprints ────────────────────────────────────────────────────────────────
from blueprints.predictions import predictions_bp
from blueprints.dashboard   import dashboard_bp
from blueprints.vaccine     import vaccine_bp
from blueprints.api         import api_bp
from blueprints.auth import auth_bp
from db.database            import init_db
from ml.predictor           import load_model
from utils.logging_setup    import configure_logging


def create_app(debug: bool = False) -> Flask:
    configure_logging(debug)

    app            = Flask(__name__)
    app.secret_key = SECRET_KEY

    # ── One-time startup tasks ─────────────────────────────────────────────
    with app.app_context():
        init_db()
        load_model()

    # ── Register blueprints ────────────────────────────────────────────────
    app.register_blueprint(predictions_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vaccine_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    
    return app


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = create_app(debug=True)
    app.run(debug=True)