FROM ubuntu:xenial
MAINTAINER Pablo Orviz <orviz@ifca.unican.es>

USER root

RUN apt-get clean
RUN apt-get update
RUN apt-get -y install vim texlive texlive-latex-extra \\
                       python-devel libjpeg8-dev zlib1g-dev

RUN pip install jenkinsapi Pillow

ADD https://raw.githubusercontent.com/amix/vimrc/master/vimrcs/basic.vim /root/.vimrc
