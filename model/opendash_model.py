# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UnicodeText, Date, create_engine, Column
from sqlalchemy import Integer, ForeignKey, Table, String
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'
	
	id = Column(Integer, primary_key=True)
	user = Column(String, nullable=False)
	password = Column(String, nullable=False)
	
	def __init__(self, user=None, password=None):
		self.user = user
		self.password = password

	# Flask-Login integration
	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def check_password(self, password):
		return self.password == password

class Endpoint(Base):
	__tablename__ = 'endpoint'
	
	id = Column(Integer, primary_key=True)
	url = Column(UnicodeText, nullable=False)
	
	def __init__(self, url=None):
		self.url = url

if __name__ == '__main__':
	USER = 'opendash'
	PASS = 'opendash'
	
	DB_NAME = 'teseo'
	
	#engine = create_engine('mysql://%s:%s@localhost/%s?charset=utf8' % (USER, PASS, DB_NAME))
	engine = create_engine('sqlite:///opendash.db')
	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)