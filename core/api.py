from core.patches import Api

class CoreAPI(Api):
    def setup_api(self, app):
        with app.app_context():
            name = app.name
            app.name = "core"
            core_api.init_app(app)
            app.name = name

core_api = CoreAPI()
