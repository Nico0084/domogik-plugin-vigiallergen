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

Vigipollens

Implements
==========

- Vigipollens Manager

"""

import traceback
import threading
import requests
import time
import locale
from datetime import datetime
import urllib
from six.moves.html_parser import HTMLParser
from domogik_packages.plugin_vigiallergen.lib.vigiallergen import BaseVigiallergens

DEPARTMENTS = {
    '01': u'Ain',
    '02': u'Aisne',
    '03': u'Allier',
    '04': u'Alpes-de-Haute-Provence',
    '05': u'Hautes-Alpes',
    '06': u'Alpes-Maritimes',
    '07': u'Ardèche',
    '08': u'Ardennes',
    '09': u'Ariège',
    '10': u'Aube',
    '11': u'Aude',
    '12': u'Aveyron',
    '13': u'Bouches-du-Rhône',
    '14': u'Calvados',
    '15': u'Cantal',
    '16': u'Charente',
    '17': u'Charente-Maritime',
    '18': u'Cher',
    '19': u'Corrèze',
    '20': u'Corse',
    '21': u'Côte-d\'Or',
    '22': u'Côtes-d\'Armor',
    '23': u'Creuse',
    '24': u'Dordogne',
    '25': u'Doubs',
    '26': u'Drôme',
    '27': u'Eure',
    '28': u'Eure-et-Loir',
    '29': u'Finistère',
    '30': u'Gard',
    '31': u'Haute-Garonne',
    '32': u'Gers',
    '33': u'Gironde',
    '34': u'Hérault',
    '35': u'Ille-et-Vilaine',
    '36': u'Indre',
    '37': u'Indre-et-Loire',
    '38': u'Isère',
    '39': u'Jura',
    '40': u'Landes',
    '41': u'Loir-et-Cher',
    '42': u'Loire',
    '43': u'Haute-Loire',
    '44': u'Loire-Atlantique',
    '45': u'Loiret',
    '46': u'Lot',
    '47': u'Lot-et-Garonne',
    '48': u'Lozère',
    '49': u'Maine-et-Loire',
    '50': u'Manche',
    '51': u'Marne',
    '52': u'Haute-Marne',
    '53': u'Mayenne',
    '54': u'Meurthe-et-Moselle',
    '55': u'Meuse',
    '56': u'Morbihan',
    '57': u'Moselle',
    '58': u'Nièvre',
    '59': u'Nord',
    '60': u'Oise',
    '61': u'Orne',
    '62': u'Pas-de-Calais',
    '63': u'Puy-de-Dôme',
    '64': u'Pyrénées-Atlantiques',
    '65': u'Hautes-Pyrénées',
    '66': u'Pyrénées-Orientales',
    '67': u'Bas-Rhin',
    '68': u'Haut-Rhin',
    '69': u'Rhône',
    '70': u'Haute-Saône',
    '71': u'Saône-et-Loire',
    '72': u'Sarthe',
    '73': u'Savoie',
    '74': u'Haute-Savoie',
    '75': u'Paris',
    '76': u'Seine-Maritime',
    '77': u'Seine-et-Marne',
    '78': u'Yvelines',
    '79': u'Deux-Sèvres',
    '80': u'Somme',
    '81': u'Tarn',
    '82': u'Tarn-et-Garonne',
    '83': u'Var',
    '84': u'Vaucluse',
    '85': u'Vendée',
    '86': u'Vienne',
    '87': u'Haute-Vienne',
    '88': u'Vosges',
    '89': u'Yonne',
    '90': u'Territoire de Belfort',
    '91': u'Essonne',
    '92': u'Hauts-de-Seine',
    '93': u'Seine-Saint-Denis',
    '94': u'Val-de-Marne',
    '95': u'Val-d\'Oise'
    }

RNSA_Manager = None
TIME_CHECK = 21600

class Rnsa_Manager(threading.Thread):
    """ Class with only one instance to check RNSA web site general information"""
    # Decoding vigipollens web site parameters
#    strValidity = u"Carte de vigilance - mise à jour le "
    strValidity = u"Carte de vigilance - mise &agrave; jour le "
#    strURLimg = (u'<div id="info1">', "01.")
    strURLimg = (u'<div id="vigilanceMap">', "01.")
#    urlMap = u"https://www.pollens.fr/generated/vigilance_map.png"
    urlDataDep = u'/risks/thea/counties/'

    def __init__(self, get_config, log, stop):
        threading.Thread.__init__(self)
        self.stop = stop
        self.log = log
        self.get_config = get_config
        self.validityDate = ""
        self.urlVigipollens = ""
        self.urlVigiMap = ""
        self.running = False
        self.log.info(u"Rnsa_Manager initialized")

    def getVigiSource(self, httpsource):
        """
        Load vigipollens web site and extact parameters
        """
        self.log.debug(u"RNSA Manager loading web site source .....")
        try :
            req = urllib.urlopen(httpsource)
            htmltext = req.read().decode("utf-8", "replace")
            req.close()
            self.log.info(u"RNSA Manager loaded web site source : {0}".format(httpsource))
        except urllib.error.URLError as e:
            self.log.error(u"RNSA Manager GET {0}, URLError reason: {1}".format(httpsource, e.reason))
        except urllib.error.HTTPError as e:
            self.log.error(u"RNSA Manager GET {0}, HTTPError code: {1} ({2})".format(httpsource, e.code, e.reason))
        except UnicodeDecodeError as e:
            self.log.error(u"RNSA Manager decoding {0}, Unicode fail: {1} )".format(httpsource, e))
        except :
            self.log.error(u"RNSA Manager GET {0}, Unknown error: {1}".format(httpsource, traceback.format_exc()))
        else :
            locale.setlocale(locale.LC_ALL, '')
#            print(htmltext)
            start = htmltext.find(self.strValidity) + len(self.strValidity)
            end = htmltext.find(u"</u>", start)
            validDate = htmltext[start:end]
            h = HTMLParser()
            validDate = u"{0}".format(h.unescape(validDate))
            year = datetime.now().year
            try :
                Validity = datetime.strptime(u"{0} {1}".format(validDate, year).encode('utf-8'), '%d %B %Y' )
                self.validityDate = Validity.strftime('%Y-%m-%d')
                self.log.info(u"RNSA Manager decode validity date :  {0}".format(self.validityDate))
            except ValueError as e:
                self.log.warning(u"RNSA Manager fail to decode validity date on source : {0}, error is : {1}".format(validDate, e))
                self.validityDate = ""
            try :
                start = htmltext.find(self.strURLimg[0])
                start = htmltext.find(u'<img src="', start + len(self.strURLimg[0]))
                end = htmltext.find(u' alt="', start + len(self.strURLimg[0]))
                self.urlVigiMap = htmltext[start+10:end]
                self.urlVigipollens = u"{0}{1}".format(httpsource, self.urlDataDep)
                self.log.info(u"RNSA Manager decode URL for vigi map : {0}, URI for dep : {1}".format(self.urlVigiMap, self.urlVigipollens))
            except ValueError as e:
                self.log.warning(u"RNSA Manager fail to decode URL for vigi map on source : {0}, error is : {1}".format(self.urlVigiMap, e))
                self.urlVigiMap = ""
                self.urlVigipollens = ""
            return ""
        return "error"

    def getURIDep(self, dep):
        """Return URL for vigilance value from a french departement"""
        if self.urlVigipollens :
            return ("{0}{1}".format(self.urlVigipollens, dep), self.validityDate)
        else :
            return ("", "")

    def run(self):
        """ Get pollens vigilance
        """
        self.running = True
        self._lastUpdate = 0
        self.log.info(u"RNSA Manager start thread to check source web source every 6 hour")
        try :
            while not self.stop.isSet() and self.running:
                if self._lastUpdate + TIME_CHECK < time.time() :
                    if self.getVigiSource(self.get_config("httpsource")) == "" :
                        self._lastUpdate = time.time()
                self.stop.wait(60)
        except :
            self.log.error(u"RNSA Manager thread stopped, error: {0}".format(traceback.format_exc()))
        self.running = False
        self.log.info(u"RNSA Manager stoppe thread to check source web source.")

class VigiRnsaPollens(BaseVigiallergens):
    """ VigiRnsaPollens
    """
    allergensListFr = [u"Cyprès", u"Saule", u"Frêne", u"Peuplier",
                u"Charme",  u"Bouleau", u"Platane", u"Chêne",
                u"Graminées", u"Oseille", u"Urticacées", u"Châtaignier",
                u"Armoise", u"Aulne", u"Noisetier",  u"Plantain",
                u"Olivier", u"Ambroisies", u"Tilleul"
                ]
    allergensListEn = [u"Cypress", u"Willow", u"Ash", u"Poplar",
                u"Charm",  u"Birch", u"Platane", u"Oak",
                u"Gramineae",  u"Sorrel", u"Urticaceae", u"Chestnut",
                u"Armoise", u"Alder", u"Hazelnut", u"Plantain",
                u"Olive", u"Ambrosia", u"Linden"
                ]

    # -------------------------------------------------------------------------------------------------
    def __init__(self, log, send, stop, get_config, directory, device_id, dep, register_thread):
        """ Init VigiRnsaPollens object
            @param log : log instance
            @param send : send
            @param stop : stop flag
            @param device_id : domogik device id
            @param dep : departement ID
        """
        global RNSA_Manager

        BaseVigiallergens.__init__(self, log, send, stop, device_id)
        self.dep = dep
        self.nbAllergen = len(self.allergensListFr)
        if RNSA_Manager is None :
            # Start only one RNSA_Manager
            RNSA_Manager = Rnsa_Manager(get_config, log, stop)
            RNSA_Manager.start()
            register_thread(RNSA_Manager)
            self._stop.wait(2)
        self.getURIDep = RNSA_Manager.getURIDep

    # -------------------------------------------------------------------------------------------------
    def setParams(self, dep):
        if self.dep != dep :
            self.log.info(u"Device {0} updated departement '{1}' to '{2}'".format(self.device_id, self.dep, dep))
            self.dep = dep
            self._lastUpdate = 0

    def check(self):
        """ Get pollens vigilance
        """
        self.run = True
        self._lastUpdate = 0
        self.log.info(u"Start to check allergens vigilance for departement '{0}'".format(self.dep))
        try :
            while not self._stop.isSet() and self.run:
                if self._lastUpdate + TIME_CHECK < time.time() :
                    self.log.debug(u"Get allergens vigilance for {0} 'departement'".format(self.dep))
                    pollensVigi = self.getVigilance()
                    print(pollensVigi)

                    if pollensVigi != "error":
                        self._send(self.device_id, self.dep, pollensVigi)
                    else:
                        self.log.error(u"Error getting allergens vigilance for departement' {0}".format(self.dep))
                    self._lastUpdate = time.time()

                self._stop.wait(60)
        except :
            self.log.error(u"Check device {0} error: {1}".format(self.device_id, (traceback.format_exc())))
        self.run = False
        self.log.info(u"Stopped allergens vigilance checking for {0} 'departement'".format(self.dep))

    # -------------------------------------------------------------------------------------------------
    def getVigilance(self):
        """ Get vigilance image and decode it """
        uri, validityDate = self.getURIDep(self.dep)
        if not uri :
            self.log.warning(u"Device can't retrieve data from Vigipollens web site")
            return "error"
        try:
            result = requests.get(uri).json()
            self.log.info(u"Device loaded web site source : {0}".format(uri))
        except requests.exceptions.ConnectionError as e:
            self.log.error(u"Device GET {0}, URLError reason: %s" % (uri, e.reason))
            return "error"
        except requests.exceptions.HTTPError as e:
            self.log.error(u"Device GET {0}, HTTPError code: {1} , reason : {2}" % (uri, e.code, e.reason))
            return "error"
        except requests.exceptions.Timeout as e:
            self.log.error(u"Device GET {0}, Timeout code: {1} , reason : {2}" % (uri, e.code, e.reason))
            return "error"
        except UnicodeDecodeError as e:
            self.log.error(u"Device decoding {0}, Unicode fail: {1} )".format(uri, e))
            return "error"
        except:
            self.log.error(u"### Retrieve RNSA vigilance GET '{0}', Unknown error: {1}".format(uri, (traceback.format_exc())))
            return "error"
        try:
            pollensVigi = {"Departement" : self.dep, "ValidityReport" : validityDate, "MaxDepartementLevel" : result["riskLevel"]}
            for item in result['risks']:
                if item["pollenName"] in self.allergensListFr :
                    if  item["level"] >= 0 and  item["level"] <= 5 :
                        self.log.debug(u"Allergen {0} identified at level {1}".format( item["pollenName"], item["level"]))
                        level = item["level"]
                    else :
                        self.log.warning(u"Allergen {0} identified with unknown level {1} (setting level=0)".format( item["pollenName"], item["level"]))
                        level = 0
                    id = self.allergensListFr.index(item["pollenName"])
                    pollensVigi["Allergen{0}".format(self.allergensListEn[id])] = level
        except:
            self.log.error(u"### Retrieve RNSA vigilance decoding '{0}', error: {1}".format(result, (traceback.format_exc())))
            return "error"
        return pollensVigi
