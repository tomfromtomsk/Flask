##### IMPORTS #####
from http import HTTPStatus
import json
from random import choice
from typing import List
from core.generic import T, E, Generic_T, Generic_T_E

from flask import request
from flask.views import MethodView
from flask_rest_api import abort
from flask.wrappers import Response

from core.database import db, extract_columns

from marshmallow import fields, Schema


##### GLOBAL #####
UPDATE_METHODS = ["DELETE", "PATCH", "POST", "PUT"]

##### SCHEMAS #####
class CrudCollectionArgsSchema(Schema):
    filter = fields.String(description="Фильтр", missing=None)
    sort = fields.String(description="Сортировка", missing=None)
    page = fields.Int(description="Страница", missing=1)

##### API (COLLECTIONS) #####
class CrudCollection(MethodView, Generic_T[T]):
    def security_check(self):
        # TODO: impl
        req_access_update = request.method in UPDATE_METHODS
        # TODO: decorator
        # mock for now
        if choice([False, False, False, False, True]):
            abort(HTTPStatus.NOT_FOUND, message="Нет доступа к коллекции")

    def get(self, filter: str = None, sort: str = None, page: int = 1) -> List[T]:
        self.security_check()

        items = self.T.query
        # TODO: runtime only, singleton
        columns = extract_columns(self.T)

        # Server side filtering
        if filter:
            filter_field = columns.get(filter, None)
            # TODO raise if filter set but filter_field unknown
            fvalue = request.args.get("fvalue", None, type=str)
            # TODO raise if filter set but fvalue isnt
            if not fvalue:
                abort(HTTPStatus.BAD_REQUEST, message="Фильтр подразумевает fvalue")
            fvalue = json.loads(fvalue)
            items = items.filter(filter_field == fvalue)

        # Server side sorting
        if sort:
            sort_field = columns.get(sort, None)
            # TODO raise if sorted set but sort_field unknown
            if not sort_field:
                abort(HTTPStatus.UNPROCESSABLE_ENTITY, message="Поле %s неизвестно" % sort)
            items = items.order_by(sort_field)

        # Server side pagination
        count = items.order_by(None).count()
        limit = request.args.get("per_page", 20, type=int)
        start = (page-1)*limit
        items = items.limit(limit).offset(start)

        result: List[T] = items.all()
        return result

    def post(self, new_item: T) -> T:
        self.security_check()

        # TODO: check exists
        db.session.add(new_item)
        db.session.commit()
        return new_item

##### API (OBJECTS) #####
class CrudItem(MethodView, Generic_T[T]):
    def security_check(self, id: int, cant_view: int = HTTPStatus.NOT_FOUND) -> T:
        # TODO: impl
        req_access_update = request.method in UPDATE_METHODS
        # TODO: decorator
        item: T = self.T.query.get(id)
        if not item:
            abort(Response(status=cant_view))
        # TODO: can view, but not update (then 403 is issued)
        return item

    def head(self, id: int) -> int:
        self.security_check(id, cant_view=HTTPStatus.NO_CONTENT)
        # implied return 200

    def get(self, id: int) -> T:
        item: T = self.security_check(id)
        return item

    def patch(self, update_data: T, id: int) -> T:
        # security check
        self.security_check(id)

        # additional validation: input should match resource
        state = db.inspect(update_data)
        if not state.persistent or update_data.id != id:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, message="ID аргумента должен быть тем же, что у ресурса")

        db.session.add(update_data)
        db.session.commit()
        return update_data

    def delete(self, id: int) -> int:
        item: T = self.security_check(id)
        #TODO versioning, chg to soft delete
        db.session.delete(item)
        db.session.commit()
        # implied return 200

##### API (CONTAINERS) #####
class CrudContainer(MethodView, Generic_T_E[T, E]):
    def security_check(self, id: int) -> T:
        # TODO: impl
        req_access_update = request.method in UPDATE_METHODS
        # TODO: decorator
        cont: T = self.T.query.get_or_404(id)
        # TODO: can view, but not update (then 403 is issued)
        return cont

    def head(self, attr: str, id: int) -> int:
        items: List[E] = self.get(attr, id)
        if len(items) == 0:
            abort(Response(status=HTTPStatus.NO_CONTENT))
        # implied return 200

    def get(self, attr: str, id: int) -> List[E]:
        cont: T = self.security_check(id)
        return getattr(cont, attr)

    def put(self, attr: str, update_data: List[E], id: int) -> List[E]:
        # security check
        cont: T = self.security_check(id)

        # additional validation: input should exist
        item: E
        for item in update_data:
            state = db.inspect(item)
            if not state.persistent:
                abort(HTTPStatus.UNPROCESSABLE_ENTITY, message="Все переданные объекты должны существовать")

        setattr(cont, attr, update_data)
        db.session.add(cont)
        db.session.commit()
        return getattr(cont, attr)

    def delete(self, attr: str, id: int) -> List[E]:
        return self.put(attr, [], id)

##### API (CONTAINER ITEMS) #####
class CrudContainerItem(MethodView, Generic_T_E[T, E]):
    def security_check_T(self, id: int) -> T:
        # TODO: impl (check update)
        req_access_update = request.method in UPDATE_METHODS
        # TODO: decorator
        cont: T = self.T.query.get_or_404(id)
        # TODO: can view, but not update (then 403 is issued)
        return cont

    def security_check_E(self, eid: int) -> E:
        # TODO: impl (check view)
        # TODO: decorator
        item: E = self.E.query.get_or_404(eid)
        return item

    def head(self, attr: str, id: int, eid: int) -> int:
        cont: T = self.security_check_T(id)
        item: E = self.security_check_E(eid)

        items: List[E] = getattr(cont, attr)
        if item not in items:
            abort(Response(status=HTTPStatus.NO_CONTENT))
        # implied return 200

    def put(self, attr: str, id: int, eid: int) -> int:
        cont: T = self.security_check_T(id)
        item: E = self.security_check_E(eid)

        items: List[E] = getattr(cont, attr)
        if item in items:
            abort(Response(status=HTTPStatus.NOT_MODIFIED))
        items.append(item)
        db.session.add(cont)
        db.session.commit()
        # implied return 200

    def delete(self, attr, id, eid) -> int:
        cont = self.security_check_T(id)
        item = self.security_check_E(eid)

        items = getattr(cont, attr)
        if item not in items:
            abort(Response(status=HTTPStatus.NOT_MODIFIED))
        items.remove(item)
        db.session.add(cont)
        db.session.commit()
        # implied return 200
