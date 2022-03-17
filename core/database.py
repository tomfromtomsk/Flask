from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.interfaces import NOT_EXTENSION


db = SQLAlchemy()
migrate = Migrate()

def setup_database(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        migrate.init_app(app, db)

def extract_columns(model_cls):
    insp = db.inspect(model_cls)
    columns = dict(insp.columns)
    for k, v in insp.all_orm_descriptors.items():
        if  v.extension_type is not NOT_EXTENSION:
            columns[k] = getattr(model_cls, k)
    return columns
