import os
import sys
import ldap3
import mimetypes
from flask import (request,render_template,flash, redirect, url_for, Blueprint,abort,jsonify,send_file,session,g)
from flask_login import (current_user,login_user,logout_user,login_required)
from apps import app
from apps import login_manager
from apps.auth import User,LoginForm
from apps.fetch_url import fetchProjects
from apps.projects import getProjectsList
from apps.utils import write_file, dir_tree, get_file_extension
from apps.git_actions import deleteProject,pullProject,pushProject


FLASKCODE_APP_TITLE = 'Workflow Submission Application'
FLASKCODE_EDITOR_THEME = 'vs-dark'
FLASKCODE_RESOURCE_BASEPATH = None

auth = Blueprint('auth', __name__)

@auth.context_processor
def process_template_context():
    return dict(
        app_title=FLASKCODE_APP_TITLE,
        editor_theme=FLASKCODE_EDITOR_THEME
    )

@login_manager.user_loader

def load_user(id):
    return User

@auth.before_request
def get_current_user():
    g.user = current_user

@auth.route('/')
def main_index():
    if current_user.is_authenticated:
        return redirect('/home')

    else:
        return redirect('/login')


@auth.route('/login')
@auth.route('/authenticate', methods = ['POST'])

def login():
    if request.method == 'POST':
        form = LoginForm(request.form)
        username = request.form['username']
        password = request.form['password']

        try:
            User.try_login(username,password)
        except:
            flash(
                'Invalid username or password. Please try again.',
                'danger')
            return redirect('/login')

        user = User(username = username, password = password)
        login_user(user)
        session['Username'] = username
        current_user.username = username 
        return redirect('/home')

    else:
        form = LoginForm(request.form)
        return render_template('home/login.html', form=form) 


@auth.route('/home')
@login_required
def home():
    user = session['Username']
    if os.path.exists('/home/' + user + '/workflow_app_projects'):
        projects = getProjectsList('/home/' + user + '/workflow_app_projects')
    else:
        projects = []
    return render_template('home/index.html', projects=projects)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@auth.route('/fetch', methods = ['GET','POST'])
@login_required
def fetch_url():
    user=session['Username']
    username = request.form['username']
    password = request.form['password']
    url = request.form['url']

    output = fetchProjects(user, username, password, url)

    if output == 0:
        flash('Project has been fetched successfully', 'success')
    elif output == 1:
        flash('Invalid username or password. Please try again.', 'danger')
    elif output == 2:
        flash('Project url is incorrect. Please try again.', 'danger')
    elif output == 3:
        flash('Project already exits. Existing projects cannot be fetched again.', 'danger')
    elif output == 4:
        flash('Unexpected error. Please try again.', 'danger')

    return redirect('/home')


@auth.route('/delete', methods = ['GET','POST'])
@login_required
def delete_project():

    if request.method == 'POST':
        project = request.form['action']
        output = deleteProject(session['Username'], project) 
        if output == 0:
            flash('Project has been deleted successfully', 'success')    
        else:
            flash('An error occured while deleting project', 'danger') 

    return redirect('/home')

@auth.route('/pull', methods = ['GET','POST'])
@login_required
def pull_project():

    if request.method == 'POST':
        project = request.form['action']
        output = pullProject(session['Username'], project)
        if output == 0:
            flash('Project has been pulled successfully', 'success')
        else:
            flash('An error occured while pulling project', 'danger')

    return redirect('/home')

    
@auth.route('/push', methods = ['GET','POST'])
@login_required
def push_project():

    if request.method == 'POST':
        project = request.form['action']
        output = pushProject(session['Username'], project)
        if output == 0:
            flash('Project has been pushed successfully', 'success')
        else:
            flash('An error occured while pushing project', 'danger')

    return redirect('/home')


def get_segment( request ):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None


@auth.route('/files', methods = ['GET','POST'])
@login_required
def index():
    user = session['Username']

    if request.method == 'POST':
        session['project'] = request.form['action']
    
    resource_basepath = '/home/' + user + '/workflow_app_projects/' + session['project'] 
    if not (resource_basepath and os.path.isdir(resource_basepath)):
        abort(500, '`FLASKCODE_RESOURCE_BASEPATH` is not a valid directory path')
    else:
        g.flaskcode_resource_basepath = os.path.abspath(resource_basepath).rstrip('/\\')

    dirname = os.path.basename(g.flaskcode_resource_basepath)
    dtree = dir_tree(g.flaskcode_resource_basepath, g.flaskcode_resource_basepath + '/')
    return render_template('flaskcode/index.html', dirname=dirname, dtree=dtree)


@auth.route('/resource-data/<path:file_path>.txt', methods=['GET', 'HEAD'])
@login_required
def resource_data(file_path):
    user = session['Username']
    resource_basepath = '/home/' + user + '/workflow_app_projects/' + session['project'] 
    if not (resource_basepath and os.path.isdir(resource_basepath)):
        abort(500, '`FLASKCODE_RESOURCE_BASEPATH` is not a valid directory path')
    else:
        g.flaskcode_resource_basepath = os.path.abspath(resource_basepath).rstrip('/\\')

    file_path = os.path.join(g.flaskcode_resource_basepath, file_path)
    if not (os.path.exists(file_path) and os.path.isfile(file_path)):
        abort(404)
    response = send_file(file_path, mimetype='text/plain', cache_timeout=0)
    mimetype, encoding = mimetypes.guess_type(file_path, False)
    if mimetype:
        response.headers.set('X-File-Mimetype', mimetype)
        extension = mimetypes.guess_extension(mimetype, False) or get_file_extension(file_path)
        if extension:
            response.headers.set('X-File-Extension', extension.lower().lstrip('.'))
    if encoding:
        response.headers.set('X-File-Encoding', encoding)
    return response


@auth.route('/update-resource-data/<path:file_path>', methods=['POST'])
@login_required
def update_resource_data(file_path):
    user = session['Username']
    resource_basepath = '/home/' + user + '/workflow_app_projects/' + session['project'] 
    if not (resource_basepath and os.path.isdir(resource_basepath)):
        abort(500, '`FLASKCODE_RESOURCE_BASEPATH` is not a valid directory path')
    else:
        g.flaskcode_resource_basepath = os.path.abspath(resource_basepath).rstrip('/\\')

    file_path = os.path.join(g.flaskcode_resource_basepath, file_path)
    is_new_resource = bool(int(request.form.get('is_new_resource', 0)))
    if not is_new_resource and not (os.path.exists(file_path) and os.path.isfile(file_path)):
        abort(404)
    success = True
    message = 'File saved successfully'
    resource_data = request.form.get('resource_data', None)
    if resource_data:
        success, message = write_file(resource_data, file_path)
    else:
        success = False
        message = 'File data not uploaded'
    return jsonify({'success': success, 'message': message})

