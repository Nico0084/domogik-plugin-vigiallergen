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

import time
import urllib
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
    allergenLevels = {"#ffffff": 0, '#74e46c': 1, "#048000": 2, "#f2ea1a": 3, "#ff7f29": 4, "#ff0200": 5}

    # -------------------------------------------------------------------------------------------------
    def __init__(self, log, send, stop, getURIDep, directory, device_id, dep):
        """ Init VigiRnsaPollens object
            @param log : log instance
            @param send : send
            @param stop : stop flag
            @param device_id : domogik device id
            @param dep : departement ID
        """
        BaseVigiallergens.__init__(self, log, send, stop, device_id)
        self.dep = dep
        self.getURIDep = getURIDep
        self.nbAllergen = len(self.allergensListFr)

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
                if self._lastUpdate + 3600 < time.time() :
                    self.log.debug(u"Get allergens vigilance for {0} 'departement'".format(self.dep))
                    pollensVigi = self.getVigilance()
                    print(pollensVigi)

                    if pollensVigi != "error":
                        self._send(self.device_id, self.dep, pollensVigi)
                    else:
                        self.log.error(u"Error getting allergens vigilance for departement' {0}".format(self.dep))
                    self._lastUpdate = time.time()

                self._stop.wait(1)
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
            req = urllib.urlopen(uri)
            htmltext = req.read().decode("utf-8", "replace")
            req.close()
            self.log.info(u"Device loaded web site source : {0}".format(uri))
        except urllib.error.URLError as e:
            self.log.error(u"Device GET {0}, URLError reason: %s" % (uri, e.reason))
            return "error"
        except urllib.error.HTTPError as e:
            self.log.error(u"Device GET {0}, HTTPError code: {1} , reason : {2}" % (uri, e.code, e.reason))
            return "error"
        except UnicodeDecodeError as e:
            self.log.error(u"Device decoding {0}, Unicode fail: {1} )".format(uri, e))
            return "error"
        except:
            self.log.error(u"### API GET '%s', Unknown error: '%s'" % (uri, (traceback.format_exc())))
            return "error"

#        print(htmltext)
        vigiLevelMax = 0
        pollensVigi = {"Departement" : self.dep, "ValidityReport" : validityDate}
        start = htmltext.find(DEPARTMENTS[self.dep])
        end = htmltext.find('</b></center>', start)
#        print(u"++++ departement : {0}".format(htmltext[start:end]))
        startName = end
        startVigi = end
        while startName != -1 :
            startName = htmltext.find('<tspan x="80" dx="0" text-anchor="end"', startName)
            startName = htmltext.find(';">', startName) + 3
            endName = htmltext.find('</tspan>', startName)
            allergName = htmltext[startName:endName].strip()
            startVigi = htmltext.find('style="fill: ', startVigi) + 13
            endVigi = htmltext.find('; stroke:', startVigi)
            allergVigi = htmltext[startVigi:endVigi].lower()
#            print(u"****** Allergen Name find {0} to {1} : {2}={3}".format(startName, endName, allergName, allergVigi))
            if allergName in self.allergensListFr :
                if allergVigi in self.allergenLevels :
                    self.log.debug(u"Allergen {0} identified at level {1}".format(allergName, self.allergenLevels[allergVigi]))
                    level = self.allergenLevels[allergVigi]
                else :
                    self.log.warning(u"Allergen {0} identified with unknown level {1} (setting level=0)".format(allergName, allergVigi))
                    level = 0
                id = self.allergensListFr.index(allergName)
                if level > vigiLevelMax:
                    vigiLevelMax = level
                    pollensVigi["MaxDepartementLevel"] = level
                pollensVigi["Allergen{0}".format(self.allergensListEn[id])] = level
            startName = htmltext.find('<tspan x="80" dx="0" text-anchor="end"', endName)
            startVigi = endVigi
#            print(startName, startVigi,  htmlLen)
        return pollensVigi
