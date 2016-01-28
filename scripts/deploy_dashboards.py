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
url = $name
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
parser.add_argument('db_user',
                    metavar="USERID",
                    type=str,
                    default="indigo.dc",
                    help="MetricsDB user ID.")
parser.add_argument('db_password',
                    metavar="PASSWORD",
                    type=str,
                    default="",
                    help="MetricsDB user password.")
parser.add_argument('db_host',
                    metavar="HOST",
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

def clone_repo(url, dest, branch=None, backup=True):
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

    lcmd = ["git", "clone", url, dest]
    if branch:
        logger.debug("Selected branch '%s'" % branch)
        lcmd = ["git", "clone", "-b", branch, "--single-branch", url, dest]
    else:
        lcmd = ["git", "clone", url, dest]

    return subprocess.check_output(lcmd, stderr=subprocess.STDOUT)


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
        if clone_repo(args.automator_url,
                      args.automator_path,
                      branch=args.automator_branch,
                      backup=False):
            logger.debug("Automator tool cloned under %s" % args.automator_path)
    else:
        logger.info("Automator tool already found under %s" % args.automator_path)

def main():
    # CREATE workspace e.g. /srv/indigo-dc
    create_workspace()
    org_data = json.loads(urllib2.urlopen("https://api.github.com/orgs/indigo-dc/repos").read())
    for repo in org_data:
        name = repo["name"]
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

        clone_repo("https://github.com/VizGrimoire/GrimoireLib.git",
                   os.path.join(tool_dir, "GrimoireLib"),
                   backup=False)
        logger.debug("Tool GrimoireLib added")

        clone_repo("https://github.com/VizGrimoire/VizGrimoireUtils.git",
                   os.path.join(tool_dir, "VizGrimoireUtils"),
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
            "db_password": args.db_password})
        with open(os.path.join(conf_dir, 'main.conf'), 'w') as f:
            f.write(main_conf)
        logger.debug("Configuration file generated under %s" % conf_dir)

        # 5. RUN python Automator.indigo/launch.py -d /srv/indigo-dc/identity-harmonization
        fetch_automator()
        json_dir = os.path.join(area_dir, "json")
        lcmd = ["python", os.path.join(args.automator_path, "launch.py"), "-d", area_dir]
        p = subprocess.Popen(lcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        logger.debug("Running: %s" % ' '.join(lcmd))
        if stderr:
            logger.fail("Error running automator's launch.py script")
            sys.exit(200)

        # 6. VizGrimoireJS
        #
        # If gh-repos branch exits, fetch it, otherwise (likely only 1st time) create the
        # dashboard from the template
        dashboard_dir = os.path.join(tool_dir, "VizGrimoireJS")
        lcmd = ["git", "--git-dir", os.path.join(scm_dir, ".git"), "branch", "-a"]
        for line in subprocess.check_output(lcmd, stderr=subprocess.STDOUT).split('\n'):
            line = line.strip()
            if line == "remotes/origin/gh-pages":
                logger.debug("gh-pages branch found. Using it for dashboard re-creation")
                clone_repo(repo_url, dashboard_dir, branch="gh-pages")
            else:
                logger.debug("gh-pages branch not found. Using template from %s" % args.dashboard_url)
                clone_repo(args.dashboard_url, dashboard_dir)
                subprocess.check_output(["sed", "-i", r"s/project_name/%s/g" % name,
                                         os.path.join(dashboard_dir, "templates/common/navbar.tmpl")])
        logger.debug("Tool VizGrimoireJS added")
        json_dir_dest = os.path.join(dashboard_dir, "browser/data/json")
        if os.path.exists(json_dir_dest):
            shutil.rmtree(json_dir_dest)
            logger.debug("Removing last '%s' json data directory" % json_dir_dest)
        shutil.copytree(json_dir, json_dir_dest)
        logger.debug("JSON files copied to '%s'" % json_dir_dest)


if __name__ == "__main__":
    main()
