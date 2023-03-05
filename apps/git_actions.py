import os
import pwd
import datetime
from subprocess import Popen, PIPE

def deleteProject(user,project):
    project_path = f"/home/{user}/workflow_app_projects/{project}"
    try:
        process = Popen(f"rm -rf {project_path} ", shell=True, stdout=PIPE, stderr=PIPE)
        output, error = process.communicate()
        rc = process.returncode
        print(error)
        return 0
    except:
        return 1


def pullProject(user,project):

    project_path = f"/home/{user}/workflow_app_projects/{project}"
    try:
        process = Popen(f"sudo -iu {user} sh -c 'cd {project_path} && git pull'", shell=True, stdout=PIPE, stderr=PIPE)
        output, error = process.communicate()
        rc = process.returncode
        os.system(f"chown -R {user}:{user} {project_path}")
        return 0
    except:
        return 1


def pushProject(user,project):

    project_path = f"/home/{user}/workflow_app_projects/{project}"
    branch = f"{user}-{project}"
    now = datetime.datetime.now()
    time = now.strftime("%d-%b-%Y-%H:%M:%S")
    print(time)

    branch_process = Popen(f"sudo -iu {user} sh -c 'cd {project_path} && git checkout {branch}'", shell=True, stdout=PIPE, stderr=PIPE)
    branch_process.wait()

    if branch_process.returncode != 0:
        print("New Branch")
        branch_process = Popen(f"sudo -iu {user} sh -c 'cd {project_path} && git checkout -b {branch}'", shell=True, stdout=PIPE, stderr=PIPE)
        branch_process.wait()

    add_process = Popen(f"sudo -iu {user} sh -c 'cd {project_path} && git add .'", shell=True, stdout=PIPE, stderr=PIPE)
    add_process.wait()

    commit_message = f'{time} - User {user} - submit {project} job'

    commit_process = Popen(f"sudo -iu {user} sh -c `cd {project_path} && git commit -m '{commit_message}'`", shell=True, stdout=PIPE, stderr=PIPE)
    commit_process.wait()
    if commit_process.returncode != 0:
        commit_process = Popen(f"sudo -iu {user} sh -c `cd {project_path} && git commit --amend --no-edit -m '{commit_message}'`", 
                               shell=True, stdout=PIPE, stderr=PIPE)
        commit_process.wait()
    output, error = commit_process.communicate()
   
    process = Popen(f"sudo -iu {user} sh -c 'cd {project_path} && git push origin {branch} --force'", shell=True, stdout=PIPE, stderr=PIPE)
    output, error = process.communicate()
    rc = process.returncode
    print(error)
    os.system(f"chown -R {user}:{user} {project_path}")
    return 0
