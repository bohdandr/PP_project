from marshmallow import ValidationError

from lab6.check_models import Session
from sqlalchemy.sql import exists
from lab6.models import Session, User, Transaction


def is_name_taken(model_class, name):
	session = Session()
	if model_class == User:
		return session.query(exists().where(model_class.username == name)).scalar()

def id_exists(model_class, uid):
	session = Session()
	return session.query(exists().where(model_class.id == uid)).scalar()


def create_entry(model_class, *, commit=True, **kwargs):
	session = Session()
	entry = model_class(**kwargs)
	session.add(entry)
	if commit:
		session.commit()
	return entry


def get_entry_by_uid(model_class, id, **kwargs):
	session = Session()
	return session.query(model_class).filter_by(id=id, **kwargs).one()


def get_entry_by_username(model_class, username, **kwargs):
	session = Session()
	return session.query(model_class).filter_by(username=username, **kwargs).one()


def update_entry(entry, *, commit=True, **kwargs):
	session = Session()
	for key, value in kwargs.items():
		setattr(entry, key, value)
	if commit:
		session.commit()
	return entry


def delete_entry(model_class, id, *, commit=True, **kwargs):
	session = Session()
	session.query(model_class).filter_by(id=id, **kwargs).delete()
	if commit:
		session.commit()


def get_value_withdraw(entry, val, *, commit=True, **kwargs):
	session = Session()

	setattr(entry, "value", val)

	if commit:
		session.commit()
	return entry


def get_wallet_by_uid(model_class, uid, **kwargs):
	session = Session()
	return session.query(model_class).filter_by(id=id, **kwargs).one()


def update_wallet(entry, val, *, commit=True, **kwargs):
	session = Session()
	for key, value in kwargs.items():
		if key == "wallet":
			value += val
		setattr(entry, key, value)
	if commit:
		session.commit()
	return entry


def find_transactions_by_userid(sentuserid):
	session = Session()
	return session.query(Transaction).filter_by(sentByUser=sentuserid).all()

def find_transactions_to_userid(recieveduserid):
	session = Session()
	return session.query(Transaction).filter_by(sentToUser=recieveduserid).all()


