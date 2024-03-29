import os
import platform
import json
import requests
import arcpy


mxd = arcpy.mapping.MapDocument("CURRENT")
dirname = os.path.dirname(mxd.filePath)

connection_folder = os.path.join(dirname, 'Connections')
if not os.path.isdir(connection_folder):
    os.mkdir(connection_folder)
connection_out_name = 'connection_server.ags'
connection_full_path = os.path.join(connection_folder,connection_out_name)
arcpy.AddMessage("Input parameters: ")
version_folder = os.path.join(dirname, 'Versions')
if not os.path.isdir(version_folder):
    os.mkdir(version_folder)
version_names = arcpy.GetParameter(0)
arcpy.AddMessage(version_names)
arcpy.AddMessage("Config file: " + arcpy.GetParameterAsText(1))
system_name = platform.node()
adminConn = arcpy.env.workspace


# Validations
workspace_description = arcpy.Describe(arcpy.env.workspace)
if workspace_description.workspaceType != u'RemoteDatabase':
    arcpy.AddError("Error: Current workspace need to be a RemoteDatabase")
    raise
if workspace_description.connectionProperties.instance.find("postgresql:localhost") < 0:
    arcpy.AddError("Error: Current workspace need to be a Postgresql database running in localhost")
    raise
if workspace_description.connectionProperties.user != u'sde':
    arcpy.AddError("Error: Current workspace need to be in sde user")
    raise    
if workspace_description.connectionProperties.version != u'sde.DEFAULT':
    arcpy.AddError("Error: Current workspace need to be in default version")
    raise

versionList = arcpy.ListVersions(adminConn)
for version_name in version_names:
    full_version_name = "sde." + version_name
    try:
        versionList.index(full_version_name)
    except ValueError as e:
       arcpy.AddError(version_name + " version doesn't exist")
       raise

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
            try:
                arcpy.RemoveDataStoreItem(connection_full_path,"DATABASE",version_name)
            except Exception as e:
                arcpy.AddError("Error removing Data Store item " + connection_full_path)
                arcpy.AddError(e)
            db_connection_file = version_name + "@" + db_name + ".sde"
            db_connection_full_path = os.path.join(connection_folder,db_connection_file)
            versionedMapDocumentPath = os.path.join(version_folder, db_name + "_" + version_name + ".mxd")
            versionedServiceDraftPath = os.path.join(version_folder, db_name + "_" + version_name + ".sddraft")
            versionedServiceSdPath = os.path.join(version_folder, db_name + "_" + version_name + ".sd")
            try:
                if os.path.exists(db_connection_full_path):
                    os.remove(db_connection_full_path)
            except Exception as e:
                arcpy.AddError("Error deleting db connection file " + db_connection_full_path)
                arcpy.AddError(e)
            try:                
                if os.path.exists(versionedMapDocumentPath):
                    os.remove(versionedMapDocumentPath)
            except Exception as e:
                arcpy.AddError("Error deleting versioned map document " + versionedMapDocumentPath)
                arcpy.AddError(e) 
            try:                
                if os.path.exists(versionedServiceDraftPath):
                    os.remove(versionedServiceDraftPath)        
            except Exception as e:
                arcpy.AddError("Error deleting service draft " + versionedServiceDraftPath)
                arcpy.AddError(e)     
            try:             
                if os.path.exists(versionedServiceSdPath):
                    os.remove(versionedServiceSdPath)
            except Exception as e:
                arcpy.AddError("Error deleting service definition " + versionedServiceSdPath)
                arcpy.AddError(e) 
            try:    
                arcpy.DisconnectUser(adminConn, "ALL")    
                arcpy.management.DeleteVersion(arcpy.env.workspace, version_name)
                arcpy.AddMessage("Deleted service " + version_name)
                arcpy.AcceptConnections(adminConn, True)
            except Exception as e:
                arcpy.AddError("Error deleting version " + version_name)
                arcpy.AddError(e)                 
        else:
            arcpy.AddError("Error deleting " + version_name + " status code "+ str(status))

with open(arcpy.GetParameterAsText(1)) as f:
    config = json.load(f)
    process(config)



