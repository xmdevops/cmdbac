#!/usr/bin/env python
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "db_webcrawler.settings")
import django
django.setup()

import traceback
import json
import logging

import crawlers
from crawler.models import *
import utils

## =====================================================================
## LOGGING CONFIGURATION
## =====================================================================
LOG = logging.getLogger()

with open(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "secrets", "secrets.json"), 'r') as auth_file:
    auth = json.load(auth_file)

def add_module(module_name, package_name, package_type_id, package_version):
    for project_type in ProjectType.objects.filter(id=package_type_id):
        package = Package()
        package.project_type = project_type
        package.name = package_name
        package.version = package_version
        package.save()
        module = Module()
        module.name = module_name
        module.package = package
        module.save()

def add_repo(repo_name, crawler_status_id, repo_setup_scripts):
    for cs in CrawlerStatus.objects.filter(id=crawler_status_id):
        repo_source = cs.source
        project_type = cs.project_type

        moduleName = "crawlers.%s" % (repo_source.crawler_class.lower())
        moduleHandle = __import__(moduleName, globals(), locals(), [repo_source.crawler_class])
        klass = getattr(moduleHandle, repo_source.crawler_class)
        crawler = klass(cs, auth)

        try:
            crawler.add_repository(repo_name, repo_setup_scripts)
        except Exception, e:
            LOG.info(traceback.print_exc())
            raise e

def deploy_repo(repo_name):
    database = Database.objects.get(name='MySQL')

    for repo in Repository.objects.filter(name=repo_name):
        print 'Attempting to deploy {} using {} ...'.format(repo, repo.project_type.deployer_class)
        try:
            result = utils.vagrant_deploy(repo, database.name, 0)
        except Exception, e:
            LOG.info(traceback.print_exc())
            raise e
        print result
        return result

def delete_repo(repo_name):
    for repo in Repository.objects.filter(name=repo_name):
        try:
            repo.delete()
        except Exception, e:
            LOG.info(traceback.print_exc())
            raise e