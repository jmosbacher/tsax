##################################################################################################################
#              
#                                        Slow Control Class for the new Webservice 
#                                           (see its wiki page for more info)
#                        
#           Returns information from Historian Database in json Format         
#                                                                               
# Author: Alfio Rizzo (alfio.rizzo@columbia.edu) 
#           (for the Slow Control Group)
# Date: Fri Mar 10 16:11:46 CET 2017 
#
#  Example Usage:
#       import xe1tscwebapi as sc
#       mysc = sc.xe1tscwebapi()
#        
#       # You need to be authorized in order to get data
#       # You should use your username and password if you don't have the token or if you need to get the token
#       # (you can use the getpass module to pass password safely) via this method 
#       mysc.AuthUser('username','password')   
#                                            
#       # Then call this method to get the token 
#       mysc.GetToken()                         
#       
#       # Alternatively, if you have already a token, 
#       # you can use it to get the authorization without 
#       # the need of username,passord with this method
#       mysc.AuthToken('token')   
#       
#       # You create then a dictionary depending on the query you want to use, 
#       # to get data in a timestamp, last data value or pmt last value.
#       # If you want to get for instance SC Data, do: 
#       query = {'name':'XE1T.CRY_PT103_PCHAMBER_AI.PI',
#                'QueryType':'lab',
#                'StartDateUnix':'1483056000',
#                'EndDateUnix':'1483056900',
#                'Interval':'5'
#               }
#       # The 'StartDateUnix' and 'EndDateUnix' can be replaced by
#       # 'StartDateLNGS':'YYYY-MM-DD HH:MM:SS' , 'EndDateLNGS':'YYYY-MM-DD HH:MM:SS'  if you want to specify LNGS time or by
#       # 'StartDateUTC':'YYYY-MM-DD HH:MM:SS' , 'EndDateUTC':'YYYY-MM-DD HH:MM:SS'  if you want to specify UTC time  
#        
#       # Then set the query
#       mysc.SetQuery(query)
#       
#       # Now you are able to get the data in json format with this method for instance
#       mydata = mysc.GetSCData()
#
#       #Then you can loop over the json object or make a plot
#       for item in mydata:
#           print (item['timestampseconds'],item['value']
#       # The timestamp is always in Unix format, you can of course translate it the timezone you prefer    
#
#       # The other two methods to get data are
#       mydata = mysc.GetSCLastValue()  # to get the last measured value and
#       
#       mydata = mysc.GetLastMeasuredPMTValues() # to get the last parameters of the PMT
#
###########################################################################################################################


import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from datetime import datetime
import pytz
import sys

class xe1tscwebapi:
    def __init__(self):
        Mainurl = 'https://172.16.2.105:5544/'
        self.urlLogin = Mainurl+'Login'
        self.urlData = Mainurl+'GetSCData'
        self.urlLValue = Mainurl+'GetSCLastValue'
        self.urlLPmt= Mainurl+'GetLastMeasuredPMTValues'
        self.query = {}
        self.login = {}
        self.token = ''        
        self.headers = {}
        
    
    def AuthUser(self,username,password):
        self.login['username']=username
        self.login['password']=password
        try:
            r = requests.post(self.urlLogin,data=self.login,verify=False) 
            r.raise_for_status()   
        except requests.exceptions.HTTPError:
            print ('\nError : '+str(r.json()['Message']))
            sys.exit()
        self.token = r.json()['token']
        self.headers['Authorization']=self.token
        
    def GetToken(self):
        return self.token

    def AuthToken(self,token):
        self.token = token
        self.headers['Authorization']=self.token


    def SetQuery(self,query):
        try:
            self.query['name'] = query['name']
        except:
            pass
        
        try:
            self.query['QueryType'] = query['QueryType']
            self.query['Interval'] = query['Interval']
        except:
            pass

        unix_epoch = datetime(1970, 1, 1)
        try:
            self.query['StartDateUnix'] = query['StartDateUnix']
        except:
            pass

        try:
            self.query['EndDateUnix'] = query['EndDateUnix']
        except:
            pass


        try:         
            sdate = datetime.strptime(query['StartDateLNGS'],"%Y-%m-%d %H:%M:%S")
            slngs = pytz.timezone('Europe/Rome').localize(sdate) 
            sutcoffset = slngs.utcoffset().total_seconds()
            self.query['StartDateUnix']=str( int((sdate - unix_epoch).total_seconds() - sutcoffset) )
        except:
            pass
        try:
            sdate = datetime.strptime(query['StartDateUTC'],"%Y-%m-%d %H:%M:%S")
            self.query['StartDateUnix']=str( int((sdate - unix_epoch).total_seconds() ) ) 
        except:
            pass
        
        try:         
            edate = datetime.strptime(query['EndDateLNGS'],"%Y-%m-%d %H:%M:%S")
            elngs = pytz.timezone('Europe/Rome').localize(edate) 
            eutcoffset = elngs.utcoffset().total_seconds()
            self.query['EndDateUnix']=str( int((edate - unix_epoch).total_seconds() - eutcoffset) )
        except:
            pass

        try:
            edate = datetime.strptime(query['EndDateUTC'],"%Y-%m-%d %H:%M:%S")
            self.query['EndDateUnix']=str( int((edate - unix_epoch).total_seconds() ) )  
        except:
            pass

         
        

    def _Request(self,url):
        if (self.token ==''):
            print ('\nError: No authentication method (passord or token) found, please authenticate yourself before to get any data.')
            sys.exit()
        try:
            r = requests.get(url,params=self.query,headers=self.headers,verify=False)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print ('\nError. Status code ' + str(e.response.status_code) + ".")
            sys.exit()
        return r.json()
      
           
                
    def GetSCData(self):
        return self._Request(self.urlData)     
        
        
    def GetSCLastValue(self):
        return self._Request(self.urlLValue)
           

    def GetLastMeasuredPMTValues(self):
        return self._Request(self.urlLPmt)
        
        

