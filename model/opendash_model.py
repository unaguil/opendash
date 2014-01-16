# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UnicodeText, Date, create_engine, Column
from sqlalchemy import Integer, ForeignKey, Table, String
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'
	
	id = Column(Integer, primary_key=True)
	account = Column(String, nullable=False)
	
	def __init__(self, account=None):
		self.account = account

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