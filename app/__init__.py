"""Flask application factory."""
import logging
from datetime import datetime, timezone
import click
from flask import Flask, jsonify, render_template, request
from config import Config
from .extensions import db, migrate, login_manager, csrf, limiter


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Fail fast on missing critical config
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY is missing. Check your configuration.")
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("DATABASE_URL is missing. Check your configuration.")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # User loader for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    # Global context processors for templates
    @app.context_processor
    def inject_global_data():
        from flask_login import current_user
        from app.services.notification_service import get_unread_count

        unread_count = 0
        if current_user.is_authenticated:
            try:
                unread_count = get_unread_count(current_user.id)
            except Exception:
                unread_count = 0

        return {
            "unread_count": unread_count,
            "current_year": datetime.now(timezone.utc).year,
            "now_utc": datetime.now(timezone.utc),
        }

    _register_blueprints(app)
    _register_error_handlers(app)
    _register_cli_commands(app)
    _configure_logging(app)

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    # Automatically create tables in SQLite if they don't exist yet
    with app.app_context():
        try:
            db.create_all()
            # If database is freshly initialized and has no users, automatically seed demo data
            from app.models.user import User
            if User.query.count() == 0:
                from app.services.seed_service import seed_database
                seed_database()
        except Exception as e:
            app.logger.warning(f"Database bootstrap note: {e}")

    return app


def _register_blueprints(app):
    from app.auth import bp as auth_bp
    from app.dashboard import bp as dashboard_bp
    from app.skills import bp as skills_bp
    from app.bookings import bp as bookings_bp
    from app.video import bp as video_bp
    from app.wallet import bp as wallet_bp
    from app.reviews import bp as reviews_bp
    from app.notifications import bp as notifications_bp
    from app.ai import bp as ai_bp
    from app.admin import bp as admin_bp
    from app.settings import bp as settings_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(wallet_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(settings_bp)


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/") or request.headers.get("Accept") == "application/json":
            return jsonify(error="Not found"), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        if request.path.startswith("/api/") or request.headers.get("Accept") == "application/json":
            return jsonify(error="Internal server error"), 500
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith("/api/") or request.headers.get("Accept") == "application/json":
            return jsonify(error="Forbidden"), 403
        return render_template("errors/403.html"), 403


def _register_cli_commands(app):
    @app.cli.command("seed-db")
    def seed_db_command():
        """Seed database with realistic initial demo data."""
        from app.services.seed_service import seed_database
        with app.app_context():
            seed_database()
            click.echo("SkillSwap database seeded successfully!")

    @app.cli.command("create-admin")
    @click.option("--username", prompt="Admin username", default="admin")
    @click.option("--email", prompt="Admin email", default="admin@skillswap.com")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin_command(username, email, password):
        """Create a new administrator account."""
        from app.models.user import User
        from app.services.wallet_service import get_or_create_wallet, add_bonus_credits
        from decimal import Decimal

        with app.app_context():
            user = User.query.filter((User.username == username) | (User.email == email)).first()
            if user:
                click.echo("Error: User with this username or email already exists.")
                return

            admin_user = User(
                username=username,
                email=email,
                full_name="Administrator",
                role="admin",
                status="active",
            )
            admin_user.set_password(password)
            db.session.add(admin_user)
            db.session.commit()
            
            get_or_create_wallet(admin_user.id)
            add_bonus_credits(admin_user.id, Decimal("10.00"), "Admin initial allocation")
            click.echo(f"Admin account '{username}' created successfully!")


def _configure_logging(app):
    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)
