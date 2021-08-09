#!/usr/bin/env python

import configparser
#from configparser import SafeConfigParser # # pip3 install ConfigParser
#import cfgparse #pip3 install cfgparse
import re
class configVar:
    # Base SQL statement from which others are derived
    def __init__(self, configFile):


        self.parser = configparser.SafeConfigParser()
        #config.read('archive.ini')
        #self.parser = SafeConfigParser()
        self.parser.read(configFile)
        self.parser.configFile=configFile

        #self.cfgparse=cfgparse.ConfigParser()
        #self.cfgparse.add_file(configFile)
        #self.cfgopts=self.cfgparse.parse()

    def setItem(self, configItem, configValue, section='SETTINGS'):
        #if configValue.isnumeric():
        #print("%s = %s, %s" % (configItem, configValue, section))
        self.parser.set(section, configItem, str(configValue))
        self.saveAll()
        #else:
        #    self.parser.set('SETTINGS', configItem, bytes([configValue]))
        #return self.parser.set('SETTINGS', configItem, bytes([configValue]))

    def onItemChange(self, event, section='SETTINGS'):
        return self.parser.set(section, configItem, configValue)

    def getItem(self, configItem, section='SETTINGS'):
        
        retValue = ""
        try:
            retValue=str(self.parser.get(section, configItem))
        except:
            retValue=''
        
        return retValue

    def getBoolean(self, configItem, section='SETTINGS'):
        
        retValue = ""
        try:
            retValue=bool(self.parser.getboolean(section, configItem))
        except:
            retValue=False
        
        return retValue

    def saveItem(self, configItem):
        pass
    
    def saveAll(self):
        # Writing out configuration file to 'configfile.conf'
        #print (self.parser.configFile)
        #print (self.parser)
        #for key in self.parser['SETTINGS']: print("%s = %s" % (key, self.parser['SETTINGS'][key]))
        with open(self.parser.configFile, 'w') as configfile:
            self.parser.write(configfile)
    