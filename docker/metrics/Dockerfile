FROM ubuntu:trusty
MAINTAINER Pablo Orviz <orviz@ifca.unican.es>

USER root

RUN apt-get clean
RUN apt-get update
RUN apt-get -y install python git

ENV tooldir /srv/tools
RUN mkdir -p $tooldir


# repositoryhandler
WORKDIR $tooldir
RUN apt-get -y install autoconf wget curl
RUN git clone git://github.com/MetricsGrimoire/RepositoryHandler.git
WORKDIR ${tooldir}/RepositoryHandler
RUN python setup.py install


# cmetrics
WORKDIR $tooldir
RUN apt-get -y install gcc flex make automake1.11
RUN git clone https://github.com/MetricsGrimoire/CMetrics.git
WORKDIR ${tooldir}/CMetrics
RUN ./autogen.sh && make && make install


# cvsanaly
WORKDIR $tooldir
RUN apt-get -y install python-setuptools python-mysqldb pymetrics cccc sloccount
RUN git clone git://github.com/MetricsGrimoire/CVSAnalY.git
WORKDIR ${tooldir}/CVSAnalY
RUN python setup.py install


# sortinghat
#RUN apt-get -y install python3.4 \
#		       python3-sqlalchemy \
#		       python3-dateutil \
#		       python3-jinja
#
#RUN apt-get -y install software-properties-common
#RUN apt-add-repository -y 'deb http://archive.ubuntu.com/ubuntu/ wily universe'
#RUN apt-get update
#RUN apt-get -y install python3-pymysql
#RUN apt-add-repository -y -r 'deb http://archive.ubuntu.com/ubuntu/ wily universe'
#RUN apt-get update

WORKDIR $tooldir
RUN git clone https://github.com/MetricsGrimoire/sortinghat.git
WORKDIR ${tooldir}/sortinghat
RUN python setup.py install


# bicho
WORKDIR $tooldir
RUN apt-get -y install python-storm \
		       python-launchpadlib \
		       python-beautifulsoup \
		       python-feedparser \
		       python-dateutil
RUN git clone https://github.com/MetricsGrimoire/Bicho.git
WORKDIR ${tooldir}/Bicho
RUN python setup.py install


# pullpo
WORKDIR $tooldir
RUN apt-get -y install python-pip \
		       python-sqlalchemy \
		       python-requests \
		       python-dev \
		       libffi-dev \
		       libssl-dev 
ADD https://pypi.python.org/packages/source/g/github3.py/github3.py-1.0.0a1.tar.gz /tmp/github3.py-1.0.0a1.tar.gz
RUN tar xvfz /tmp/github3.py-1.0.0a1.tar.gz -C /tmp/
WORKDIR /tmp/github3.py-1.0.0a1
RUN python setup.py install ; exit 0 # urltemplate false positive
WORKDIR $tooldir
RUN git clone https://github.com/MetricsGrimoire/pullpo.git
WORKDIR ${tooldir}/pullpo
RUN python setup.py install


# rremoval
WORKDIR $tooldir
RUN git clone https://github.com/MetricsGrimoire/rremoval.git
WORKDIR ${tooldir}/rremoval
RUN python setup.py install


# R & VizGrimoire
RUN apt-get -y install r-base \
		   python-rpy2 \
		   python-scipy \
		   python-jinja2 \ 
		   language-pack-en \
		   p7zip


# custom indigo stuff
WORKDIR $tooldir
ENV metrics_repo_path $tooldir/metrics
ENV automator_repo_path $tooldir/Automator
RUN git clone https://github.com/orviz/Automator.git
RUN git clone https://github.com/indigo-dc/metrics.git 
#RUN sed -i '/exit 0/i\source /root/.sqa/sqarc\ncd $metrics_repo_path && git pull origin master\ncd $automator_repo_path && git pull origin master'


# misc 
WORKDIR /root
RUN apt-get -y install vim
