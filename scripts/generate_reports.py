#!/usr/bin/env python

import argparse
import os

import jenkins
import jinja2
from jinja2 import Template


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
        #"repository": {"url": "https://github.com/indigo-dc/udocker"},
        "repository": {"url": ""},
        "code_style": {"data": code_style["pep8"], "exceptions": None, "richness": "-"},
        "unittest": {"jenkins_job": "udocker-unittest", "graph": None, "data": []},
    }
}


def parse_args():
    parser = argparse.ArgumentParser(description="Generate INDIGO-DataCloud SQA reports")
    parser.add_argument('template',
			metavar="FILE",
			type=str,
			help="LaTeX template location.")
    parser.add_argument('--report',
			metavar="FILE",
                        #default="indigo_sqa.tex",
			type=str,
			help="LaTeX report file location.")
    return parser.parse_args()


def load_jinja(fname):
    if os.path.isabs(fname):
        load_dir = os.path.dirname(fname)
    else:
        load_dir = os.path.dirname(os.path.abspath(fname))

    return jinja2.Environment(
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
            loader = jinja2.FileSystemLoader(load_dir)
    )


def main(fname, output=None):
    latex_jinja_env = load_jinja(fname)
    for product in products.keys():
        # jenkins
        products[product]["unittest"]["graph"] = jenkins.save_cobertura_graph(
            products[product]["unittest"]["jenkins_job"],
            dest_dir="figs")
        products[product]["unittest"]["data"] = jenkins.get_cobertura_data(
            products[product]["unittest"]["jenkins_job"])

        # latex
        template = latex_jinja_env.get_template(os.path.basename(fname))
        r = template.render(
                product=product,
                period="Apr-May 2016",
                tasks=products[product]["tasks"],
                repository=products[product]["repository"],
                code_style=products[product]["code_style"],
                unit_test=products[product]["unittest"],
        )
        if output:
            open(args.report, 'w').write(r)
        else:
            print(r)


if __name__ == "__main__":
    args = parse_args()
    main(args.template, output=args.report)
