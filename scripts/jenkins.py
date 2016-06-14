import json
import os.path
import requests
from StringIO import StringIO

import jenkinsapi
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.requester import Requester
from PIL import Image


JENKINS_URL = "https://jenkins.indigo-datacloud.eu:8080/"

requests.packages.urllib3.disable_warnings()


def get_last_buildno(job_name):
    #j = Jenkins(JENKINS_URL, requester=Requester(username, password, baseurl=JENKINS_URL, ssl_verify=False))
    j = Jenkins(JENKINS_URL, ssl_verify=False)
    try:
        return j.get_job(job_name).get_last_good_build().buildno
    except jenkinsapi.custom_exceptions.NoBuildData:
        return j.get_job(job_name).get_last_build().buildno
    except jenkinsapi.custom_exceptions.UnknownJob:
        raise


def get_last_job_url(job_name):
    try:
        buildno = get_last_buildno(job_name)
    except jenkinsapi.custom_exceptions.UnknownJob:
        return None
    return '/'.join([JENKINS_URL, "job/%s/%s" % (job_name, buildno)])


def save_cobertura_graph(job_name, dest_dir):
    try:
        last_build = get_last_buildno(job_name)
    except jenkinsapi.custom_exceptions.UnknownJob:
        return None

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    url = '/'.join([JENKINS_URL, "job/%s/%s/cobertura/graph" % (job_name, last_build)])
    r = requests.get(url, verify=False)
    if r.status_code == 500:
        return None
    fname = os.path.join(dest_dir, "graph_%s.png" % job_name)
    i = Image.open(StringIO(r.content))
    i.save(fname)
    return os.path.abspath(fname)


def get_cobertura_data(job_name):
    try:
        last_build = get_last_buildno(job_name)
    except jenkinsapi.custom_exceptions.UnknownJob:
        return {}
    url = '/'.join([JENKINS_URL, "job/%s/%s/cobertura/api/json?depth=2" % (job_name, last_build)])
    r = requests.get(url, verify=False)
    return json.loads(r.content)["results"]["elements"]

