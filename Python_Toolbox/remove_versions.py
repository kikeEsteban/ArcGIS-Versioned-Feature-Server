import os
import platform
import json
import urllib
import urllib2
import ssl
import arcpy


"""
Get token: 
https://desktop-bhfu9l0:6443/arcgis/admin/generateToken
To delete
https://desktop-bhfu9l0:6443/arcgis/admin/services/<db_name>/<version_name>.MapServer/delete
"""


arcpy.AddMessage("Input parameters: ")
version_names = arcpy.GetParameter(0)
arcpy.AddMessage(version_names)
arcpy.AddMessage("Config file: " + arcpy.GetParameterAsText(1))
system_name = platform.node()
server_url = "https://desktop-bhfu9l0:6443/arcgis/admin/"

def gentoken(url, username, password, expiration=60):
    query_dict = {'username':   username,
                  'password':   password,
                  'expiration': str(expiration),
                  'client': 'requestip'}
    query_string = urllib.urlencode(query_dict)
    arcpy.AddMessage("Token URL " + url + "?f=json&" + query_string)
    req = urllib2.Request(url + "?f=json&" + query_string, headers={'User-Agent':'Mozilla/5.0'})
    gcontext = ssl.SSLContext()  # Only for gangstars
    return urllib2.urlopen(req, context=gcontext).read()

def deleteservice(server, servicename, username, password, token=None, port=6080):
    if token is None:
        token_url = "{}generateToken".format(server_url)
        token = gentoken(token_url, username, password)
    delete_service_url = "http://{}:{}/arcgis/admin/services/{}/delete?token={}".format(server, port, servicename, token)
    urllib2.urlopen(delete_service_url, ' ').read() # The ' ' forces POST

def process(config):
    db_name = config["db_name"]
    db_sde_password = config["db_sde_password"]
    server_publisher_name = config["server_publisher_name"]
    server_publisher_password = config["server_publisher_password"]
    token_url = "{}generateToken".format(server_url)
    token = gentoken(token_url, server_publisher_name, server_publisher_password)
    arcpy.AddMessage("Generated token: " + token)

with open(arcpy.GetParameterAsText(1)) as f:
    config = json.load(f)
    process(config)


# if you need a token, execute this line:
#deleteservice("<server>", "<service>.MapServer", "<admin username>", "<admin password>")

# if you already have a token, execute this line:
#deleteservice("<server>", "<service>.MapServer", None, None, token='<token string>')