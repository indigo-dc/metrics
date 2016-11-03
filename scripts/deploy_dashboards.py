#!/usr/bin/env python

import argparse
import json
import logging
import os
import os.path
import shutil
import string
import subprocess
import sys
import tempfile
import urllib2


SCRIPT_NAME = os.path.basename(__file__)
CONFIG_TEMPLATE = """# Remove _OFF to activate sections

[generic]
## generic configuration here

# where to send notifications
mail = orviz@ifca.unican.es
project = $name

# data about the databases
db_user = $db_user
db_password = $db_password
db_host = $db_host
db_cvsanaly = INDIGO_${name_underscored}_cvsanaly
db_bicho = INDIGO_${name_underscored}_bicho
#bicho_backend = github
db_sortinghat = INDIGO_${name_underscored}_sortinghat
db_identities = INDIGO_${name_underscored}_sortinghat
db_pullpo = INDIGO_${name_underscored}_pullpo

[cvsanaly]
# This file contains the information needed to execute cvsanaly
extensions = CommitsLOC,FileTypes,Metrics

[bicho]
# This file contains the information needed to execute Bicho
backend = github
backend_token = ${access_token}
debug = True
delay = 1
log_table = False
trackers = https://api.github.com/repos/indigo-dc/${name}/issues

[sortinghat]

[identities]

[pullpo]
owner = indigo-dc
# url = $name
projects = $name
oauth_key = ${access_token}

#[gerrit]
## Information about gerrit
#backend = gerrit
#user = owl
#debug = True
#delay = 1
#trackers = gerrit.wikimedia.org
#projects = "mediawiki/extensions/Cite","mediawiki/extensions/ArticleFeedback"

#[mlstats]
## This file contains the information needed to execute mlstats
#mailing_lists = http://lists.wikimedia.org/pipermail/mediawiki-announce,http://lists.wikimedia.org/pipermail/mediawiki-api-announce
#
##[irc]

[r]
# This file contains information about the R script. The launcher
# basically chdir into the dir and execute the rscript with the
# parameters

## this needs to be pass to generic
# rscript = run-analysis.py
#r_libs = ../r-lib:$R_LIBS
# r_libs = ~/repos/automator/demo/tools/r-lib/:$R_LIBS

# interval of time for the analysis
start_date = 2015-04-01
# end_date = 2013-09-01
reports = repositories,people
#reports = repositories
period = months
# json_dir = /home/luis/repos/automator/demo/json/

#[git-production_OFF]
## Details about the git destination of the JSON
#destination_json = production/browser/data/json/
#
#[db-dump_OFF]
##Data about final dir to dump databases
#destination_db_dump = production/browser/data/db/
#
#[rsync_OFF]
## Destination where the production dir will be sync
#destination = yourmaildomain@activity.devstack.org:/var/www/dash/"""


logger = logging.getLogger(SCRIPT_NAME)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("%s.log" % SCRIPT_NAME)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


parser = argparse.ArgumentParser(description="Deploy indigo-dc VizGrimoire dashboards")
parser.add_argument('repository',
                    metavar="REPOSITORY",
                    type=str,
                    help="GitHub repository name ('indigo_all' for the whole organization).")
parser.add_argument('db_user',
                    metavar="DB_USER",
                    type=str,
                    default="indigo.dc",
                    help="MetricsDB user ID.")
parser.add_argument('db_password',
                    metavar="DB_PASSWORD",
                    type=str,
                    default="",
                    help="MetricsDB user password.")
parser.add_argument('db_host',
                    metavar="DB_HOST",
                    type=str,
                    default="metricsdb",
                    help="MetricsDB host.")
parser.add_argument('access_token',
                    metavar="GITHUB_OAUTH_TOKEN",
                    type=str,
                    help="GitHub OAuth access token.")
parser.add_argument('--organization-url',
                    metavar="URL",
                    type=str,
                    default="https://github.com/indigo-dc",
                    help="INDIGO-DataCloud organization URL.")
parser.add_argument('--dashboard-url',
                    metavar="URL",
                    type=str,
                    default="https://github.com/orviz/indigo-dashboard.git",
                    help="Template for dashboard URL.")
parser.add_argument('--workspace',
                    metavar="PATH",
                    type=str,
                    default="/var/tmp/indigo-dc",
                    help="Location that points to the indigo-dc workspace.")
parser.add_argument('--automator-path',
                    metavar="PATH",
                    type=str,
                    default="/var/tmp/Automator",
                    help="Location for Automator tool.")
parser.add_argument('--automator-url',
                    metavar="URL",
                    type=str,
                    default="https://github.com/orviz/Automator.git",
                    help="URL location of Automator tool.")
parser.add_argument('--automator-branch',
                    metavar="BRANCH",
                    type=str,
                    default="indigo",
                    help="Branch to fetch from Automator repository.")
args = parser.parse_args()


def clone_repo(url, dest=None, branch=None, backup=True):
    lcmd = ["git", "clone"]
    if branch:
	lcmd.extend(["-b", branch, "--single-branch"])
    lcmd.extend([url])
    if dest:
        if os.path.exists(dest):
            if backup:
                dest_last = '.'.join([dest, "last"])
                if os.path.exists(dest_last):
                    shutil.rmtree(dest_last)
                shutil.move(dest, dest_last)
                logger.debug("Backup last existing repo directory: %s" % dest_last)
            else:
                shutil.rmtree(dest)
                logger.debug("Remove already existing repo directory: %s" % dest)
        lcmd.extend([dest])
    logger.debug("COMMAND: %s" % ' '.join(lcmd))
    try:
    	return subprocess.check_output(lcmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, err:
        logger.debug("Could not clone repository: %s" % err.output)


def push_gh_pages(name, repo_url, dashboard_path):
    last_cwd = os.getcwd()
    tmpdir = tempfile.mkdtemp()
    repodir = os.path.join(tmpdir, name)
    
    os.chdir(tmpdir)
    logger.debug("Switching to temporary directory: %s" % tmpdir)
    clone_error = False
    logger.debug("1")
    if not clone_repo(repo_url, branch="gh-pages", backup=False):
    	logger.debug("No gh-pages branch found. Creating'")
    	logger.debug("2")
	if clone_repo(repo_url, backup=False):
	    logger.debug("Switching to directory: %s" % repodir)
	    os.chdir(repodir)
	    exec_command(["git", "checkout", "--orphan", "gh-pages"])
	    exec_command(["git", "rm", "-rf", "."])
	else:
	    clone_error = True	
    else:
	logger.debug("Switching to directory: %s" % repodir)
	os.chdir(repodir)

    if clone_error:
	logger.debug("Could not clone repository: %s" % repo_url)

    logger.debug("Copying dashboard files from '%s' to '%s'" % (dashboard_path, os.getcwd()))
    dest_dashboard = ''.join([dashboard_path, '/'])
    exec_command(["rsync", "--exclude", ".git", "-avz", ''.join([dashboard_path, '/']), os.getcwd()], abort=True)
    try:
	    logger.debug("Commiting files")
	    logger.debug(subprocess.check_output(["git", "add", "*"], stderr=subprocess.STDOUT))
	    logger.debug(subprocess.check_output(["git", "commit", "-a", "-m", "Updated by %s" % SCRIPT_NAME], stderr=subprocess.STDOUT))

	    logger.debug("Pushing files")
	    logger.debug(subprocess.check_output(["git",
				     "push",
				     "https://%s@github.com/indigo-dc/%s.git" % (args.access_token, name),
				     "gh-pages",
				     "-f"], stderr=subprocess.STDOUT))
    except subprocess.CalledProcessError, err:
        logger.debug("Could not push dashboard files to gh-pages branch: %s" % err.output)
        sys.exit(err.returncode)

    logger.info("Dashboard files pushed to 'gh-pages' branch")
    shutil.rmtree(tmpdir)  
    os.chdir(last_cwd)
    

def create_workspace():
    if not os.path.exists(args.workspace):
        os.makedirs(args.workspace)
        logger.debug("Workspace '%s' created" % args.workspace)
    else:
        logger.debug("Skipping workspace creation: '%s' already exists" % args.workspace)


def create_area(name):
    area_dir = os.path.join(args.workspace, '.'.join([name, "project"]))
    if not os.path.exists(area_dir):
        os.makedirs(area_dir)
        for d in ["scm", "conf", "log", "tools", "json"]:
            abs_d = os.path.join(area_dir, d)
            os.makedirs(abs_d)
            logger.debug("Directory '%s' created" % abs_d)
    else:
        logger.debug("Skipping project area creation: '%s' already exists" % area_dir)

    return area_dir


def fetch_automator():
    if not os.path.exists(args.automator_path):
        logger.debug("Automator tool could not be found at %s" % args.automator_path)
	logger.debug("4")
        if clone_repo(args.automator_url,
                      args.automator_path,
                      branch=args.automator_branch,
                      backup=False):
            logger.debug("Automator tool cloned under %s" % args.automator_path)
    else:
        logger.info("Automator tool already found under %s" % args.automator_path)


def exec_command(lcmd, abort=False, stderr_to_stdout=True):
#    if stderr_to_stdout:
#	lcmd.append("2>&1")
    p = subprocess.Popen(lcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
	logger.debug("Command '%s' did not succeed. Reason: %s" % (' '.join(lcmd), err))
	if abort:
	    sys.exit(-1)
    return out


def main():
    # CREATE workspace
    create_workspace()
    if args.repository == "indigo_all":
    	org_data = json.loads(urllib2.urlopen("https://api.github.com/orgs/indigo-dc/repos").read())
	repos = [repo["name"] for repo in org_data]
	repos = [
            #{"name": "accounting"},
            #{"name": "cloud-info-provider"},
            #{"name": "CloudProviderRanker"},
            #{"name": "clues-indigo"},
            #{"name": "CDMI"},
            ##{"name": "dcache"},
            #{"name": "fgapiserver"},
            #{"name": "heat-translator"},
            #{"name": "identity-harmonization"},
            #{"name": "im"},
            #{"name": "im-java-api"},
            #{"name": "iam"},
            #{"name": "indigokepler"},
            #{"name": "omt-android"},
            #{"name": "java-reposync"},
            #{"name": "jsaga"},
            ##{"name": "jsaga-adaptor-rocci"},
            #{"name": "jsaga-adaptor-tosca"},
            #{"name": "liferayiam"},
            #{"name": "python-novaclient"},
            #{"name": "onedock"},
            #{"name": "ooi"},
            ##{"name": "python-openstackclient"},
            #{"name": "ophidia-server"},
            #{"name": "opie"},
            #{"name": "orchestrator"},
            #{"name": "dynpart"},
            #{"name": "pocci"},
            #{"name": "rocci-server"},
            #{"name": "synergy-service"},
            #{"name": "synergy-scheduler-manager"},
            ##{"name": "tosca-parser"},
            #{"name": "tts"},
            #{"name": "udocker"},
            #{"name": "monitoring"},
        ]
    else:
        repos = [args.repository]

    for name in repos:
        repo_url = os.path.join(args.organization_url, name)

        logger.debug("Managing project '%s'" % name)

        # 1. Create area
        area_dir = create_area(name)

        # 2. Clone repo
        scm_dir = os.path.join(area_dir, "scm", name)
        if clone_repo(repo_url, scm_dir):
            logger.debug("Repository cloned under %s" % scm_dir)

        # 3. Get tools
        tool_dir = os.path.join(area_dir, "tools")

        #clone_repo("https://github.com/VizGrimoire/GrimoireLib.git",
        clone_repo("https://github.com/orviz/GrimoireLib.git",
                   os.path.join(tool_dir, "GrimoireLib"),
		   branch="indigo",
                   backup=False)
        logger.debug("Tool GrimoireLib added")

        #clone_repo("https://github.com/VizGrimoire/VizGrimoireUtils.git",
        clone_repo("https://github.com/orviz/VizGrimoireUtils.git",
                   os.path.join(tool_dir, "VizGrimoireUtils"),
		   branch="remote_db_for_domains_analysis",
                   backup=False)
        logger.debug("Tool VizGrimoireUtils added")

        # 4. conf/main.conf generation
        conf_dir = os.path.join(area_dir, "conf")
        name_underscored = name.replace('-', '_')
        main_conf = string.Template(CONFIG_TEMPLATE).safe_substitute({
            "name": name,
            "name_underscored": name_underscored,
            "access_token": args.access_token,
            "db_user": args.db_user,
            "db_password": args.db_password,
	    "db_host": args.db_host})
        with open(os.path.join(conf_dir, 'main.conf'), 'w') as f:
            f.write(main_conf)
        logger.debug("Configuration file generated under %s" % conf_dir)

        # 5. RUN python Automator.indigo/launch.py -d /srv/indigo-dc/identity-harmonization
        fetch_automator()
        json_dir = os.path.join(area_dir, "json")
        lcmd = ["python", os.path.join(args.automator_path, "launch.py"), "-d", area_dir]
        logger.debug("Running: %s" % ' '.join(lcmd))
	try:
    	    result = subprocess.check_output(lcmd, stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError, err:
            logger.debug("Error running automator's launch.py script: %s" % err.output)
            sys.exit(err.returncode)

        # 6. VizGrimoireJS
        #
        dashboard_dir = os.path.join(tool_dir, "VizGrimoireJS")
	if clone_repo(args.dashboard_url, dashboard_dir):
            logger.debug("Tool VizGrimoireJS added")
            exec_command(["sed", "-i", r"s/project_name/%s/g" % name,
                          os.path.join(dashboard_dir, "templates/common/navbar.tmpl")])

        json_dir_dest = os.path.join(dashboard_dir, "browser/data/json")
        if os.path.exists(json_dir_dest):
            shutil.rmtree(json_dir_dest)
            logger.debug("Removing last '%s' json data directory" % json_dir_dest)
        shutil.copytree(json_dir, json_dir_dest)
        logger.debug("JSON files copied to '%s'" % json_dir_dest)
	
	push_gh_pages(name, repo_url, dashboard_dir)

if __name__ == "__main__":
    main()
