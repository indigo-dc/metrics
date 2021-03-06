# INDIGO-DataCloud SQA monitoring

This repository contains the configuration scripts needed to deploy the metric
monitoring system for INDIGO-DataCloud project. 

## Description and tools

The metric collector uses [MetricsGrimoire](https://github.com/metricsgrimoire), 
generating dashboards, using [VizGrimoire](https://github.com/vizgrimoire), for
each repository under [indigo-dc GitHub organization](https://github.com/indigo-dc).

It is Docker-based (both DB and consumer). The metric collector container uses
a [custom Docker image](docker/metrics/Dockerfile) with all the tools
needed for the metric gathering and displaying.

## DB considerations

The MetricsDB container uses the [official MariaDB image](https://hub.docker.com/_/mariadb/)
and it is recommended to use a Docker volume for storing the DB data. The current
(production) deployment at CERN OpenStack infra uses a (cinder) volume that is mapped
to the Docker volume being used by the Metrics DB container.

The initial DB configuration is customized via [SQL scripts](docker/metrics/initdb.d/) that 
the Docker image triggers at boot time.

## Deployment

Just run the `run_container.sh` script to deploy both the MetricsDB and the 
collector containers.

This script expects a file in `/root/.sqa/sqarc` with all the following environment variables 
defined:

- REPO_PATH
- MYSQL_ROOT_PASSWORD
- MYSQL_USER
- MYSQL_PASSWORD
- MYSQL_HOST
- GITHUB_TOKEN

## Generating repository dashboards

Tackled by `deploy_dashboards.py` script, it needs credentials (passed through 
positional arguments) in order to get access to the MetricsDB and to push dashboard files
to GitHub. Usually it will be ok with:

```
	deploy_dashboards.py <repo> $MYSQL_USER $MYSQL_PASSWORD $MYSQL_HOST $GITHUB_TOKEN
```

Once `deploy_dashboards.py` has been triggered in the collector, the
dashboards will be accesible via:

```
	https://indigo-dc.github.io/<repository-name>
```

which uses GitHub Pages for creating the websites.

In the current implementation, the metrics manager container exposes a service (port 5000, see 
below) that will receive POSTs from GitHub webhooks to create/update the dashboard for the given 
repository. For that purpose it uses [Python GitHub Webhooks](https://github.com/carlos-jenkins/python-github-webhooks)
tool, which will run the [hook](https://github.com/indigo-dc/metrics/raw/master/scripts/hooks/all)
for triggering the `deploy_dashboard.py` execution.
