##### IMPORTS #####
from http import HTTPStatus

from flask_rest_api import abort
from core.patches import Blueprint
from core.crud import CrudCollection, CrudItem, CrudContainer, CrudContainerItem
from calc.api import calc_api

from sqlalchemy.ext.hybrid import hybrid_property
from core.database import db
from core.traits import Traited
from calc.data_block import DataBlock, DataBlockSummarySchema
from calc.result import Result, ResultSummarySchema

from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema, field_for
from core.crud import CrudCollectionArgsSchema
from core.traits import TraitSchemaMixin
from core.period import PeriodSchema


##### GLOBAL #####
bp_snap = Blueprint('snapshots', __name__, url_prefix="/snapshots", description="API - Срезы")

##### MODELS #####
snap_x_data = db.Table("snapshot_x_data",
    db.Column("snap_id", db.Integer, db.ForeignKey("snapshot.id"), primary_key=True),
    db.Column("snap_data_id", db.Integer, db.ForeignKey("data_block.id"), primary_key=True)
)
snap_x_result = db.Table("snapshot_x_result",
    db.Column("snap_id", db.Integer, db.ForeignKey("snapshot.id"), primary_key=True),
    db.Column("snap_result_id", db.Integer, db.ForeignKey("result.id"), primary_key=True)
)

class Snapshot(Traited):
    id = db.Column(db.Integer, db.ForeignKey("traited.id"), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    period_id = db.Column(db.Integer, db.ForeignKey('period.id'))
    period = db.relationship("Period", backref="snapshots")
    datum = db.relationship("DataBlock",
        secondary=snap_x_data,
        backref=db.backref("snapshots", lazy="dynamic"))
    results = db.relationship("Result",
        secondary=snap_x_result,
        backref=db.backref("results", lazy="dynamic"))

    __mapper_args__ = {
        "polymorphic_identity": "snapshots"
    }

    @hybrid_property
    def has_data(self):
        return len(self.datum) > 0

    @has_data.expression
    def has_data(cls):
        return cls.datum.any()

    @hybrid_property
    def has_result(self):
        return len(self.results) > 0

    @has_result.expression
    def has_result(cls):
        return cls.results.any()

##### SCHEMAS #####
@calc_api.definition("Snapshot", description="Срез")
class SnapshotSchema(ModelSchema, TraitSchemaMixin):
    class Meta:
        model = Snapshot
        sqla_session = db.session

    id = field_for(Snapshot, "id", required=False, description="ID среза")
    name = field_for(Snapshot, "name", description="Описание")
    has_data = fields.Boolean(description="Признак наличия данных")
    has_result = fields.Boolean(description="Признак наличия результата")
    period = fields.Nested("PeriodSchema", description="Отчетный период")
    datum = fields.Nested("DataBlockSummarySchema", many=True, dump_only=True, description="Связанные блоки данных")
    results = fields.Nested("ResultSummarySchema", many=True, dump_only=True, description="Связанные результаты расчета")

@calc_api.definition("SnapshotSummary", description="Срез (сокр)")
class SnapshotSummarySchema(SnapshotSchema):
    class Meta:
        model = Snapshot
        sqla_session = db.session
        exclude = ["datum", "results", "traits"]
    period = field_for(Snapshot, "period", description="Отчетный период")

##### API (COLLECTIONS) #####
@bp_snap.route("")
class SnapshotCollection(CrudCollection[Snapshot]):
    @bp_snap.doc(tags=["data-admins", "web-users"])
    @bp_snap.arguments(CrudCollectionArgsSchema, location="query", as_kwargs=True)
    @bp_snap.response(SnapshotSummarySchema(many=True))
    def get(self, **kwargs):
        """
        Возвращает список Срезов.

        Поддерживается фильтрация, сортировка, пагинация.
        """
        return super().get(**kwargs)

    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.arguments(SnapshotSchema)
    @bp_snap.throws(code=HTTPStatus.BAD_REQUEST, description="Аргумент не соответствует схеме.")
    @bp_snap.throws(code=HTTPStatus.UNPROCESSABLE_ENTITY, description="Аргумент не прошел валидацию.")
    @bp_snap.response(SnapshotSchema, code=HTTPStatus.CREATED)
    def post(self, new_item):
        """
        Создает Срез с переданными атрибутами.
        """
        return super().post(new_item)

##### API (OBJECTS) #####
@bp_snap.route("/<int:id>")
class SnapshotItem(CrudItem[Snapshot]):
    @bp_snap.doc(tags=["data-admins", "web-users"])
    @bp_snap.response(code=HTTPStatus.OK, description="Срез существует.")
    @bp_snap.throws(code=HTTPStatus.NO_CONTENT, description="Срез не существует.")
    def head(self, id):
        """
        Проверяет существование данного Среза.
        """
        return super().head(id)

    @bp_snap.doc(tags=["data-admins", "web-users"])
    @bp_snap.response(SnapshotSchema)
    def get(self, id):
        """
        Возвращает текущее состояние Среза.
        """
        return super().get(id)

    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.arguments(SnapshotSummarySchema)
    @bp_snap.throws(code=HTTPStatus.BAD_REQUEST, description="Аргумент не соответствует схеме.")
    @bp_snap.throws(code=HTTPStatus.UNPROCESSABLE_ENTITY, description="Аргумент не прошел валидацию.")
    #@bp_snap.throws(code=422, description="ID аргумента должен быть тем же, что у ресурса.")
    @bp_snap.response(SnapshotSchema)
    def patch(self, update_data, id):
        """
        Обновляет атрибуты Среза переданными значениями.
        """
        return super().patch(update_data, id)

    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, id):
        """
        Удаляет Срез.
        """
        return super().delete(id)

##### API (CONTAINERS) #####
@bp_snap.route("/<int:id>/datum")
class SnapshotDatumContainer(CrudContainer[Snapshot, DataBlock]):
    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.response(code=HTTPStatus.OK, description="Указанный Срез не пуст")
    @bp_snap.throws(code=HTTPStatus.NO_CONTENT, description="Указанный Срез пуст")
    def head(self, id):
        """
        Проверяет, пуст ли Контейнер.
        """
        return super().head("datum", id)

    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.response(DataBlockSummarySchema(many=True))
    def get(self, id):
        """
        Возвращает коллекцию Блоков данных, входящих в Контейнер.
        """
        return super().get("datum", id)

    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.arguments(DataBlockSummarySchema(many=True))
    @bp_snap.throws(code=HTTPStatus.BAD_REQUEST, description="Аргумент не соответствует схеме.")
    @bp_snap.throws(code=HTTPStatus.UNPROCESSABLE_ENTITY, description="Аргумент не прошел валидацию.")
    #@bp_snap.throws(code=422, description="Все переданные Блоки данных должны существовать")
    @bp_snap.response(DataBlockSummarySchema(many=True))
    def put(self, update_data, id):
        """
        Замещает коллекцию Блоков данных, входящих в Контейнер.
        """
        return super().put("datum", update_data, id)

    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, id):
        """
        Опустошает Контейнер.
        """
        return super().delete("datum", id)

@bp_snap.route("/<int:id>/results")
class SnapshotResultsContainer(CrudContainer[Snapshot, Result]):
    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.response(code=HTTPStatus.OK, description="Указанный Срез не пуст")
    @bp_snap.throws(code=HTTPStatus.NO_CONTENT, description="Указанный Срез пуст")
    def head(self, id):
        """
        Проверяет, пуст ли Контейнер.
        """
        return super().head("results", id)

    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.response(ResultSummarySchema(many=True))
    def get(self, id):
        """
        Возвращает коллекцию Результатов расчета, входящих в Контейнер.
        """
        return super().get("results", id)

    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.arguments(ResultSummarySchema(many=True))
    @bp_snap.throws(code=HTTPStatus.BAD_REQUEST, description="Аргумент не соответствует схеме.")
    @bp_snap.throws(code=HTTPStatus.UNPROCESSABLE_ENTITY, description="Аргумент не прошел валидацию.")
    @bp_snap.response(ResultSummarySchema(many=True))
    def put(self, update_data, id):
        """
        Замещает коллекцию Результатов расчета, входящих в Контейнер.
        """
        return super().put("results", update_data, id)

    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, id):
        """
        Опустошает Контейнер.
        """
        return super().delete("results", id)

##### API (CONTAINER ITEMS) #####
@bp_snap.route("/<int:id>/datum/<int:eid>")
class SnapshotDatumContainerItem(CrudContainerItem[Snapshot, DataBlock]):
    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.response(code=HTTPStatus.OK, description="Указанный Блок данных присутствует в Срезе.")
    @bp_snap.throws(code=HTTPStatus.NO_CONTENT, description="Указанный Блок данных отсутствует в Срезе.")
    def head(self, id, eid):
        """
        Проверяет, присутствует ли указанный Блок данных в Контейнере.
        """
        return super().head("datum", id, eid)

    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.response(code=HTTPStatus.OK)
    def put(self, id, eid):
        """
        Добавляет указанный Блок данных в Контейнер
        """
        return super().put("datum", id, eid)

    @bp_snap.doc(tags=["data-admins"])
    @bp_snap.response(code=HTTPStatus.OK)
    def delete(self, id, eid):
        """
        Удаляет указанный Блок данных из Контейнера
        """
        return super().delete("datum", id, eid)

##### GLOBAL #####
calc_api.register_blueprint(bp_snap)
