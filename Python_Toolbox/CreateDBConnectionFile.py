from ensurepip import version
import arcpy
import os

serviceName = "registered_version"
con = r'C:\EsriTraining\MasterGisOnline\Proyecto_Final_de_Master\proyecto\Connections\connection_server.ags'
out_folder_path = r'C:\EsriTraining\MasterGisOnline\Proyecto_Final_de_Master\proyecto\Connections'
rootMxdName = "geofences_and_pois"
versionName = "sde." + serviceName
out_name = versionName + "@" + rootMxdName + ".sde"
database_platform = "POSTGRESQL"
instance = "localhost"
account_authentication = "DATABASE_AUTH"
username = 'sde'
password = 'gis12345'
save_user_pass = True
database = "geofences_and_pois"
version_type = "TRANSACTIONAL"

arcpy.management.CreateDatabaseConnection(
    out_folder_path, 
    out_name, 
    database_platform, 
    instance, 
    account_authentication, 
    username, 
    password, 
    save_user_pass, 
    database, 
    None, 
    version_type, 
    versionName)

sdeWorkspace = os.path.join(out_folder_path,out_name)
arcpy.AddDataStoreItem(con, "DATABASE", serviceName, sdeWorkspace, sdeWorkspace)