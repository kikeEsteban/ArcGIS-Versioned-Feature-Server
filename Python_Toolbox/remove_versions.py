import os
import platform
import json
import requests
import arcpy

workspace_description = arcpy.Describe(arcpy.env.workspace)
if workspace_description.workspaceType != u'RemoteDatabase':
    arcpy.AddError("Error: Current workspace need to be a RemoteDatabase")
    exit()
if workspace_description.connectionProperties.instance != u'sde:postgresql:localhost':
    arcpy.AddError("Error: Current workspace need to be sde connection to a Postgresql running in localhost")
    exit()

# Other check: Only one dataset and the dataset must be versioned
# This way, the database name and the dataset can be got from map config
# Also check that current version is "default"

dirname = os.path.dirname(__file__)
connection_folder = os.path.join(dirname, 'Connections')
connection_out_name = 'connection_server.ags'
connection_full_path = os.path.join(connection_folder,connection_out_name)
arcpy.AddMessage("Input parameters: ")
version_folder = os.path.join(dirname, 'Versions')
version_names = arcpy.GetParameter(0)
arcpy.AddMessage(version_names)
arcpy.AddMessage("Config file: " + arcpy.GetParameterAsText(1))
system_name = platform.node()

def gentoken(username, password, expiration=60):
    query_dict = {'username':   username,
                  'password':   password,
                  'expiration': str(expiration),
                  'client': 'requestip',
                  'f': 'json'}
    token_url = "https://{}:6443/arcgis/admin/generateToken".format(system_name)
    response = requests.post(token_url, data = query_dict, verify = False)
    return json.loads(response.text)["token"]

def delete_service(db_name, version_name, token):
    query_dict = {'f': 'json'}
    delete_url = "https://{}:6443/arcgis/admin/services/{}/{}.MapServer/delete?token={}".format(system_name,db_name,version_name,token)
    response = requests.post(delete_url, data = query_dict, verify = False)
    return response.status_code

def process(config):
    db_name = config["db_name"]
    server_publisher_name = config["server_publisher_name"]
    server_publisher_password = config["server_publisher_password"]
    token = gentoken(server_publisher_name, server_publisher_password)
    for version_name in version_names:
        arcpy.AddMessage("Deleting " + version_name)
        status = delete_service(db_name, version_name, token)
        if status==200:
            arcpy.RemoveDataStoreItem(connection_full_path,"DATABASE",version_name)
            db_connection_file = version_name + "@" + db_name + ".sde"
            db_connection_full_path = os.path.join(connection_folder,db_connection_file)
            if os.path.exists(db_connection_full_path):
                os.remove(db_connection_full_path)
            versionedMapDocumentPath = os.path.join(version_folder, db_name + "_" + version_name + ".mxd")
            if os.path.exists(versionedMapDocumentPath):
                os.remove(versionedMapDocumentPath)
            versionedServiceDraftPath = os.path.join(version_folder, db_name + "_" + version_name + ".sddraft")
            if os.path.exists(versionedServiceDraftPath):
                os.remove(versionedServiceDraftPath)        
            versionedServiceSdPath = os.path.join(version_folder, db_name + "_" + version_name + ".sd")
            if os.path.exists(versionedServiceSdPath):
                os.remove(versionedServiceSdPath)                 
            arcpy.management.DeleteVersion(arcpy.env.workspace, version_name)
            arcpy.AddMessage("Deleted service " + version_name)
        else:
            arcpy.AddError("Error deleting " + version_name + " status code "+ str(status))

with open(arcpy.GetParameterAsText(1)) as f:
    config = json.load(f)
    process(config)



