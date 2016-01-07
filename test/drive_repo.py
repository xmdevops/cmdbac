#!/usr/bin/env python
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, "core"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmudbac.settings")
import django
django.setup()
from library.models import *
from deployers import *
from drivers import *
from analyzers import *

from library.models import *
import utils

def main():
    if len(sys.argv) not in [3, 4]:
        return
    repo_name = sys.argv[1]
    deploy_id = sys.argv[2]
    database_name = 'MySQL'
    print 'Database : {} ...'.format(database_name)

    repo = Repository.objects.get(name=repo_name)
    database = Database.objects.get(name=database_name)
    
    moduleName = "deployers.%s" % (repo.project_type.deployer_class.lower())
    moduleHandle = __import__(moduleName, globals(), locals(), [repo.project_type.deployer_class])
    klass = getattr(moduleHandle, repo.project_type.deployer_class)
    
    deployer = klass(repo, database, deploy_id)

    try:
        driver = BaseDriver(deployer)
        driverResult = driver.drive()
    except Exception, e:
        LOG.exception(e)
        driverResult = {}

    # deployer.kill_server()

if __name__ == "__main__":
    main()