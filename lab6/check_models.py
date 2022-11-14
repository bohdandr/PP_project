from models import Session, User, Transaction

session = Session()

user1 = User(username="stepans", firstName="Stepan", lastName="Sarabun", email="stepankolv12@gmail.com",
             password=b"beb123", phone="+380963651527", birthDate="2004-02-27", wallet=8)
user2 = User(username="stepans", firstName="Stepan", lastName="Sarabun", email="stepankolv12@gmail.com",
             password=b"beb456", phone="+380963651527", birthDate="2004-02-27", wallet=8)

transaction1 = Transaction(fromUser=user1, toUser=user2, value=4)
transaction2 = Transaction(fromUser=user2, toUser=user1, value=3)
transaction3 = Transaction(fromUser=user2, toUser=user1, value=2)
transaction4 = Transaction(fromUser=user1, toUser=user2, value=5)

# session.add(user1)
# session.add(user2)
# session.add(transaction1)
# session.add(transaction2)
# session.add(transaction3)
# session.add(transaction4)

session.commit()
