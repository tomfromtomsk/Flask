from flask import Flask

from core.database import setup_database
from core.api import core_api
from calc.api import calc_api


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("flask.cfg")
    #app.url_map.strict_slashes = False
    #app.config['DEBUG'] = True
    setup_database(app)

    app.config['OPENAPI_URL_PREFIX'] = None
    core_api.setup_api(app)
    app.config['OPENAPI_URL_PREFIX'] = "/api/calc"
    calc_api.setup_api(app)
    import calc.snapshot
    import calc.data_block
    #print(app.url_map)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
