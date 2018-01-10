#!/usr/bin/python

import requests
from bs4 import BeautifulSoup as BS
import json
import MySQLdb
import datetime
import sys

#suppress Requests warning
requests.packages.urllib3.disable_warnings()

def login():
        a=MySQLdb.connect(host="localhost",
                                port=3306,
                                user="<mysql user>",
                                password="<mysql password>",
                                db="<db name>")
        x=a.cursor()
        x.execute("SELECT * FROM auth")
        z=x.fetchone()
        #print z[0]
        if z[0] > datetime.datetime.today()-datetime.timedelta(hours=24):
                #get new auth token
                print "need new auth token"
                r=requests.post("https://<splunk api server>/services/auth/login",data={'username':'<username>','password':'<password>'},verify=False)
                print r.text
                soup=BS(r.text,"html.parser")
                sessionkey=(soup.find("sessionkey").text)
                b=a.cursor()
                b.execute("DELETE FROM auth")
                a.commit()
                b.execute("INSERT INTO auth (time,sessiontoken) VALUES (now(),'"+sessionkey+"')")
                a.commit()
                a.close()
                return sessionkey
        else:
                #print "Token is fresh!"
                a.close()
                return z[1]

def create_search(auth_header,search):
        r=requests.post("https://<splunk api server>/services/search/jobs",headers=auth_header,data={"search":search},verify=False)
        #print r.headers
        #print r.text
        search_response=BS(r.text,"html.parser")
        return search_response.find("sid").text

def check_status(auth_header,search_id):
        r=requests.get("https://<splunk api server>/services/search/jobs/"+search_id, headers=auth_header,verify=False)
        #print r.headers
        #print r.text
        if r.status_code == 200:
                import xmltodict
                tree=xmltodict.parse(r.text)
                #print tree
                #print tree['entry']['content']['s:dict']['s:key'][19]['#text']
                #return tree['entry']['content']['s:dict']['s:key'][19]['#text']
                i=0
                for key in tree['entry']['content']['s:dict']['s:key']:
                        if tree['entry']['content']['s:dict']['s:key'][i]['@name']=="isDone":
                                break
                        else:
                                i=i+1
                #print tree['entry']['content']['s:dict']['s:key'][i]['#text']
                return tree['entry']['content']['s:dict']['s:key'][i]['#text']

def get_results(auth_header,search_id):
        r=requests.get("https://<splunk api server>/services/search/jobs/"+search_id+"/results/",data="output_mode=json",headers=auth_header,verify=False)
        #print r.text
        #import json
        #j=json.loads(r.text)
        #print json.dumps(j,indent=4)
        #print "Result count is: "+str(len(j['results']))
        #return j
        return r.text

def sqlify(results):
        j=json.loads(results)
        count=j['results'][0]['Total']
        #print "The count is: "+count
        conn=MySQLdb.connect(host="localhost",
                                port=3306,
                                passwd="<mysql username>",
                                user="<mysql password>",
                                db="<db name>")

        x=conn.cursor()
        x.execute("INSERT INTO bad_logins(time,bad_logins) VALUES (now(),"+count+")")
        conn.commit()
        conn.close()
