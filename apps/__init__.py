# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

# import Flask 
from flask import Flask
from flask_login import LoginManager
from .config import Config
from flask import Blueprint, current_app, g, abort

# Inject Flask magic
app = Flask(__name__)
app.config['WTF_CSRF_SECRET_KEY'] = 'random key for form'
app.config['LDAP_PROVIDER_URL'] = 'ldap://mgmt.cluster.local:389/'
app.config['LDAP_PROTOCOL_VERSION'] = 3

app.secret_key = 'randon_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

ctx = app.test_request_context()
ctx.push()


# load Configuration
app.config.from_object( Config ) 

# Import routing to render the pages
from apps import views

from apps.views import auth
app.register_blueprint(auth)

