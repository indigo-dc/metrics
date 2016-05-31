import json
import os.path
import requests
from StringIO import StringIO

from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.requester import Requester
from PIL import Image


JENKINS_URL = "https://jenkins.indigo-datacloud.eu:8080/"

requests.packages.urllib3.disable_warnings()


def get_last_buildno(job_name):
    #j = Jenkins(JENKINS_URL, requester=Requester(username, password, baseurl=JENKINS_URL, ssl_verify=False))
    j = Jenkins(JENKINS_URL, ssl_verify=False)
    return j.get_job(job_name).get_last_good_build().buildno


def save_cobertura_graph(job_name, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    last_build = get_last_buildno(job_name)
    url = '/'.join([JENKINS_URL, "job/%s/%s/cobertura/graph" % (job_name, last_build)])
    r = requests.get(url, verify=False)
    fname = os.path.join(dest_dir, "graph_%s.png" % job_name)
    i = Image.open(StringIO(r.content))
    i.save(fname)
    return fname


def get_cobertura_data(job_name):
    last_build = get_last_buildno(job_name)
    url = '/'.join([JENKINS_URL, "job/%s/%s/cobertura/api/json?depth=2" % (job_name, last_build)])
    r = requests.get(url, verify=False)
    return json.loads(r.content)["results"]["elements"]

