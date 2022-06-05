import arcpy

outdir = r'C:\EsriTraining\MasterGisOnline\Proyecto_Final_de_Master\proyecto\Connections'
out_folder_path = outdir
out_name = 'connection_server.ags'
server_url = 'https://DESKTOP-BHFU9L0:6443/arcgis/admin/'
use_arcgis_desktop_staging_folder = True
staging_folder_path = r'C:\Users\autok\AppData\Local\Temp\arc93BC\Staging'
username = 'EEG_Publicador'
password = 'EEG_Publicador'
    
arcpy.mapping.CreateGISServerConnectionFile("ADMINISTER_GIS_SERVICES",
                                            out_folder_path,
                                            out_name,
                                            server_url,
                                            "ARCGIS_SERVER",
                                            use_arcgis_desktop_staging_folder,
                                            staging_folder_path,
                                            username,
                                            password,
                                            "SAVE_USERNAME")