from lab6.models import Session, User, Transaction
from flask_bcrypt import generate_password_hash

session = Session()

user1 = User(username="admin", firstName="admin", lastName="admin", email="admin@gmail.com",
             password=generate_password_hash("beb123beb"), phone="+380963651527",
             birthDate="2000-01-01", wallet=0, isAdmin='1')

session.add(user1)
session.commit()