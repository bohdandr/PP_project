from flask_bcrypt import generate_password_hash
from marshmallow import validate, Schema, fields
from datetime import date


class UserData(Schema):
    id = fields.Integer()
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String()
    password = fields.String()
    phone = fields.String()
    birthDate = fields.Date()
    wallet = fields.Float()
    userStatus = fields.String()
    isAdmin = fields.String()


class GetUser(Schema):
    id = fields.Integer()
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String()
    phone = fields.String()
    birthDate = fields.Date()
    userStatus = fields.String()
    isAdmin = fields.String()


class CreateUser(Schema):
    username = fields.String(required=True, validate=validate.Regexp('^[a-zA-Z\d\.-_]{4,120}$'))
    firstName = fields.String(required=True, validate=validate.Length(min=2))
    lastName = fields.String(required=True, validate=validate.Length(min=2))
    email = fields.String(required=True, validate=validate.Email())
    password = fields.Function(required=True, deserialize=lambda obj: generate_password_hash(obj), load_only=True)
    phone = fields.Function(validate=validate.Regexp('^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[\s0-9]{4,20}$'))
    birthDate = fields.Date(validate=lambda x: x < date.today())
    wallet = fields.Float(validate=validate.Range(min=0))
    isAdmin = fields.String(validate=validate.OneOf(choices=['0', '1']))


class UserToUpdate(Schema):
    firstName = fields.String(validate=validate.Length(min=2))
    lastName = fields.String(validate=validate.Length(min=2))
    email = fields.String(validate=validate.Email())
    password = fields.Function(deserialize=lambda obj: generate_password_hash(obj), load_only=True)
    phone = fields.Function(validate=validate.Regexp('^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[\s0-9]{4,20}$'))


class TransactionData(Schema):
    id = fields.Integer()
    sentByUser = fields.Integer()
    sentToUser = fields.Integer()
    value = fields.Float()
    datePerformed = fields.DateTime()


class CreateTransaction(Schema):
    sentByUser = fields.Integer(required=True, validate=validate.Range(min=1))
    sentToUser = fields.Integer(required=True, validate=validate.Range(min=1))
    value = fields.Float(required=True, validate=validate.Range(min=0))
