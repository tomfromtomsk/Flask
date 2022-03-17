from core.patches import Api
from core.schemas import ValidationSchema


class CalcAPI(Api):
    def setup_api(self, app):
        with app.app_context():
            name = app.name
            app.name = "calc"
            calc_api.init_app(app)
            app.name = name

            calc_api.spec.add_tag({
                "name": "web-users",
                "description": "Функции, доступные пользователям веб-интерфейса",
            })
            calc_api.spec.add_tag({
                "name": "data-admins",
                "description": "Функции, доступные Администратору данных",
            })
            calc_api.spec.definition(
                "Validation", schema=ValidationSchema,
                description="Ошибки при валидации"
            )

calc_api = CalcAPI()
