define([
  'dojo/_base/declare',
  'jimu/BaseWidget',
  'esri/layers/FeatureLayer',
  "esri/request",
  'dojo/_base/html',
  ],
  function(declare, BaseWidget, FeatureLayer, esriRequest, html) {
    return declare([BaseWidget], {
      baseClass: 'jimu-widget-WMSLoader',
      name: "WMSLoader",
      addFMS: function() {

        html.empty(this.customContentNode);

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
              for(const layer in result.layers){
                const layerUrl = params.url + "/" + result.layers[layer].id;
                const featureLayer = new FeatureLayer(layerUrl);
                const addedLayer = this.map.addLayer(featureLayer);
                this.addedLayers.push(addedLayer);
              }
            }
          }, null, (update) => { 
            console.log("progress !!!", update); 
          }).catch((err) => { 
            console.log("Error !!!")
            console.log(err);
            var aboutContent = html.toDom("<span>Error!!!</span>");
            html.place(aboutContent, this.customContentNode);
          });
        }
      }
    });
  });