# -*- coding: utf-8 -*-

### common imports
from flask import Blueprint, abort
from domogik.common.utils import get_packages_directory
from domogik.admin.application import render_template
from domogik.admin.views.clients import get_client_detail, get_client_devices
from jinja2 import TemplateNotFound
import traceback
import sys

### package specific imports
import subprocess

#from domogik.common.plugin import Plugin.get_config ???


### package specific functions

def get_informations(devices):
    departmentslist = []
    for a_device in devices:
        departmentslist.append(a_device['parameters']['departement']['value'])
    return departmentslist


def get_errorlog(cmd, log):
    print("Command = %s" % cmd)
    errorlog = subprocess.Popen([cmd, log], stdout=subprocess.PIPE)
    output = errorlog.communicate()[0]
    if isinstance(output, str):
        output = unicode(output, 'utf-8')
    return output




### common tasks
package = "plugin_vigiallergen"
template_dir = "{0}/{1}/admin/templates".format(get_packages_directory(), package)
static_dir = "{0}/{1}/admin/static".format(get_packages_directory(), package)
geterrorlogcmd = "{0}/{1}/admin/geterrorlog.sh".format(get_packages_directory(), package)
logfile = "/var/log/domogik/{0}.log".format(package)

plugin_vigiallergen_adm = Blueprint(package, __name__,
                        template_folder = template_dir,
                        static_folder = static_dir)


@plugin_vigiallergen_adm.route('/<client_id>')
def index(client_id):
    detail = get_client_detail(client_id)      # vigiallergen plugin configuration
    devices = get_client_devices(client_id)     # vigiallergen plugin devices list
    #print("Admin vigiallergen devices\n %s" % format(devices))
    print("Departements list: %s" % format(get_informations(devices)))
    try:
        return render_template('plugin_vigiallergen.html',
            clientid = client_id,
            client_detail = detail,
            mactive ="clients",
            active = 'advanced',
            departementslist = get_informations(devices),
            logfile = logfile,
            errorlog = get_errorlog(geterrorlogcmd, logfile))

    except TemplateNotFound:
        abort(404)

@plugin_vigiallergen_adm.route('/<client_id>/log')
def log(client_id):
    clientid = client_id
    detail = get_client_detail(client_id)
    with open(logfile, 'r') as contentLogFile:
        content_log = contentLogFile.read()
    try:
        return render_template('plugin_vigiallergen_log.html',
            clientid = client_id,
            client_detail = detail,
            mactive="clients",
            active = 'advanced',
            logfile = logfile,
            contentLog = content_log)

    except TemplateNotFound:
        abort(404)
