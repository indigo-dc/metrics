#!/usr/bin/env python

import argparse
import glob
import os
import shutil

import jenkins
import jinja2
from jinja2 import Template
import yaml


code_style = {
    "pep8": {
        "name": "PEP 8 -- Style Guide for Python Code",
        "url": "https://www.python.org/dev/peps/pep-0008/",
        "defacto": "Yes"},
}


def parse_args():
    parser = argparse.ArgumentParser(description="Generate INDIGO-DataCloud SQA reports")
    parser.add_argument('template',
			metavar="LATEX_TEMPLATE",
			type=str,
			help="LaTeX template location.")
    parser.add_argument('specdir',
			metavar="YAML_SPECS_DIR",
			type=str,
			help="Directory with the YAML specs for each product.")
    parser.add_argument('--report',
			metavar="FILE",
			type=str,
			help="LaTeX report file location.")
    parser.add_argument('--compile',
			action="store_true",
                        help="Compile resulting LaTeX rendered file.")
    return parser.parse_args()


def load_yaml(fname):
    return yaml.load(open(fname, 'r'))


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


def main(fname, specdir, output=None, do_compile=False):
    latex_jinja_env = load_jinja(fname)
    spec_yaml_files = glob.glob(os.path.join(specdir, "*.yaml"))

    for f in spec_yaml_files:
        specs = load_yaml(f)
        # jenkins
        specs["code_style"]["data"] = code_style[specs["code_style"]["standard"]]
        specs["unit_test"]["graph"] = jenkins.save_cobertura_graph(
            specs["unit_test"]["jenkins_job"],
            dest_dir="figs")
        specs["unit_test"]["data"] = jenkins.get_cobertura_data(
            specs["unit_test"]["jenkins_job"])

        # latex
        template = latex_jinja_env.get_template(os.path.basename(fname))
        r = template.render(
            product=specs,
            period="Apr-Jun 2016",
            weeks=12,
            current_week=9,
        )
        if output:
            open(args.report, 'w').write(r)
        else:
            print(r)
    if do_compile:
        for f in glob.glob(os.path.join(os.path.dirname(fname), "title_*.tex")):
            shutil.copy(f, '.')
        # FIXME(orviz) pdflatex command missing


if __name__ == "__main__":
    args = parse_args()
    main(args.template,
         args.specdir,
         output=args.report,
         do_compile=args.compile)
