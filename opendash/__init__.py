# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect
from flask.ext.admin import Admin

from flask.ext.login import LoginManager, current_user

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from admin.model_view import UserView, EndpointView, LogoutView
from admin.model_view import ReportView, ChartView, PrefixView
from form.login import LoginForm

from opendash.model.opendash_model import User

app = Flask(__name__)

engine = create_engine('sqlite:///opendash.db')
Session = sessionmaker(bind=engine)
session = Session()

app.config['SECRET_KEY'] = '123456790'

login_manager = LoginManager()
login_manager.setup_app(app)

admin = Admin(app, name='OpenDASH')
admin.add_view(UserView(session))
admin.add_view(EndpointView(session))
admin.add_view(ReportView(session))
admin.add_view(ChartView(session))
admin.add_view(PrefixView(session))
admin.add_view(LogoutView(name='Log out'))

# Create user loader function
@login_manager.user_loader
def load_user(user_id):
	user = session.query(User).get(user_id)
	return user

@app.route("/")
def index():
	form = LoginForm(session)

	if current_user.is_authenticated() and current_user.is_admin():
		return redirect('/admin')
	return render_template('index.html', form=form, user=current_user)