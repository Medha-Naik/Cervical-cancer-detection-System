"""CervixGuard AI - Flask application factory."""
from datetime import date

from flask import Flask, session

from . import config
from .db import init_db
from .ml.model import load_model
from .services import users
from .translations import LANG_NAMES, get_translator


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    init_db()
    print("Database ready:", config.DB_PATH)
    load_model()

    @app.context_processor
    def inject_globals():
        lang = session.get("lang", "en")
        user_id = session.get("user_id")
        return {
            "profile": users.get_profile(user_id) if user_id else None,
            "current_year": date.today().year,
            "t": get_translator(lang),
            "current_lang": lang,
            "lang_names": LANG_NAMES,
            "current_user": session.get("username"),
        }

    from .routes import assess, auth, chat, dashboard, vaccine
    for module in (auth, assess, dashboard, vaccine, chat):
        app.register_blueprint(module.bp)

    return app
