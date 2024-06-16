from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"
mail = Mail()
migrate = Migrate()
scheduler = BackgroundScheduler()


def delete_old_pending_users():

    from flaskblog.models import User

    with app.app_context():
        logger.info("Running delete_old_pending_users task.")
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        old_users = User.query.filter(
            User.created_at < cutoff_time, User.email_verified == False
        ).all()
        if old_users:
            logger.info(f"Found {len(old_users)} old pending users to delete.")
            for user in old_users:
                logger.info(
                    f"Deleting user {user.username} created at {user.created_at} with email {user.email}"
                )
                db.session.delete(user)
            db.session.commit()
            logger.info(f"Deleted {len(old_users)} old pending users.")
        else:
            logger.info("No old pending users to delete.")


def create_app(config_class=Config):
    global app
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    if not scheduler.running:
        # Log attempt to start the scheduler
        logger.info("Attempting to start the scheduler.")
        scheduler.add_job(func=delete_old_pending_users, trigger="interval", minutes=1)
        scheduler.start()
        logger.info("Scheduler started for deleting old pending users.")
    else:
        logger.info("Scheduler is already running.")

    return app


app = create_app()
