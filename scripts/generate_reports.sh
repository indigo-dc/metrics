#!/bin/bash

last_dir=`pwd`
build_dir="../reports/build"

[ ! -d $build_dir ] && mkdir -p $build_dir

cd $build_dir
virtualenv .venv
source .venv/bin/activate
pip install requests jenkinsapi Jinja2 Pillow pytz PyYAML
python ${last_dir}/generate_reports.py ../templates/report.tex ../specs/ --output-dir=`pwd`
deactivate
cd $last_dir
