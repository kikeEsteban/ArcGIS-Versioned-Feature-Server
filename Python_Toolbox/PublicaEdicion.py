"""
NuevaEdicion.py:
Crea una nueva versión del la geodatabase y la publica como servicio con ArcGIS server
Referencia: https://desktop.arcgis.com/es/arcmap/latest/map/publish-map-services/publishing-a-map-service-with-python.htm 
"""

#Import modules
import arcpy
import os

sdeWorkspace = r"C:\Users\autok\AppData\Roaming\ESRI\Desktop10.8\ArcCatalog\sde@geofences_and_pois.sde"
editorWorkspace = r"C:\Users\autok\AppData\Roaming\ESRI\Desktop10.8\ArcCatalog\dataeditor@geofences_and_pois.sde"
versionedMxdFolder =  r"C:\EsriTraining\MasterGisOnline\Proyecto_Final_de_Master\proyecto\Versions"
con = r'C:\EsriTraining\MasterGisOnline\Proyecto_Final_de_Master\proyecto\Connections\connection_server.ags'
rootMxdName = "geofences_and_pois"
parentVersion = "sde.DEFAULT"

versionName = arcpy.GetParameterAsText(0)
arcpy.AddMessage("Version name: " + versionName)

# Save mxd document with target version and workspace
mxd = arcpy.mapping.MapDocument("CURRENT")

# Create service and publish it
service = rootMxdName + "_WFST_" + versionName
versionedServiceDraftPath = os.path.join(versionedMxdFolder, service + ".sddraft")
versionedServiceSdPath = os.path.join(versionedMxdFolder, service + ".sd")
summary = 'Editable version of Geofences and Pois with name ' + versionName
tags = 'TFM, EEG'

versionedMapDocumentPath = os.path.join(versionedMxdFolder, rootMxdName + "_" + versionName + ".mxd")

mxdVersioned = arcpy.mapping.MapDocument(versionedMapDocumentPath)
# create service definition draft
analysis = arcpy.mapping.CreateMapSDDraft(mxdVersioned, versionedServiceDraftPath, service, 'ARCGIS_SERVER', 
                                          con, True, None, summary, tags)
# stage and upload the service if the sddraft analysis did not contain errors
if analysis['errors'] == {}:
    # Execute StageService
    arcpy.StageService_server(versionedServiceDraftPath, versionedServiceSdPath)
    # Execute UploadServiceDefinition
    arcpy.UploadServiceDefinition_server(versionedServiceSdPath, con)
else: 
    # if the sddraft analysis contained errors, display them
    print(analysis['errors'])



# Restore versions and workspace to sde 
"""
arcpy.ChangeVersion_management('geofences','TRANSACTIONAL', parentVersion,'')
arcpy.ChangeVersion_management('pois','TRANSACTIONAL', parentVersion,'')
arcpy.env.workspace = sdeWorkspace
"""

