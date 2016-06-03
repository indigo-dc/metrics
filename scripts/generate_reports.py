#!/usr/bin/env python

import argparse
import glob
import os
import shutil

import jenkins
import jinja2
from jinja2 import Template
import yaml


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
    parser.add_argument('--code-style',
                        metavar="YAML_FILE",
                        type=str,
                        help="Compile resulting LaTeX rendered file.")
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


def main(fname, specdir, code_style=None, output=None, do_compile=False):
    latex_jinja_env = load_jinja(fname)
    spec_yaml_files = glob.glob(os.path.join(specdir, "*.yaml"))
    if not code_style:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        code_style = load_yaml(os.path.join(current_dir,
                               os.pardir,
                               "reports/data/code_style.yaml"))

    for f in spec_yaml_files:
        specs = load_yaml(f)
        # specs - code_style
        specs["code_style"]["job_url"] = jenkins.get_last_job_url(
            specs["code_style"]["jenkins_job"])
        specs["code_style"]["data"] = code_style[specs["code_style"]["standard"]]
        # specs - unit_test
        specs["unit_test"]["job_url"] = jenkins.get_last_job_url(
            specs["unit_test"]["jenkins_job"])
        specs["unit_test"]["graph"] = jenkins.save_cobertura_graph(
            specs["unit_test"]["jenkins_job"],
            dest_dir="figs")
        specs["unit_test"]["data"] = jenkins.get_cobertura_data(
            specs["unit_test"]["jenkins_job"])
        # specs - config_management
        specs["config_management"]["job_url"] = jenkins.get_last_job_url(
            specs["config_management"]["jenkins_job"])

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
         code_style=args.code_style,
         output=args.report,
         do_compile=args.compile)
