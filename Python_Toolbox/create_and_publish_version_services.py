import os
import platform
import arcpy
import json
import time
import xml.dom.minidom as DOM 

workspace_description = arcpy.Describe(arcpy.env.workspace)
if workspace_description.workspaceType != u'RemoteDatabase':
    arcpy.AddError("Error: Current workspace need to be a RemoteDatabase")
    exit()
if workspace_description.connectionProperties.instance.find("postgresql:localhost") < 0:
    arcpy.AddError("Error: Current workspace need to be a Postgresql database running in localhost")
    exit()
if workspace_description.connectionProperties.user != u'sde':
    arcpy.AddError("Error: Current workspace need to be in sde user")
    exit()    
if workspace_description.connectionProperties.version != u'sde.DEFAULT':
    arcpy.AddError("Error: Current workspace need to be in default version")
    exit()

mxd = arcpy.mapping.MapDocument("CURRENT")
map_layers = arcpy.mapping.ListLayers(mxd)
for layer in map_layers:
    if not layer.isFeatureLayer:
        arcpy.AddError("Error: All layers in the map need to be FeatureLayers")
        exit() 

dirname = os.path.dirname(__file__)
connection_folder = os.path.join(dirname, 'Connections')
connection_out_name = 'connection_server.ags'
connection_full_path = os.path.join(connection_folder,connection_out_name)
arcpy.AddMessage("Connection file: " + connection_full_path)
version_folder = os.path.join(dirname, 'Versions')
arcpy.AddMessage("Version folder: " + version_folder)
system_name = platform.node()
server_url = 'https://{}:6443/arcgis/admin/'.format(system_name)
db_instance = "localhost"
arcpy.AddMessage("Server URL: " + server_url)
arcpy.AddMessage("DB Instance: " + db_instance)
arcpy.AddMessage("Input parameters: ")
version_names = arcpy.GetParameter(0)
arcpy.AddMessage(version_names)
arcpy.AddMessage("Config file: " + arcpy.GetParameterAsText(1))

adminConn = arcpy.env.workspace
versionList = arcpy.ListVersions(adminConn)
for version_name in version_names:
    full_version_name = "sde." + version_name
    try:
        if versionList.index(full_version_name) >= 0:
            arcpy.AddError(version_name + " version already exists")
            exit(-1)
    except ValueError as e:
        pass


def configure_service_draft(doc):
    type_names = doc.getElementsByTagName('TypeName')
    for type_name in type_names:
        if type_name.firstChild.data == "FeatureServer":
            type_name.parentNode.getElementsByTagName("Enabled")[0].firstChild.data = "true"
        if type_name.firstChild.data == "KmlServer":
            type_name.parentNode.getElementsByTagName("Enabled")[0].firstChild.data = "false"

def create_version(version_name, db_name, db_sde_password):
    db_connection_file = version_name + "@" + db_name + ".sde"
    db_connection_full_path = os.path.join(connection_folder,db_connection_file)
    full_version_name = "sde." + version_name
    parentVersion = "sde.DEFAULT"
    summary = 'Editable version of ' + db_name + ' with name ' + version_name
    tags = 'EEG, TFM, Esri, ArcGIS Server, Postgresql' 
    arcpy.AddMessage("Process " + full_version_name)
    arcpy.AddMessage("Step 1: Generating version: " + full_version_name)
    arcpy.CreateVersion_management(arcpy.env.workspace, parentVersion, version_name, "PUBLIC")
    arcpy.ChangeVersion_management('geofences','TRANSACTIONAL', full_version_name,'')
    arcpy.ChangeVersion_management('pois','TRANSACTIONAL', full_version_name,'')
    time.sleep(2)
    arcpy.AddMessage("Step 2: Create database connection file: " + db_connection_file)
    arcpy.management.CreateDatabaseConnection(
        connection_folder, 
        db_connection_file, 
        "POSTGRESQL", 
        "localhost", 
        "DATABASE_AUTH", 
        'sde', 
        db_sde_password, 
        True, 
        db_name, 
        None, 
        "TRANSACTIONAL", 
        full_version_name)
    arcpy.AddMessage("Step 3: Register source in ArcGIS Server " + db_connection_file)
    arcpy.AddDataStoreItem(connection_full_path, "DATABASE", version_name, db_connection_full_path, db_connection_full_path)
    versionedMapDocumentPath = os.path.join(version_folder, db_name + "_" + version_name + ".mxd")
    versionedServiceDraftPath = os.path.join(version_folder, db_name + "_" + version_name + ".sddraft")
    versionedServiceSdPath = os.path.join(version_folder, db_name + "_" + version_name + ".sd")
    arcpy.AddMessage("Step 4: Saving map document version")
    mxd = arcpy.mapping.MapDocument("CURRENT")
    mxd.saveACopy(versionedMapDocumentPath)
    mxdVersioned = arcpy.mapping.MapDocument(versionedMapDocumentPath)
    arcpy.AddMessage("Step 5: Generate service draft")
    analysis = arcpy.mapping.CreateMapSDDraft(mxdVersioned, versionedServiceDraftPath, version_name, 'ARCGIS_SERVER', 
                                            connection_full_path, True, db_name, summary, tags)
    draft_errors = False
    if analysis['errors'] == {}:
        # Open and inspect sddraft
        doc = DOM.parse(versionedServiceDraftPath)
        with open(versionedServiceDraftPath, 'w+') as xml:
            configure_service_draft(doc)
            doc.writexml(xml)
        # Execute StageService
        analysis = arcpy.mapping.AnalyzeForSD(versionedServiceDraftPath)
        if analysis['errors'] == {}:
            arcpy.AddMessage("Step 6: Generate service definition")
            arcpy.StageService_server(versionedServiceDraftPath, versionedServiceSdPath)
            arcpy.AddMessage("Step 7: Upload service definition")
            arcpy.UploadServiceDefinition_server(versionedServiceSdPath, connection_full_path)
        else:
            draft_errors = True 
    else: 
        draft_errors = True
    # Restore versions and workspace to sde 
    arcpy.AddMessage("Step 8: Restore default version in current map")
    for layer in map_layers:
        arcpy.ChangeVersion_management(layer.name,'TRANSACTIONAL', parentVersion,'')
    time.sleep(3)
    if draft_errors:
        arcpy.AddError(analysis['errors'])

def process(config):
    db_name = config["db_name"]
    db_sde_password = config["db_sde_password"]
    server_publisher_name = config["server_publisher_name"]
    server_publisher_password = config["server_publisher_password"]
    arcpy.AddMessage("db_name: " + db_name)
    if workspace_description.connectionProperties.database != db_name:
        arcpy.AddError("Error: Current workspace need to be a connected to target DB")
        exit()
    arcpy.AddMessage("Preparing GIS Server connection file")
    if os.path.exists(connection_full_path):
        os.remove(connection_full_path)
    arcpy.mapping.CreateGISServerConnectionFile("ADMINISTER_GIS_SERVICES",
        connection_folder,
        connection_out_name,
        server_url,
        "ARCGIS_SERVER",
        True,
        version_folder,
        server_publisher_name,
        server_publisher_password,
        "SAVE_USERNAME")
    for version_name in version_names:
        create_version(version_name,db_name,db_sde_password)

with open(arcpy.GetParameterAsText(1)) as f:
    config = json.load(f)
    process(config)















