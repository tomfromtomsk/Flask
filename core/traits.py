##### IMPORTS #####
from core.database import db
from sqlalchemy.ext.declarative import declared_attr

from marshmallow import fields, pre_load, post_dump
from marshmallow_sqlalchemy import ModelSchema


##### GLOBAL #####

##### MODELS #####
class Traited(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    traits = db.relationship("Trait")

    __mapper_args__ = {
        "polymorphic_identity": "traited",
        "polymorphic_on": type
    }

class Trait(db.Model):
    __tablename__ = 'traited_x_trait'
    id = db.Column(db.Integer, db.ForeignKey("traited.id"), primary_key=True)
    key = db.Column(db.String(20), primary_key=True)
    value = db.Column(db.String(20), primary_key=True)

##### SCHEMAS #####
class TraitSchema(ModelSchema):
    class Meta:
        model = Trait
        sqla_session = db.session

class TraitSchemaMixin():
    traits = fields.Nested("TraitSchema", many=True)

    @pre_load
    def load_traits(self, data):
        traits = data.pop("traits", None)
        if traits:
            traits_proxy = []
            for item in traits:
                for key, values in item.items():
                    for value in values:
                        traits_proxy.append({"key": key, "value": value})
            data["traits"] = traits_proxy
        return data

    @post_dump
    def dump_traits(self, data):
        traits_proxy = data.pop("traits", None)
        if traits_proxy:
            traits = {}
            for item in traits_proxy:
                key = item["key"]
                if key not in traits:
                    traits[key] = []
                traits[key].append(item["value"])
            data["traits"] = traits
        return data

##### API #####
