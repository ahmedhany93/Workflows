import os
import pwd
from git import Repo
from subprocess import Popen, PIPE

def getProjectsList(path):
    apps_list = []
    for dir in os.listdir(path):
        if not os.path.isfile(os.path.join(path, dir)):
            if os.path.exists(f"{path}/{dir}/.git/config"):
                process = Popen(f"cat {path}/{dir}/.git/config | grep url | sed 's/.*url = //g'", shell=True, stdout=PIPE, stderr=PIPE)
                out,err = process.communicate()
                url = out.decode("utf-8").replace('\n','')
                apps_list.append([dir,url])
    return apps_list
