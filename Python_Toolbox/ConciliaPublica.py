"""
Concilia y publica todas las versiones en la capa sde.DEFAULT
Referencia: https://desktop.arcgis.com/es/arcmap/latest/manage-data/geodatabases/using-python-scripting-to-batch-reconcile-and-post-versions.htm
"""

#Import modules
import arcpy
from datetime import date

today = date.today().strftime("%d-%m-%y")

adminConn = r"C:\Users\autok\AppData\Roaming\ESRI\Desktop10.8\ArcCatalog\sde@geofences_and_pois.sde"
reconcilieLogFile = r"C:\EsriTraining\MasterGisOnline\Proyecto_Final_de_Master\proyecto\Logs\reconcilieLog"+today+".txt"

concileOption = "KEEP_VERSION"
deleteVersions = arcpy.GetParameter(0)
if deleteVersions: 
    concileOption = "DELETE_VERSION"

# Block new connections to the database.
arcpy.AddMessage("The database is no longer accepting connections")
arcpy.AcceptConnections(adminConn, False)

# Disconnect all users from the database.
arcpy.AddMessage("Disconnecting all users")
arcpy.DisconnectUser(adminConn, "ALL")

# Get a list of versions to pass into the ReconcileVersions tool.
# Only reconcile versions that are children of Default
arcpy.AddMessage("Compiling a list of versions to reconcile")
versionList = arcpy.ListVersions(adminConn)

# Execute the ReconcileVersions tool.
arcpy.AddMessage("Reconciling all versions")
arcpy.ReconcileVersions_management(adminConn, "ALL_VERSIONS", "sde.DEFAULT", versionList, "LOCK_ACQUIRED", "NO_ABORT", "BY_OBJECT", "FAVOR_TARGET_VERSION", "POST", concileOption, reconcilieLogFile)

# Run the compress tool.
arcpy.AddMessage("Running compress")
arcpy.Compress_management(adminConn)

# Allow the database to begin accepting connections again
arcpy.AddMessage("Allow users to connect to the database again")
arcpy.AcceptConnections(adminConn, True)

# Update statistics and indexes for the system tables
# Note: to use the "SYSTEM" option the user must be an geodatabase or database administrator.
# Rebuild indexes on the system tables
arcpy.AddMessage("Rebuilding indexes on the system tables")
arcpy.RebuildIndexes_management(adminConn, "SYSTEM")

# Update statistics on the system tables
arcpy.AddMessage("Updating statistics on the system tables")
arcpy.AnalyzeDatasets_management(adminConn, "SYSTEM")

arcpy.AddMessage("Finished.")







