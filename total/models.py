from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Enum, DateTime
import datetime

DB_URL = "mysql://root:$ygnivkA12@localhost:3306/ap"

engine = create_engine(DB_URL)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(30))
    firstName = Column(String(30))
    lastName = Column(String(30))
    email = Column(String(30))
    password = Column(String(255))
    phone = Column(String(30))
    birthDate = Column(Date)
    wallet = Column(Float, default=0)
    userStatus = Column(Enum('0', '1'), default='1')
    isAdmin = Column(Enum('0', '1'), default='0')


class Transaction(BaseModel):
    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True)
    sentByUser = Column(Integer, ForeignKey("user.id"))
    sentToUser = Column(Integer, ForeignKey("user.id"))
    value = Column(Float)
    datePerformed = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    fromUser = relationship(User, foreign_keys=[sentByUser], backref="transactions_from", lazy="joined")
    toUser = relationship(User, foreign_keys=[sentToUser], backref="transactions_to", lazy="joined")
