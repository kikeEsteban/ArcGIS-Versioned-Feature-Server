"""
NuevaEdicion.py:
Crea una nueva versión del la geodatabase y la publica como servicio con ArcGIS server
Referencia: https://desktop.arcgis.com/es/arcmap/latest/map/publish-map-services/publishing-a-map-service-with-python.htm 
"""

#Import modules
import arcpy
import os
import xml.dom.minidom as DOM 
import time

sdeWorkspace = r"C:\Users\autok\AppData\Roaming\ESRI\Desktop10.8\ArcCatalog\sde@geofences_and_pois.sde"
versionedMxdFolder =  r"C:\EsriTraining\MasterGisOnline\Proyecto_Final_de_Master\proyecto\Versions"
con = r'C:\EsriTraining\MasterGisOnline\Proyecto_Final_de_Master\proyecto\Connections\connection_server.ags'
rootMxdName = "geofences_and_pois" # Get from Mxd name 
parentVersion = "sde.DEFAULT" 

versionName = arcpy.GetParameterAsText(0)
versionedMapDocumentPath = os.path.join(versionedMxdFolder, rootMxdName + "_" + versionName + ".mxd")
# Create service and publish it
service = versionName
summary = 'Editable version of Geofences and Pois with name ' + versionName
tags = 'TFM, EEG'
versionedServiceDraftPath = os.path.join(versionedMxdFolder, rootMxdName + "_" + versionName + ".sddraft")
versionedServiceSdPath = os.path.join(versionedMxdFolder, rootMxdName + "_" + versionName + ".sd")

arcpy.AddMessage("Version service name: " + versionName)
arcpy.AddMessage("Version service summary: " + summary)
arcpy.AddMessage("Version service tag: " + tags)
arcpy.AddMessage("Versioned map document: " + versionedMapDocumentPath)
arcpy.AddMessage("Temporal service definition draft file: " + versionedServiceDraftPath)
arcpy.AddMessage("Service definition file: " + versionedServiceSdPath)

# Execute CreateVersion
arcpy.AddMessage("Step 1: Generating version: " + "sde." + versionName)
arcpy.CreateVersion_management(sdeWorkspace, parentVersion, versionName, "PUBLIC")
#Change current version ans environment session prior save current 
arcpy.ChangeVersion_management('geofences','TRANSACTIONAL', "sde." + versionName,'')
arcpy.ChangeVersion_management('pois','TRANSACTIONAL', "sde." + versionName,'')
time.sleep(3)

# Save mxd document with target version and workspace
arcpy.AddMessage("Step 2: Saving map document version")
mxd = arcpy.mapping.MapDocument("CURRENT")
mxd.saveACopy(versionedMapDocumentPath)
mxdVersioned = arcpy.mapping.MapDocument(versionedMapDocumentPath)

# create service definition draft
# CreateMapSDDraft (map_document, out_sddraft, service_name, {server_type}, {connection_file_path}, {copy_data_to_server}, {folder_name}, {summary}, {tags})
arcpy.AddMessage("Step 3: Generate service draft")
analysis = arcpy.mapping.CreateMapSDDraft(mxdVersioned, versionedServiceDraftPath, service, 'ARCGIS_SERVER', 
                                          con, True, rootMxdName, summary, tags)

# stage and upload the service if the sddraft analysis did not contain errors
draft_errors = False
if analysis['errors'] == {}:
    # Open and inspect sddraft
    doc = DOM.parse(versionedServiceDraftPath)
    def configure_capabilities(doc):
        type_names = doc.getElementsByTagName('TypeName')
        for type_name in type_names:
            """
            # Warning gives a code=90 error
            # To add store item (database): 
            # https://desktop.arcgis.com/es/arcmap/latest/analyze/arcpy-functions/adddatastoreitem.htm
            if type_name.firstChild.data == "FeatureServer":
                type_name.parentNode.getElementsByTagName("Enabled")[0].firstChild.data = "true"
            """
            if type_name.firstChild.data == "KmlServer":
                type_name.parentNode.getElementsByTagName("Enabled")[0].firstChild.data = "false"
    with open(versionedServiceDraftPath, 'w+') as xml:
        configure_capabilities(doc)
        doc.writexml(xml)
    # Execute StageService
    analysis = arcpy.mapping.AnalyzeForSD(versionedServiceDraftPath)
    if analysis['errors'] == {}:
        arcpy.AddMessage("Step 4: Generate service definition")
        arcpy.StageService_server(versionedServiceDraftPath, versionedServiceSdPath)
        arcpy.AddMessage("Step 5: Upload service definition")
        arcpy.UploadServiceDefinition_server(versionedServiceSdPath, con)
    else:
        draft_errors = True 
else: 
    draft_errors = True
    
# Restore versions and workspace to sde 
arcpy.AddMessage("Step 6: Restore default version in current map")
arcpy.ChangeVersion_management('geofences','TRANSACTIONAL', parentVersion,'')
arcpy.ChangeVersion_management('pois','TRANSACTIONAL', parentVersion,'')
time.sleep(10)
if draft_errors:
    arcpy.AddError(analysis['errors'])



