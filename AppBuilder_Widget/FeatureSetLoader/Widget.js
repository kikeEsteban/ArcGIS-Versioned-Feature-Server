define([
  'dojo/_base/declare',
  'jimu/BaseWidget',
  'esri/layers/FeatureLayer',
  "esri/request",
  'dojo/_base/html',
  "esri/geometry/Point",
  "esri/InfoTemplate"
  ],
  function(declare, BaseWidget, FeatureLayer, esriRequest, html, Point, InfoTemplate) {
    return declare([BaseWidget], {
      baseClass: 'jimu-widget-FeatureSetLoader',
      name: "FeatureSetLoader",
      addFMS: function() {

        html.empty(this.errorResultNode);
        html.empty(this.loadedResultNode);

        if(this.wfsTextBox.value != ""){
          var params = {
              url: this.config.base_url + this.wfsTextBox.value + "/FeatureServer",
              content: {
                f: "pjson"
              }
          };
          var requestHandle = esriRequest(params);
          requestHandle.then((result) => {
            if(result.layers && result.layers.length > 0){
              if(this.addedLayers && this.addedLayers.length > 0){
                for(const layer in this.addedLayers){
                  this.map.removeLayer(this.addedLayers[layer]);
                }
              }
              this.addedLayers = []
              const fullExtent = result["fullExtent"]
              var contentStr = "<div style='display: flex; flex-direction: column;'><div>Layers loaded:</div>"
              console.log("!!! Result")
              console.log(result)
              var infoTemplate = new InfoTemplate("Attributes", "${*}");
              for(const layer in result.layers){
                const layerUrl = params.url + "/" + result.layers[layer].id;
                const featureLayer = new FeatureLayer(layerUrl,{outFields:["*"], infoTemplate: infoTemplate});
                const addedLayer = this.map.addLayer(featureLayer);
                this.addedLayers.push(addedLayer);
                console.log(layer)
                contentStr = contentStr + "<div style='margin-top: 5px'>" + result.layers[layer].type + " <b>" + result.layers[layer].name + "</b> of type: " + result.layers[layer].geometryType + "</div>"
              }
              contentStr = contentStr + "</div>"
              const x = (fullExtent.xmax + fullExtent.xmin) / 2
              const y = (fullExtent.ymax + fullExtent.ymin) / 2
              this.map.centerAndZoom(new Point(x,y,fullExtent.spatialReference),1)
              var aboutContent = html.toDom(contentStr);
              html.place(aboutContent, this.loadedResultNode);
            }
          }, null, (update) => { 
            console.log("progress loading feature set", update); 
          }).catch((err) => { 
            var aboutContent = html.toDom("<span>Error loading feature set: " + err.message+ "</span>");
            html.place(aboutContent, this.errorResultNode);
          });
        }
      }
    });
  });