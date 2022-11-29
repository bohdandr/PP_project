import base64
import unittest
from unittest.mock import ANY

from flask import url_for, Flask
from flask_bcrypt import generate_password_hash
from flask_testing import TestCase

from total import db_utils
from total.models import User, Session, Transaction, BaseModel, engine
from total.app import app


class BaseTestCase(TestCase):
	def setUp(self):
		self.create_tables()

		self.user1_data = {
			"username": "user1",
			"firstName": "user1",
			"lastName": "user1",
			"email": "user1@gmail.com",
			"password": "user1",
			"phone": "+380961010101",
			"birthDate": "2000-01-01",
			"wallet": 100.0,
			"isAdmin": "1"
		}

		self.user1_data_with_invalid_wallet = {
			"username": "user1",
			"firstName": "user1",
			"lastName": "user1",
			"email": "user1@gmail.com",
			"password": "user1",
			"phone": "+380961010101",
			"birthDate": "2000-01-01",
			"wallet": 0.0,
			"isAdmin": "1"
		}

		self.user1_data_hashed = {
			**self.user1_data,
			"password": generate_password_hash(self.user1_data["password"]).decode("utf-8"),
		}

		self.user1_data_with_invalid_wallet_hashed = {
			**self.user1_data_with_invalid_wallet,
			"password": generate_password_hash(self.user1_data_with_invalid_wallet["password"]).decode("utf-8"),
		}

		self.user1_credentials = {
			"username": self.user1_data["username"],
			"password": self.user1_data["password"],
		}

		self.user2_data = {
			"username": "user2",
			"firstName": "user2",
			"lastName": "user2",
			"email": "user2@gmail.com",
			"password": "user2",
			"phone": "+380672730422",
			"birthDate": "2000-01-01",
			"wallet": 125.0,
			"isAdmin": "0"
		}

		self.update_user_valid = {
			"firstName": "firstname",
			"lastName": "lastname",
			"email": "email@gmail.com",
			"password": "password",
			"phone": "+380999999999",
		}

		self.update_user_invalid_firstname = {
			"firstName": "3",
		}

		self.update_user_valid_hashed = {
			**self.update_user_valid,
			"password": generate_password_hash(self.update_user_valid["password"]).decode("utf-8"),
		}

		self.user2_data_hashed = {
			**self.user2_data,
			"password": generate_password_hash(self.user2_data["password"]).decode("utf-8"),
		}

		self.user2_credentials = {
			"username": self.user2_data["username"],
			"password": self.user2_data["password"],
		}

		self.transaction1_data = {
			"sentByUser": 1,
			"sentToUser": 2,
			"value": 50
		}

		self.transaction2_data = {
			"sentByUser": 1,
			"sentToUser": 2,
			"value": 100
		}

	def tearDown(self):
		self.close_session()

	def create_tables(self):
		BaseModel.metadata.drop_all(engine)
		BaseModel.metadata.create_all(engine)

	def close_session(self):
		Session.close()

	def create_app(self):
		return app

	def get_auth_basic(self, credentials):
		to_token = credentials["username"] + ':' + credentials["password"]

		valid_credentials = base64.b64encode(to_token.encode()).decode("utf-8")

		return {'Authorization': 'Basic ' + str(valid_credentials)}


class TestCreateUser(BaseTestCase):
	def test_create_user(self):
		resp = self.client.post(
			url_for("api.create_user"),
			json=self.user2_data
		)
		self.assertEqual(resp.status_code, 200)

		self.assertEqual(resp.json, {
			"id": 1,
			"username": self.user2_data["username"],
			"firstName": self.user2_data["firstName"],
			"lastName": self.user2_data["lastName"],
			"email": self.user2_data["email"],
			"password": ANY,
			"phone": self.user2_data["phone"],
			"birthDate": self.user2_data["birthDate"],
			"wallet": self.user2_data["wallet"],
			"isAdmin": self.user2_data["isAdmin"],
			"userStatus": "1",
			"code": 200,
		})
		self.assertTrue(
			Session.query(User).filter_by(username=self.user2_data["username"]).one()
		)


class TestUserSelf(BaseTestCase):
	def test_user_self_get(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		resp = self.client.get(
			url_for("api.user_self"),
			headers=self.get_auth_basic(self.user1_credentials)
		)
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp.json, {
			"id": 1,
			"username": self.user1_data["username"],
			"firstName": self.user1_data["firstName"],
			"lastName": self.user1_data["lastName"],
			"email": self.user1_data["email"],
			"password": self.user1_data_hashed["password"],
			"phone": self.user1_data["phone"],
			"birthDate": self.user1_data["birthDate"],
			"wallet": self.user1_data["wallet"],
			"isAdmin": self.user1_data["isAdmin"],
			"userStatus": "1",
			"code": 200,
		})

	def test_user_self_update(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		resp = self.client.put(
			url_for("api.user_self"),
			headers=self.get_auth_basic(self.user1_credentials),
			json=self.update_user_valid
		)

		self.assertEqual(resp.status_code, 200)

		self.assertEqual(resp.json, {
			"id": 1,
			"username": self.user1_data["username"],
			"firstName": self.update_user_valid["firstName"],
			"lastName": self.update_user_valid["lastName"],
			"email": self.update_user_valid["email"],
			"phone": self.update_user_valid["phone"],
			"birthDate": self.user1_data["birthDate"],
			"isAdmin": self.user1_data["isAdmin"],
			"userStatus": "1",
			"code": 200,
		})

	def test_user_self_delete(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		resp = self.client.delete(
			url_for("api.user_self"),
			headers=self.get_auth_basic(self.user1_credentials),
		)

		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp.json, {
			"id": 1,
			"username": "0",
			"firstName": self.user1_data["firstName"],
			"lastName": self.user1_data["lastName"],
			"email": self.user1_data["email"],
			"phone": self.user1_data["phone"],
			"password": self.user1_data_hashed["password"],
			"birthDate": self.user1_data["birthDate"],
			"wallet": self.user1_data["wallet"],
			"isAdmin": self.user1_data["isAdmin"],
			"userStatus": "0",
			"code": 200,
		})

	def test_user_self_put_wrong_firstName(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		resp = self.client.put(
			url_for("api.user_self"),
			headers=self.get_auth_basic(self.user1_credentials),
			json=self.update_user_invalid_firstname
		)
		self.assertEqual(resp.status_code, 400)
		self.assertEqual(resp.json, {
			"code": 400,
			"error": "{'firstName': ['Shorter than minimum length 2.']}"
		})

	def test_verify_invalid_password(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		resp = self.client.get(
			url_for("api.user_self"),
			headers=self.get_auth_basic({"username": self.user1_credentials["username"],
										 "password": "invalid_password"})
		)
		self.assertEqual(resp.status_code, 401)
		self.assertEqual(str(resp), "<WrapperTestResponse streamed [401 UNAUTHORIZED]>")

	def test_unauth_not_existing_username(self):
		resp = self.client.get(url_for("api.user_self"))
		self.assertEqual(resp.status_code, 404)
		self.assertEqual(resp.json, {'code': 404, 'error': 'Not found'})





class TestGetUserById(BaseTestCase):
	def test_get_user_by_id(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		resp = self.client.get(
			url_for("api.get_user_by_id", user_id=1),
			headers=self.get_auth_basic(self.user1_credentials)
		)
		self.assertEqual(resp.status_code, 200)

		self.assertEqual(resp.json, {
			"id": 1,
			"username": self.user1_data["username"],
			"firstName": self.user1_data["firstName"],
			"lastName": self.user1_data["lastName"],
			"email": self.user1_data["email"],
			"phone": self.user1_data["phone"],
			"birthDate": self.user1_data["birthDate"],
			"isAdmin": self.user1_data["isAdmin"],
			"userStatus": ANY,
			"code": 200,
		})

	def test_get_user_by_id_not_admin(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		db_utils.create_entry(User, **self.user2_data_hashed)
		resp = self.client.get(
			url_for("api.get_user_by_id", user_id=1),
			headers=self.get_auth_basic(self.user2_credentials)
		)
		self.assertEqual(resp.status_code, 401)

		self.assertEqual(resp.json, {
			"error": ANY,
			"code": 401
		})


class TestDeleteUserById(BaseTestCase):
	def test_delete_user_by_id(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		resp = self.client.delete(
			url_for("api.delete_user_by_id", user_id=1),
			headers=self.get_auth_basic(self.user1_credentials),
		)
		self.assertEqual(resp.status_code, 200)

		self.assertEqual(resp.json, {
			"id": 1,
			"username": "0",
			"firstName": self.user1_data["firstName"],
			"lastName": self.user1_data["lastName"],
			"email": self.user1_data["email"],
			"phone": self.user1_data["phone"],
			"birthDate": self.user1_data["birthDate"],
			"password": ANY,
			'wallet': 100.0,
			"isAdmin": self.user1_data["isAdmin"],
			"userStatus": "0",
			"code": 200,
		})


class TestUserWalletAction(BaseTestCase):
	def test_user_replenish(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		resp = self.client.put(
			url_for("api.user_replenish"),
			json={"value": 100.0},
			headers=self.get_auth_basic(self.user1_credentials),
		)

		self.assertEqual(resp.status_code, 200)

		self.assertEqual(resp.json, {
			"id": 1,
			"username": self.user1_data["username"],
			"firstName": self.user1_data["firstName"],
			"lastName": self.user1_data["lastName"],
			"email": self.user1_data["email"],
			"phone": self.user1_data["phone"],
			"birthDate": self.user1_data["birthDate"],
			"password": ANY,
			"wallet": 200,
			"isAdmin": self.user1_data["isAdmin"],
			"userStatus": "1",
			"code": 200,
		})

	def test_user_withdraw(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		resp = self.client.put(
			url_for("api.user_withdraw"),
			json={"value": 100.0},
			headers=self.get_auth_basic(self.user1_credentials),
		)

		self.assertEqual(resp.status_code, 200)

		self.assertEqual(resp.json, {
			"id": 1,
			"username": self.user1_data["username"],
			"firstName": self.user1_data["firstName"],
			"lastName": self.user1_data["lastName"],
			"email": self.user1_data["email"],
			"phone": self.user1_data["phone"],
			"birthDate": self.user1_data["birthDate"],
			"password": ANY,
			"wallet": 0,
			"isAdmin": self.user1_data["isAdmin"],
			"userStatus": "1",
			"code": 200,
		})

	def test_not_enough_money_to_withdraw(self):
		db_utils.create_entry(User, **self.user1_data_with_invalid_wallet_hashed)
		resp = self.client.put(
			url_for("api.user_withdraw"),
			json={"value": 100.0},
			headers=self.get_auth_basic(self.user1_credentials),
		)
		self.assertEqual(resp.status_code, 402)
		self.assertEqual(resp.json, {'code': 402, 'error': 'user has not enough money to withdraw'})



class TestCreateTransaction(BaseTestCase):
	def test_create_transaction(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		db_utils.create_entry(User, **self.user2_data_hashed)
		db_utils.create_entry(Transaction, **self.transaction1_data)
		resp = self.client.post(
			url_for("api.create_transaction", usernameto="user2"),
			json={"value": 20.0},
			headers=self.get_auth_basic(self.user1_credentials),
		)

		self.assertEqual(resp.status_code, 200)

		self.assertEqual(resp.json, {
			'datePerformed': ANY,
			'id': ANY,
			'sentByUser': 1,
			'sentToUser': 2,
			'value': 20.0
		})


class TestTransactionAction(BaseTestCase):
	def test_sent_transaction(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		db_utils.create_entry(User, **self.user2_data_hashed)
		db_utils.create_entry(Transaction, **self.transaction1_data)
		db_utils.create_entry(Transaction, **self.transaction2_data)

		resp = self.client.get(
			url_for("api.sent_transaction"),
			headers=self.get_auth_basic(self.user1_credentials),
		)

		self.assertEqual(resp.status_code, 200)

		self.assertEqual(resp.json, [
			{
				'datePerformed': ANY,
				'id': ANY,
				'sentByUser': 1,
				'sentToUser': 2,
				'value': 50.0
			},
			{
				'datePerformed': ANY,
				'id': ANY,
				'sentByUser': 1,
				'sentToUser': 2,
				'value': 100.0
			},
			{
				"code": 200
			}

		]
						 )

	def test_recieved_transaction(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		db_utils.create_entry(User, **self.user2_data_hashed)
		db_utils.create_entry(Transaction, **self.transaction1_data)
		db_utils.create_entry(Transaction, **self.transaction2_data)

		resp = self.client.get(
			url_for("api.recieved_transaction"),
			headers=self.get_auth_basic(self.user1_credentials),
		)

		self.assertEqual(resp.status_code, 200)

		self.assertEqual(resp.json, [
			{

				"code": 200
			}
		]
						 )

	def test_sent_transaction_by_username(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		db_utils.create_entry(User, **self.user2_data_hashed)
		db_utils.create_entry(Transaction, **self.transaction1_data)
		db_utils.create_entry(Transaction, **self.transaction2_data)

		resp = self.client.get(
			url_for("api.sent_transaction_username", username="user1"),
			headers=self.get_auth_basic(self.user1_credentials),
		)

		self.assertEqual(resp.status_code, 200)

		self.assertEqual(resp.json, [
			{
				'datePerformed': ANY,
				'id': ANY,
				'sentByUser': 1,
				'sentToUser': 2,
				'value': 50.0
			},
			{
				'datePerformed': ANY,
				'id': ANY,
				'sentByUser': 1,
				'sentToUser': 2,
				'value': 100.0
			},
			{
				"code": 200
			}

		]
						 )

	def test_recieved_transaction_by_username(self):
		db_utils.create_entry(User, **self.user1_data_hashed)
		db_utils.create_entry(User, **self.user2_data_hashed)
		db_utils.create_entry(Transaction, **self.transaction1_data)
		db_utils.create_entry(Transaction, **self.transaction2_data)

		resp = self.client.get(
			url_for("api.recieved_transaction_username", username="user1"),
			headers=self.get_auth_basic(self.user1_credentials),
		)

		self.assertEqual(resp.status_code, 200)

		self.assertEqual(resp.json, [
			{

				"code": 200
			}
		]
						 )



if __name__ == "__main__":
	unittest.main()


# coverage run --source ./total -m unittest discover lab9
# coverage report -m