import ldap
from flask_wtf import Form
from wtforms import StringField,PasswordField
from wtforms import validators
from apps import app


def get_ldap_connection():
    conn = ldap.initialize(app.config['LDAP_PROVIDER_URL'])
    return conn

class User():
    username = ''

    def __init__(self, username, password):
        self.username = username

    @staticmethod

    def try_login(username, password):
        conn = get_ldap_connection()
        conn.simple_bind_s(
            'uid=%s,cn=users,cn=accounts,dc=cluster,dc=local' %username , password
        )

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def set_username(self,username):
        self.username = username
    

class LoginForm(Form):
    username = StringField('Username',[validators.DataRequired()])
    password = PasswordField('Password',[validators.DataRequired()])    

