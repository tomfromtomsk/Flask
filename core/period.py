##### IMPORTS #####
from http import HTTPStatus
from enum import Enum

from core.patches import Blueprint
from core.crud import CrudCollection, CrudItem
from core.api import core_api

from core.database import db

from marshmallow import fields, ValidationError
from marshmallow_sqlalchemy import ModelSchema, field_for
from core.patches import EnumField
from core.crud import CrudCollectionArgsSchema


##### GLOBAL #####
bp_per = Blueprint('periods', __name__, url_prefix="/periods", description="API - Отчетные периоды")

##### MODELS #####
class PeriodType(Enum):
    DAY = "Day"
    YEAR = "Year"

class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(PeriodType, name="period_type"), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer)
    week = db.Column(db.Integer)
    day = db.Column(db.Integer)

##### SCHEMAS #####
@core_api.definition("Period", description="Отчетный период")
class PeriodSchema(ModelSchema):
    class Meta:
        model = Period
        sqla_session = db.session

    id      =   field_for(Period, "id",     description="ID отчетного периода",     required=False)
    type =      EnumField(PeriodType,       description="Тип отчетного периода")
    year    =   field_for(Period, "year",   description="Год")
    month   =   field_for(Period, "month",  description="Месяц")
    week    =   field_for(Period, "week",   description="Неделя")
    day     =   field_for(Period, "day",    description="День")

PERIOD_SCHEMA = PeriodSchema

##### API (COLLECTIONS) #####
@bp_per.route("")
class PeriodCollection(CrudCollection[Period]):
    @bp_per.doc(tags=["cfg-admins", "data-admins", "web-users"])
    @bp_per.arguments(CrudCollectionArgsSchema, location="query", as_kwargs=True)
    @bp_per.response(PeriodSchema(many=True))
    def get(self, **kwargs):
        """
        Возвращает список Отчетных периодов.

        Поддерживается фильтрация, сортировка, пагинация.
        """
        return super().get(**kwargs)

    @bp_per.doc(tags=["cfg-admins", "web-users"])
    @bp_per.arguments(PeriodSchema)
    @bp_per.throws(code=HTTPStatus.BAD_REQUEST, description="Аргумент не соответствует схеме.")
    @bp_per.throws(code=HTTPStatus.UNPROCESSABLE_ENTITY, description="Аргумент не прошел валидацию.")
    @bp_per.response(PeriodSchema, code=HTTPStatus.CREATED)
    def post(self, new_item):
        """
        Создает Отчетный период с переданными атрибутами.
        """
        return super().post(new_item)

##### API (OBJECTS) #####
@bp_per.route("/<int:id>")
class PeriodItem(CrudItem[Period]):
    @bp_per.doc(tags=["cfg-admins", "data-admins"])
    @bp_per.response(code=HTTPStatus.OK, description="Отчетный период существует.")
    @bp_per.throws(code=HTTPStatus.NO_CONTENT, description="Отчетного периода не существует.")
    def head(self, id):
        """
        Проверяет существование данного Отчетного периода.
        """
        return super().head(id)

    @bp_per.doc(tags=["cfg-admins", "data-admins", "web-users"])
    @bp_per.response(PERIOD_SCHEMA)
    def get(self, id):
        """
        Возвращает текущее состояние Отчетного периода.
        """
        return super().get(id)

    @bp_per.arguments(PeriodSchema)
    @bp_per.throws(code=HTTPStatus.BAD_REQUEST, description="Аргумент не соответствует схеме.")
    @bp_per.throws(code=HTTPStatus.UNPROCESSABLE_ENTITY, description="Аргумент не прошел валидацию.")
    @bp_per.response(PeriodSchema)
    def patch(self, update_data, id):
        """
        Обновляет атрибуты Отчетного периода переданными значениями.
        """
        return super().patch(update_data, id)

    @bp_per.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, id):
        """
        Удаляет Отчетный период.
        """
        return super().delete(id)

##### GLOBAL #####
core_api.register_blueprint(bp_per)
