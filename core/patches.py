from copy import deepcopy
from functools import wraps

import flask_rest_api
from flask_rest_api.utils import deepupdate

from core.schemas import ValidationSchema
from core.traits import TraitSchemaMixin
import marshmallow_enum as menum


class Api(flask_rest_api.Api):
    def definition(self, name, **kwargs):
        """
        PATCH: kwargs should have been in definition(), not decorator.
        """
        def decorator(schema_cls):
            self.spec.definition(name, schema=schema_cls, **kwargs)

            # HACK: patch traits doc
            if issubclass(schema_cls, TraitSchemaMixin):
                self.spec._definitions[name]["properties"]["traits"] = {
                    "type": "object",
                    "default": {},
                    "readOnly": True,
                    "additionalProperties": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Свойство"
                    },
                    "description": "Свойства"
                }

            return schema_cls
        return decorator


class Blueprint(flask_rest_api.Blueprint):
    def register_views_in_doc(self, app, spec):
        """
        PATCH: operation tags should be appended, not replaced
        """
        for endpoint, doc in self._docs.items():
            endpoint = '.'.join((self.name, endpoint))

            for operation in doc.values():
                if 'tags' not in operation:
                    operation['tags'] = []
                operation['tags'].append(self.name)
                self._prepare_doc(operation, spec.openapi_version)

            for rule in app.url_map.iter_rules(endpoint):
                spec.add_path(app=app, rule=rule, operations=deepcopy(doc))

    # PATCH: ADDED
    def throws(self, schema=ValidationSchema, *, code=400, description=''):
        """Decorator generating additional endpoint response

        :param schema: :class:`Schema <marshmallow.Schema>` class or instance.
            If not None, will be used to serialize response data.
        :param int code: HTTP status code (default: 400).
        :param str descripton: Description of the response.
        """
        if isinstance(schema, type):
            schema = schema()

        def decorator(func):
            # Add schema as response in the API doc
            doc = {'responses': {code: {'description': description}}}
            doc_schema = self._make_doc_response_schema(schema)
            if doc_schema:
                doc['responses'][code]['schema'] = doc_schema
            func._apidoc = deepupdate(getattr(func, '_apidoc', {}), doc)

            @wraps(func)
            def wrapper(*args, **kwargs):
                # Return decorated function
                return func(*args, **kwargs)

            return wrapper
        return decorator


class EnumField (menum.EnumField):
    def __init__(self, enum, by_value=False, load_by=None, dump_by=None, error='', *args,
                 **kwargs):
        super().__init__(enum, by_value, load_by, dump_by, error, *args, **kwargs)
        self.metadata['enum'] = [e.value if self.by_value else e.name for e in enum]
