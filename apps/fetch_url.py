import os
import pwd
from subprocess import Popen, PIPE

def fetchProjects(user, username, password, url):
    password = password.replace('@','%40')
    if 'https' in url:
        protocol = 'https://'
    else:
        protocol = 'http://'
    git_url = f"{protocol}{username}:{password}@{url.replace(protocol,'')}"
    clean_url = git_url.replace(f"{username}:{password}@", "" )
    clean_url_command = f"git remote set-url origin {clean_url}"
    repo_name = os.path.splitext(os.path.basename(git_url))[0]
    repo_dir = f"/home/{user}/workflow_app_projects/{repo_name}"
    store_creds = 'git config --local credential.helper store'
    set_uname = f"git config --local user.name '{username}' && git config --local user.email '{user}@cluster.local'"
    process = Popen(f"sudo -iu {user} git clone {git_url} {repo_dir} && cd {repo_dir} && {clean_url_command} && {store_creds} && {set_uname}", 
                        shell=True, stdout=PIPE, stderr=PIPE)
    output, error = process.communicate()
    rc = process.returncode
    print(output)
    print(error)

    if 'Authentication failed' in error.decode("utf-8")  and 'Access denied' in error.decode("utf-8") and rc != 0:
        return 1
    elif 'fatal: repository' in error.decode("utf-8") and 'not found' in error.decode("utf-8") and rc != 0:
        return 2
    elif rc == 0:
        return 0
    elif 'fatal: destination path' in error.decode("utf-8") and 'already exists' in error.decode("utf-8") and rc != 0:
        return 3
    else:
        print(error.decode("utf-8"))
        print("Error Here")
        return 4


