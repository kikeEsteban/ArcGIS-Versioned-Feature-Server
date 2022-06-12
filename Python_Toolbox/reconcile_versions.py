"""
Concilia y publica todas las versiones en la capa sde.DEFAULT
Referencia: https://desktop.arcgis.com/es/arcmap/latest/manage-data/geodatabases/using-python-scripting-to-batch-reconcile-and-post-versions.htm
"""

#Import modules
import os
import arcpy
from datetime import datetime

workspace_description = arcpy.Describe(arcpy.env.workspace)
if workspace_description.workspaceType != u'RemoteDatabase':
    arcpy.AddError("Error: Current workspace need to be a RemoteDatabase")
    exit()
if workspace_description.connectionProperties.instance != u'sde:postgresql:localhost':
    arcpy.AddError("Error: Current workspace need to be sde connection to a Postgresql running in localhost")
    exit()

today = datetime.today().strftime("%d-%m-%y_%H.%M.%S")
adminConn = arcpy.env.workspace
dirname = os.path.dirname(__file__)
reconcilieLogFile = os.path.join(dirname, 'Logs', "reconcilie_log_"+today+".txt")

inputs = arcpy.GetParameterAsText(0).split(";")
arcpy.AddMessage(inputs)

version_names = []
for input in inputs:
    if os.path.exists(input):
        arcpy.AddMessage(input + " is a file")
        # set Json format for list versions in a file. 
        # Fields like summary and tags can be added here
    else:
        version_names.append("sde." + input)

versionList = arcpy.ListVersions(adminConn)
arcpy.AddMessage("Version list:")
arcpy.AddMessage(versionList)

for version_name in version_names:
    try:
        versionList.index(version_name)
    except ValueError as e:
       arcpy.AddError(version_name + " version doesn't exist")
       raise 

type_of_conflict = "BY_OBJECT"
by_attribute = arcpy.GetParameter(1)
if by_attribute: 
    type_of_conflict = "BY_ATTRIBUTE"

abort = "NO_ABORT"
abort_conflicts = arcpy.GetParameter(2)
if abort_conflicts: 
    abort = "ABORT_CONFLICTS"    

# Block new connections to the database.
arcpy.AddMessage("The database is no longer accepting connections")
arcpy.AcceptConnections(adminConn, False)

# Disconnect all users from the database.
arcpy.AddMessage("Disconnecting all users")
arcpy.DisconnectUser(adminConn, "ALL")

# Execute the ReconcileVersions tool.
arcpy.AddMessage("Reconciling all versions")
arcpy.ReconcileVersions_management(
    adminConn, 
    "ALL_VERSIONS", 
    "sde.DEFAULT", 
    versionList, 
    "LOCK_ACQUIRED", 
    abort, 
    type_of_conflict, 
    "FAVOR_TARGET_VERSION", 
    "POST", 
    "KEEP_VERSION", 
    reconcilieLogFile)

# Run the compress tool.
arcpy.AddMessage("Running compress")
arcpy.Compress_management(adminConn)

# Allow the database to begin accepting connections again
arcpy.AddMessage("Allow users to connect to the database again")
arcpy.AcceptConnections(adminConn, True)

# Update statistics and indexes for the system tables
arcpy.AddMessage("Rebuilding indexes on the system tables")
arcpy.RebuildIndexes_management(adminConn, "SYSTEM")

# Update statistics on the system tables
arcpy.AddMessage("Updating statistics on the system tables")
arcpy.AnalyzeDatasets_management(adminConn, "SYSTEM")

arcpy.AddMessage("Finished.")
