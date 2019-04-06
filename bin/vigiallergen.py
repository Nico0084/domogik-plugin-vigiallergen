#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

vigiallergen

Implements
==========

- VigiallergenManager

"""

from domogik.common.plugin import Plugin
from domogik_packages.plugin_vigiallergen.lib.vigirnsapollens import VigiRnsaPollens
import threading
import traceback

class VigiallergenManager(Plugin):
    """ Get allergen vigilances
    """

    def __init__(self):
        """ Init plugin
        """
        Plugin.__init__(self, name='vigiallergen')

        # check if the plugin is configured. If not, this will stop the plugin and log an error
        #if not self.check_configured():
        #    return
        # get the devices list
        self.devices = self.get_device_list(quit_if_no_device = True)

        # get the sensors id per device :
        self.sensors = self.get_sensors(self.devices)

        # create a Vigipollens thread for each device
        self.vigiallergensthreads = {}
        self.vigiallergens_list = {}
        self._loadDMGDevices()
        # Callback for new/update devices
        self.log.info(u"==> Add callback for new/update devices.")
        self.register_cb_update_devices(self.reload_devices)
        self.ready()

    def _loadDMGDevices(self):
        """ Check and load domogik device if necessary
        """
        vigiallergens_list = {}
        directory = "{0}/{1}_{2}".format(self.get_packages_directory(), self._type, self._name)
        for a_device in self.devices: # for now, only rnsa polens device type, to add other add an handling device_type
            try:
                # global device parameters
                departement = int(self.get_parameter(a_device, "departement"))
                if departement > 0 or departement < 96:
                    if departement < 10: departement = "0" + str(departement)
                    else: departement = str(departement)

                    device_id = a_device["id"]
                    if device_id not in self.vigiallergens_list :
                        self.log.info(u"Create device ({0}) allergens vigilance for departement '{1}'".format(device_id, departement))
                        vigiallergens_list[device_id] = VigiRnsaPollens(self.log, self.send_data, self.get_stop(), self.get_config, directory, device_id, departement, self.register_thread)
                        # start the vigipollens thread
                        thr_name = "vigiallergens_{0}".format(device_id)
                        self.vigiallergensthreads[thr_name] = threading.Thread(None,
                                                  vigiallergens_list[device_id].check,
                                                  thr_name,
                                                  (),
                                                  {})
                        self.vigiallergensthreads[thr_name].start()
                        self.register_thread(self.vigiallergensthreads[thr_name])
                    else :
                        self.vigiallergens_list[device_id].setParams(departement)
                        vigiallergens_list[device_id] = self.vigiallergens_list[device_id]
                else:
                    self.log.error(u"### Departement '{0}' not supported (must in 01 => 95) !".format(departement))
            except:
                self.log.error(u"{0}".format(traceback.format_exc()))   # we don't quit plugin if an error occured, a vigipollens device can be KO and the others be ok
        # Check deleted devices
        for device_id in self.vigiallergens_list :
            if device_id not in vigiallergens_list :
                thr_name = "vigiallergens_{0}".format(device_id)
                if thr_name in self.vigiallergensthreads :
                    self.run = False
                    self.unregister_thread(self.vigiallergensthreads[thr_name])
                    del self.vigiallergensthreads[thr_name]
                    self.log.info(u"Device {0} removed".format(device_id))

        self.vigiallergens_list = vigiallergens_list

    def send_data(self, device_id, dep, dataSensors):
        """ Send the vigipollens sensors values over MQ
        """
        data = {}
        for sensor, value in dataSensors.iteritems():
            if sensor in self.sensors[device_id] :
                data[self.sensors[device_id][sensor]] = value
        self.log.info("==> 0MQ PUB for departement '%s' sended = %s " % (dep, format(data)))

        try:
            self._pub.send_event('client.sensor', data)
        except:
            self.log.debug(u"Bad MQ message to send : {0}".format(data))
            pass

    def reload_devices(self, devices):
        """ Called when some devices are added/deleted/updated
        """
        self.devices = devices
        self.sensors = self.get_sensors(devices)
        self._loadDMGDevices()
        self.log.info(u"==> Reload Device called, All updated")

if __name__ == "__main__":
    vigiallergen = VigiallergenManager()
