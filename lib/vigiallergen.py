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

- vigiallergen base class

"""

class VigiallergensException(Exception):
    """
    Vigipollens exception
    """

    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)

class BaseVigiallergens:
    """ Base class of Vigiallergens
    """

    # -------------------------------------------------------------------------------------------------
    def __init__(self, log, send, stop, device_id):
        """ Init Vigipollens object
            @param log : log instance
            @param send : send
            @param stop : stop flag
            @param device_id : domogik device id
        """
        self.log = log
        self.device_id = device_id
        self._send = send
        self._stop = stop
        self.run = False
        self._lastUpdate = 0

    # -------------------------------------------------------------------------------------------------
    def setParams(self, params):
        """ Set params of type
            must be overwriten
        """
        self.log.warning(u"setParams function not implemented for base class Vigiallergens")

    def check(self):
        """ Get allergen vigilance datas
            must be overwriten
        """
        self.run = False
        self._lastUpdate = 0
        self.log.warning(u"Check function not implemented for base class Vigiallergens")
