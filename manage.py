#!/usr/bin/env python3
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from src.app import APP
from src.models import setup_db, db

setup_db(APP)

migrate = Migrate(APP, db)
manager = Manager(APP)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
