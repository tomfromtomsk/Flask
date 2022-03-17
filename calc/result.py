##### IMPORTS #####
from http import HTTPStatus

from core.patches import Blueprint
from core.crud import CrudCollection, CrudItem
from calc.api import calc_api

from core.database import db
from core.traits import Traited

from marshmallow import fields, ValidationError
from marshmallow_sqlalchemy import ModelSchema, field_for
from core.crud import CrudCollectionArgsSchema
from core.traits import TraitSchemaMixin


##### GLOBAL #####
bp_res = Blueprint('results', __name__, url_prefix="/results", description="API - Результаты расчета")

##### MODELS #####
class Result(Traited):
    id = db.Column(db.Integer, db.ForeignKey("traited.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "results"
    }

##### SCHEMAS #####
@calc_api.definition("Result", description="Результат расчета")
class ResultSchema(ModelSchema, TraitSchemaMixin):
    class Meta:
        model = Result
        sqla_session = db.session

    id = field_for(Result, "id", required=False, description="ID результата расчета")
    snapshots = fields.Nested("SnapshotSummarySchema", many=True, dump_only=True, description="Связанные срезы")

@calc_api.definition("ResultSummary", description="Результат расчета (сокр)")
class ResultSummarySchema(ResultSchema):
    class Meta:
        model = Result
        sqla_session = db.session
        exclude = ["snapshots", "traits"]

##### API (COLLECTIONS) #####
@bp_res.route("")
class ResultCollection(CrudCollection[Result]):
    @bp_res.doc(tags=["data-admins"])
    @bp_res.arguments(CrudCollectionArgsSchema, location="query", as_kwargs=True)
    @bp_res.response(ResultSummarySchema(many=True))
    def get(self, **kwargs):
        """
        Возвращает список Результатов расчета.

        Поддерживается фильтрация, сортировка, пагинация.
        """
        return super().get(**kwargs)

    @bp_res.arguments(ResultSchema)
    @bp_res.throws(code=HTTPStatus.BAD_REQUEST, description="Аргумент не соответствует схеме.")
    @bp_res.throws(code=HTTPStatus.UNPROCESSABLE_ENTITY, description="Аргумент не прошел валидацию.")
    @bp_res.response(ResultSchema, code=HTTPStatus.CREATED)
    def post(self, new_item):
        """
        Создает Результат расчета с переданными атрибутами.
        """
        return super().post(new_item)

##### API (OBJECTS) #####
@bp_res.route("/<int:id>")
class ResultItem(CrudItem[Result]):
    @bp_res.doc(tags=["data-admins"])
    @bp_res.response(code=HTTPStatus.OK, description="Результат расчета существует.")
    @bp_res.throws(code=HTTPStatus.NO_CONTENT, description="Результат расчета не существует.")
    def head(self, id):
        """
        Проверяет существование данного Результата расчета.
        """
        return super().head(id)

    @bp_res.doc(tags=["data-admins"])
    @bp_res.response(ResultSchema)
    def get(self, id):
        """
        Возвращает текущее состояние Результата расчета.
        """
        return super().get(id)

    @bp_res.arguments(ResultSummarySchema)
    @bp_res.throws(code=HTTPStatus.BAD_REQUEST, description="Аргумент не соответствует схеме.")
    @bp_res.throws(code=HTTPStatus.UNPROCESSABLE_ENTITY, description="Аргумент не прошел валидацию.")
    @bp_res.response(ResultSchema)
    def patch(self, update_data, id):
        """
        Обновляет атрибуты Результата расчета переданными значениями.
        """
        return super().patch(update_data, id)

    @bp_res.doc(tags=["data-admins", "web-users"])
    @bp_res.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, id):
        """
        Удаляет Результат расчета.
        """
        return super().delete(id)

##### GLOBAL #####
calc_api.register_blueprint(bp_res)
