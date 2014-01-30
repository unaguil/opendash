# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, String, Unicode, UnicodeText, Boolean

from sqlalchemy.orm import sessionmaker, relationship

import uuid

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'
	
	id = Column(Integer, primary_key=True)
	user = Column(String, nullable=False)
	password = Column(String, nullable=False)

	reports = relationship('Report')
	
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

	def is_admin(self):
		return self.user == 'admin'

class Endpoint(Base):
	__tablename__ = 'endpoint'
	
	id = Column(Integer, primary_key=True)
	url = Column(UnicodeText, nullable=False)

	def __init__(self, url=None):
		self.url = url

class Report(Base):
	__tablename__ = 'report'

	id = Column(String, primary_key=True)
	name = Column(Unicode, nullable=False)
	public = Column(Boolean, nullable=False)

	user = Column(Integer, ForeignKey('user.id'))

	def __init__(self, name=None, public=False):
		self.id = str(uuid.uuid1())
		self.name = name
		self.public = public

class Chart(Base):
	__tablename__ = 'chart'

	id = Column(String, primary_key=True)
	json = Column(UnicodeText, nullable=False)

	report = Column(Integer, ForeignKey('report.id'))

	def __init__(self, json=None):
		self.json = json

if __name__ == '__main__':
	engine = create_engine('sqlite:///opendash.db')
	
	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)

	Session = sessionmaker(bind=engine)
	session = Session()

	session.add(User(user='admin', password='admin'))

	user = User(user='test', password='test')
	user.reports.append(Report('report1', False))
	user.reports.append(Report('report2', True))

	session.add(user)

	session.add(Endpoint('http://helheim.deusto.es/sparql'))
	session.add(Endpoint('http://localhost:3030/ds/query'))

	session.commit()