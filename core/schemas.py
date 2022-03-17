##### IMPORTS #####
from marshmallow import fields, Schema

##### GLOBAL #####

##### SCHEMAS #####
class ValidationSchema(Schema):
    status = fields.Str()
    errors = fields.Dict(keys=fields.Str(description="Атрибут"), values=fields.List(fields.Str(), description="Ошибки проверки атрибута"), description="Ошибки", missing={})
