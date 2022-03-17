from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import create_app

from core.database import db


app = create_app()

manager = Manager(app)
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
    manager.run()