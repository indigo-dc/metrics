#!/bin/bash

echo "This script will deploy the containers for INDIGO-DataCloud SQA monitoring.Do you wish to continue?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) exit;;
    esac
done

# File containing the configuration variables 
source /root/.sqa/sqarc

# Checks
#1 metrics container
#2 variables
[[ $REPO_PATH ]] && [[ $MYSQL_ROOT_PASSWORD ]] && [[ $MYSQL_USER ]] && [[ $MYSQL_PASSWORD ]]
[[ $? -eq 1 ]] && echo "Not all the needed variables (REPO_PATH/MYSQL_ROOT_PASSWORD/MYSQL_USER/MYSQL_PASSWORD) are defined" && exit 1


Echo "Launching MetricsDB.."
docker run --name metricsdb -p 3306:3306 \
                             -v /metricsfs:/var/lib/mysql \
			     -v $REPO_PATH/docker/metrics/initdb.d:/docker-entrypoint-initdb.d \
			     -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
			     -e MYSQL_USER=$MYSQL_USER \
			     -e MYSQL_PASSWORD=$MYSQL_PASSWORD \
			     -d mariadb:latest

Echo "Launching metrics manager.."
docker run --name metrics --link metricsdb:mysql \
			  -v /root/.sqa:/root/.sqa \
			  -d orviz/indigo-metrics
