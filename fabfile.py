# -*- coding: utf-8 -*-
"""Fabric file for managing this project.

See: http://www.fabfile.org/
"""
from __future__ import absolute_import, unicode_literals, with_statement

# Standard Library
from contextlib import contextmanager as _contextmanager
from functools import partial
from os.path import dirname, isdir, join

# Third Party Stuff
from fabric.api import local as fabric_local, env
from fabric import api as fab

local = partial(fabric_local, shell='/bin/bash')


HERE = dirname(__file__)

# ==========================================================================
#  Settings
# ==========================================================================
env.project_name = 'bot_platform'
env.apps_dir = join(HERE, env.project_name)
env.docs_dir = join(HERE, 'docs')
env.virtualenv_dir = join(HERE, 'venv')
env.requirements_file = join(HERE, 'requirements/development.txt')
env.shell = "/bin/bash -l -i -c"

env.use_ssh_config = True
env.dotenv_path = join(HERE, '.env')
env.config_setter = local


def init(vagrant=False):
    """Prepare a local machine for development."""

    install_requirements()
    local('createdb %(project_name)s' % env)  # create postgres database
    manage('migrate')


def install_requirements(file=env.requirements_file):
    """Install project dependencies."""
    verify_virtualenv()
    # activate virtualenv and install
    with virtualenv():
        local('pip install -r %s' % file)


def serve_docs(options=''):
    """Start a local server to view documentation changes."""
    with fab.lcd(HERE) and virtualenv():
        local('mkdocs serve {}'.format(options))


def deploy_docs():
    with fab.lcd(HERE) and virtualenv():
        local('mkdocs gh-deploy')
        local('rm -rf _docs_html')


def shell():
    manage('shell_plus')


def test(options='--pdb --cov'):
    """Run tests locally. By Default, it runs the test using --ipdb.
    You can skip running it using --ipdb by running - `fab test:""`
    """
    with virtualenv():
        local('flake8 .')
        local("py.test %s" % options)


def serve(host='127.0.0.1:8000'):
    """Run local developerment server, making sure that dependencies and
    database migrations are upto date.
    """
    install_requirements()
    migrate()
    manage('runserver %s' % host)


def makemigrations(app=''):
    """Create new database migration for an app."""
    manage('makemigrations %s' % app)


def migrate():
    """Apply database migrations."""
    manage('migrate')


def createapp(appname):
    """fab createapp <appname>
    """
    path = join(env.apps_dir, appname)
    local('mkdir %s' % path)
    manage('startapp %s %s' % (appname, path))


#  Enviroments & Deployments
# ---------------------------------------------------------
def prod():
    env.host_group = 'production'
    env.remote = 'origin'
    env.branch = 'prod'
    env.hosts = ['prod.bot_platform.com']
    env.dotenv_path = '/home/ubuntu/bot-platform-web/.env'
    env.config_setter = fab.run


def config(action=None, key=None, value=None):
    """Read/write to .env file on local and remote machines.

    Usages: fab [prod] config:set,<key>,<value>
            fab [prod] config:get,<key>
            fab [prod] config:unset,<key>
            fab [prod] config:list
    """
    import dotenv
    command = dotenv.get_cli_string(env.dotenv_path, action, key, value)
    env.config_setter('touch %(dotenv_path)s' % env)

    if env.config_setter == local:
        with virtualenv():
            env.config_setter(command)
    else:
        env.config_setter(command)
        restart_servers()


def restart_servers():
    fab.sudo('supervisorctl restart all')


def configure(tags='', skip_tags='deploy'):
    """Setup a host using ansible scripts

    Usages: fab [prod|qa|dev] configure
    """
    fab.require('host_group')
    cmd = 'ansible-playbook -i hosts site.yml --limit=%(host_group)s' % env
    with fab.lcd('provisioner'):
        if tags:
            cmd += " --tags '%s'" % tags
        if skip_tags:
            cmd += " --skip-tags '%s'" % skip_tags
        local(cmd)


def deploy():
    configure(tags='deploy', skip_tags='')


# Helpers
# ---------------------------------------------------------
def manage(cmd, venv=True):
    with virtualenv():
        local('python manage.py %s' % cmd)


@_contextmanager
def virtualenv():
    """Activates virtualenv context for other commands to run inside it.
    """
    with fab.cd(HERE):
        with fab.prefix('source %(virtualenv_dir)s/bin/activate' % env):
            yield


def verify_virtualenv():
    """This modules check and install virtualenv if it not present.
    It also creates local virtualenv directory if it's not present
    """
    from distutils import spawn
    if not spawn.find_executable('virtualenv'):
        local('sudo pip install virtualenv')

    if not isdir(env.virtualenv_dir):
        local('virtualenv %(virtualenv_dir)s -p $(which python2)' % env)
