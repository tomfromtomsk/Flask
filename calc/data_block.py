##### IMPORTS #####
from http import HTTPStatus

from core.patches import Blueprint
from core.crud import CrudCollection, CrudItem
from calc.api import calc_api

from core.database import db

from marshmallow import fields, ValidationError
from marshmallow_sqlalchemy import ModelSchema, field_for
from core.crud import CrudCollectionArgsSchema


##### GLOBAL #####
bp_datum = Blueprint('datum', __name__, url_prefix="/datum", description="API - Блоки данных")

##### MODELS #####
class DataBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False, default="datum")

##### SCHEMAS #####
@calc_api.definition("DataBlock", description="Блок данных")
class DataBlockSchema(ModelSchema):
    class Meta:
        model = DataBlock
        sqla_session = db.session

    id = field_for(DataBlock, "id", description="ID блока данных")
    type = fields.Constant("datum")
    snapshots = fields.Nested("SnapshotSummarySchema", many=True, dump_only=True, description="Связанные срезы")

@calc_api.definition("DataBlockSummary", description="Блок данных (сокр)")
class DataBlockSummarySchema(DataBlockSchema):
    class Meta:
        model = DataBlock
        sqla_session = db.session
        exclude = ["snapshots"]

##### API (COLLECTIONS) #####
@bp_datum.route("")
class DataBlockCollection(CrudCollection[DataBlock]):
    @bp_datum.doc(tags=["data-admins"])
    @bp_datum.arguments(CrudCollectionArgsSchema, location="query", as_kwargs=True)
    @bp_datum.response(DataBlockSummarySchema(many=True))
    def get(self, **kwargs):
        """
        Возвращает список Блоков данных.

        Поддерживается фильтрация, сортировка, пагинация.
        """
        return super().get(**kwargs)

    @bp_datum.doc(tags=["data-admins"])
    @bp_datum.arguments(DataBlockSchema)
    @bp_datum.throws(code=HTTPStatus.BAD_REQUEST, description="Аргумент не соответствует схеме.")
    @bp_datum.throws(code=HTTPStatus.UNPROCESSABLE_ENTITY, description="Аргумент не прошел валидацию.")
    @bp_datum.response(DataBlockSchema, code=HTTPStatus.CREATED)
    def post(self, new_item):
        """
        Создает Блок данных с переданными атрибутами.
        """
        return super().post(new_item)

##### API (OBJECTS) #####
@bp_datum.route("/<int:id>")
class DataBlockItem(CrudItem[DataBlock]):
    @bp_datum.doc(tags=["data-admins"])
    @bp_datum.response(code=HTTPStatus.OK, description="Блок данных существует.")
    @bp_datum.throws(code=HTTPStatus.NO_CONTENT, description="Блок данных не существует.")
    def head(self, id):
        """
        Проверяет существование данного Блока данных.
        """
        return super().head(id)

    @bp_datum.doc(tags=["data-admins"])
    @bp_datum.response(DataBlockSchema)
    def get(self, id):
        """
        Возвращает текущее состояние Блока данных.
        """
        return super().get(id)

    @bp_datum.doc(tags=["data-admins"])
    @bp_datum.arguments(DataBlockSummarySchema)
    @bp_datum.throws(code=HTTPStatus.BAD_REQUEST, description="Аргумент не соответствует схеме.")
    @bp_datum.throws(code=HTTPStatus.UNPROCESSABLE_ENTITY, description="Аргумент не прошел валидацию.")
    @bp_datum.response(DataBlockSchema)
    def patch(self, update_data, id):
        """
        Обновляет атрибуты Блока данных переданными значениями.
        """
        return super().patch(update_data, id)

    @bp_datum.doc(tags=["data-admins"])
    @bp_datum.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, id):
        """
        Удаляет Блок данных.
        """
        return super().delete(id)

##### GLOBAL #####
calc_api.register_blueprint(bp_datum)
