# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, String, Unicode, UnicodeText, Boolean, DateTime

from sqlalchemy.orm import sessionmaker, relationship

import uuid
import datetime

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
	created = Column(DateTime, nullable=False)
	modified = Column(DateTime, nullable=False)

	user = Column(Integer, ForeignKey('user.id'))

	charts = relationship('Chart')

	def __init__(self, name=None, public=False):
		self.id = str(uuid.uuid1())
		self.name = name
		self.public = public
		self.created = datetime.datetime.now()
		self.modified = self.created

class Chart(Base):
	__tablename__ = 'chart'

	id = Column(Integer, primary_key=True)
	name = Column(Unicode, nullable=False)
	json = Column(UnicodeText, nullable=False)

	report = Column(String, ForeignKey('report.id'))

	def __init__(self, name=None, json=None):
		self.name = name
		self.json = json

class Prefix(Base):
	__tablename__ = 'prefix'

	prefix = Column(String, primary_key=True)
	uri = Column(String, nullable=False)

	def __init__(self, uri, prefix = None):
		self.uri = uri
		self.prefix = prefix

		if self.prefix is None:
			self.prefix = self._get_short_prefix(self.uri)

	def _get_short_prefix(self, uri):
		prefix = ''
		for e in uri.split('/'):
			if len(e) > 0:
				prefix += e[0]

		return prefix + str(uuid.uuid4())[:5]

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

#	session.add(Endpoint('http://helheim.deusto.es/sparql'))
	session.add(Endpoint('http://localhost:3030/ds1/query'))
	session.add(Endpoint('http://localhost:3030/ds2/query'))

	session.commit()