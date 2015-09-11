# fab tasks for deplying and restarting bsp nodejs server, proxied via apache
#
# Example:
#  > BLUESKYWEB_SERVERS=username@hostname.com fab deploy
#
# Using Apache to proxy:
#  If you'd like to let apache proxy requests to the bluesky web server,
#  You can use something like the following
#  file: /etc/apache2/sites-available/
#    <VirtualHost *:80>
#            ServerAdmin webmaster@localhost
#            ServerName blueskyweb.bar.com
#            ServerAlias www.blueskyweb.bar.com
#
#            ProxyPass / http://127.0.0.1:9000/
#            ProxyPassReverse / http://127.0.0.1:9000/
#
#            ErrorLog /var/www/blueskyweb.bar.com/logs/error.log
#            LogLevel warn
#            CustomLog /var/www/blueskyweb.bar.com/logs/access.log combined
#    </VirtualHost>

import datetime
import os
import sys
from fabric import contrib
from fabric.api import *

from pyairfire.fabric.utils import (
    install_pyenv, install_pyenv_environment, add_pyenv_to_dot_file
)

from bluesky import __version__

# Only tell fabric to use .ssh config if it exists
# TODO: see how fabric searches for .ssh/config and do the same:
ssh_config = os.path.join(os.path.expanduser('~'), '.ssh/config')
if os.path.isfile(ssh_config):
    env.use_ssh_config = True

def error(msg):
    print('* {}'.format(msg))
    sys.exit(1)

##
## Role definitions and env vars
##

if not os.environ.get('BLUESKYWEB_SERVERS'):
    error('Specify BLUESKYWEB_SERVERS; ex. BLUESKYWEB_SERVERS=username@hostname.com,bar@baz.com')
env.roledefs.update({
    'web': os.environ.get('BLUESKYWEB_SERVERS').split(',')
})

PYTHON_VERSION = os.environ.get('PYTHON_VERSION') or "2.7.3"
VIRTUALENV_NAME = "bluesky-web-{}".format(PYTHON_VERSION)
REPO_GIT_URL = "git@github.com:pnwairfire/bluesky.git"
DEFAULT_BLUESKYWEB_USER = 'www-data'

##
## Helper methods
##

def env_var_or_prompt_for_input(env_var_name, msg, default):
    if not os.environ.get(env_var_name):
        sys.stdout.write('{} [{}]: '.format(msg, default))
        return raw_input().strip() or default
    else:
        return os.environ.get(env_var_name)

def install_python_tools():
    sudo('which git || apt-get install git-core')
    if not cmd_exists('pyenv'):
        print("Installing pyenv...")
        install_pyenv()
        add_pyenv_to_dot_file()
    print("Installing pyenv environment {}...".format(VIRTUALENV_NAME))
    install_pyenv_environment(PYTHON_VERSION, VIRTUALENV_NAME)
    for role in env['effective_roles']:
        add_pyenv_to_dot_file(**config.DOT_FILES[role])

class prepare_code:
    """Context manager that clones repo on enter and deletes it on exit.
    """

    # def __init__(self, branch_or_tag_or_commit):
    #     self.branch_or_tag_or_commit = branch_or_tag_or_commit

    def __enter__(self):
        self.repo_path_name = self.get_code()
        return self.repo_path_name

    def __exit__(self, type, value, traceback):
        self.clean_up()

        # TODO: suppress exception (or just certain exceptions) by returning
        #  True no matter what (first outputting an error message) *or* by
        #  calling error function.  (type, value, and traceback are undefined
        #  unless there was an exception.)

    def get_code(self):
        bluesky_version = env_var_or_prompt_for_input('BLUESKY_VERSION',
            'Git tag or commit to deploy', 'HEAD')
        repo_dir_name = 'pnwairfire-bluesky-{}'.format(bluesky_version)

        with lcd('/tmp/'):
            local('git clone %s %s' % (REPO_GIT_URL, repo_dir_name))

        self.repo_path_name = '/tmp/{}'.format(repo_dir_name)
        with lcd(repo_path_name):
            local('git checkout %s' % (bluesky_version))
            local('rm .python-version')
        return self.repo_path_name

    def clean_up(self):
        """Removes local repo *if it wasn't already existing*
        """
        local('rm -rf %s*' % (self.repo_path_name))

##
## Tasks
##

@task
@roles('web')
def setup():
    """Sets up server to run bluesky web

    Required:
     - BLUESKYWEB_SERVERS

    Optional:
     - BLUESKYWEB_USER (default: www-data)
     - BLUESKY_VERSION (default: HEAD)

    Examples:
        > BLUESKYWEB_SERVERS=username@hostname fab setup
    """
    blueskyweb_user = env_var_or_prompt_for_input('BLUESKYWEB_USER',
        'User to run blueskyweb', DEFAULT_BLUESKYWEB_USER)

    #sudo('which node || sudo apt-get install -y nodejs')
    install_python_tools()

    # print('Uploading apache upstart script...')
    # put('./init/', TMP_DIR)

    print('Creating remote root directory...')
    #sudo('mkdir -p /var/www/blueskyweb')
    sudo('mkdir -p /var/www/blueskyweb/logs/')
    sudo('chown -R www-data:www-data /var/www/blueskyweb')

@task
@roles('web')
def deploy():
    """Deploys bluesky code to server and starts web service

    Required:
     - BLUESKYWEB_SERVERS

    Optional:
     - BLUESKYWEB_USER (default: www-data)

    Examples:
        > BLUESKYWEB_SERVERS=username@hostname fab deploy
    """
    with prepare_code() as repo_path_name:
        with cd(repo_path_name):
            print("Installing bluesky package...")
            sudo('PYENV_VERSION={} python setup.py install'.format(VIRTUALENV_NAME))
            blueskyweb_user = env_var_or_prompt_for_input('BLUESKYWEB_USER',
                'User to run blueskyweb', DEFAULT_BLUESKYWEB_USER)
            print('Preparing upstart script and moving to /etc/init/ ...')
            upstart_script = './init/blueskyweb.conf'
            contrib.files.sed(upstart_script, '__BLUESKYWEBUSER__'. blueskyweb_user)
            contrib.files.sed(upstart_script, '__VIRTUALENV__', VIRTUALENV_NAME)
            sudo('mv {}/init/blueskyweb.conf /etc/init'.format(TMP_DIR))
            sudo('chown root:root /etc/init/blueskyweb.conf')
            sudo('chmod 644 /etc/init/blueskyweb.conf')

    execute(restart)

@task
@roles('web')
def restart():
    """Restarts bluesky web service

    Required:
     - BLUESKYWEB_SERVERS

    Examples:
        > BLUESKYWEB_SERVERS=username@hostname fab deploy
    """
    sudo('service blueskyweb restart')
