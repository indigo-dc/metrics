#!/usr/bin/env python

import os

import jenkins
import jinja2
from jinja2 import Template


latex_jinja_env = jinja2.Environment(
	block_start_string = '\BLOCK{',
	block_end_string = '}',
	variable_start_string = '\VAR{',
	variable_end_string = '}',
	comment_start_string = '\#{',
	comment_end_string = '}',
	line_statement_prefix = '%%',
	line_comment_prefix = '%#',
	trim_blocks = True,
	autoescape = False,
	loader = jinja2.FileSystemLoader(os.path.abspath('.'))
)

code_style = {
    "pep8": {
        "name": "PEP 8 -- Style Guide for Python Code",
        "url": "https://www.python.org/dev/peps/pep-0008/"},
        "de_facto": "Yes",
}

# FIXME(orviz) Tasks must be taken from OpenProject API
products = {
    "udocker": {
        "tasks": {
            "parent": {"id": "3641", "progress": "57"},
            "children": [
                {"name": "Repository synchronization", "id": "3647", "progress": "53"},
                {"name": "Code style specification", "id": "3650", "progress": "100"},
                {"name": "Unit testing coverage", "id": "3653", "progress": "100"},
                {"name": "Functional and integration testing coverage", "id": "3656", "progress": "0"},
                {"name": "GitBook documentation", "id": "3659", "progress": "53"}],
        },
        "code_style": {"data": code_style["pep8"], "exceptions": None, "richness": "-"},
        "unittest": {"jenkins_job": "udocker-unittest", "graph": None, "data": []},
    }
}

for product in products.keys():
    # jenkins
    products[product]["unittest"]["graph"] = jenkins.save_cobertura_graph(
        products[product]["unittest"]["jenkins_job"],
        dest_dir="figs")
    products[product]["unittest"]["data"] = jenkins.get_cobertura_data(
        products[product]["unittest"]["jenkins_job"])

    # latex
    template = latex_jinja_env.get_template("report.tex")
    print(template.render(
        product=product,
        period="Apr-May 2016",
        tasks=products[product]["tasks"],
        code_style=products[product]["code_style"],
        unit_test=products[product]["unittest"],
    ))

