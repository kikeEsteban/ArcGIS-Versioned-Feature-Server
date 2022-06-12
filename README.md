# ArcGIS-Versioned-Feature-Server
 Utils for publishing and editing versions of Feature Layers

## Nomenclaturas

1. Nombre de base de datos: EEG_DataBase

2. Nombre de dataset: EEG_FeatureSet
* pois: Capa de puntos
* geofences: Capa de polígonos 

3. Etiquetas para los servicios: "EEG, TFM, Esri, ArcGIS Server, Postgresql"

## Fichero config

```json
{
    "db_name": "XXXXX",  // Nombre de la base de datos
    "db_sde_password": "YYYYYYY", // Password en PostgreSQL del usuario SDE
    "server_publisher_name": "ZZZZZZZZ",  // Nombre de usuario publisher de ArcGIS Server
    "server_publisher_password": "WWWWWWW" // Contraseña del usuario publisher de ArcGIS Server
}
```
