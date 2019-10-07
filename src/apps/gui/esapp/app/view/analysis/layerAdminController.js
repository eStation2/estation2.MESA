Ext.define('esapp.view.analysis.layerAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-layeradmin'

    ,onClose: function(win, ev) {
        // Ext.getCmp('analysismain').lookupReference('analysismain_layersbtn').enable();
    }

    // ,onShow: function(win, ev) {
        // this.loadLayersStore();
    // }

    ,loadLayersStore: function(win, ev) {
        var me = this.getView();
        var layersgridstore  = Ext.data.StoreManager.lookup('LayersStore');
        // var layersgridstore  = me.lookupReference('layersGrid').getStore('layers');
        //console.info(me.view);
        if (layersgridstore.isStore) {
            layersgridstore.load({
                callback: function(records, options, success) {
                    me.lookupReference('layersGrid').updateLayout();
                    me.updateLayout();
                }
            });
        }
        // me.lookupReference('layersGrid').updateLayout();
        // me.updateLayout();
    }

    ,addLayer: function(){
        // Create a new layer record and pass it. With the bind the store will automaticaly saved (through CRUD) on the server!
        var layersgridstore  = Ext.data.StoreManager.lookup('LayersStore');
        var newLayerRecord = new esapp.model.Layer(
            {
                'layerid': 'newlayer',
                'layerlevel': '',
                'layername': 'New layer',
                'description': '',
                'filename': '',
                'layerorderidx': 1,
                'layertype': 'polygon',
                'polygon_outlinecolor': '#000000',
                'polygon_outlinewidth': '2',
                'polygon_fillcolor': 'Transparent',
                'polygon_fillopacity': 1,
                'feature_display_column': '',
                'feature_highlight_outlinecolor': '#319FD3',
                'feature_highlight_outlinewidth': '2',
                'feature_highlight_fillcolor': '#319FD3',
                'feature_highlight_fillopacity': 10,
                'feature_selected_outlinecolor': '#FF0000',
                'feature_selected_outlinewidth': 2,
                'enabled': true,
                'deletable': true,
                'background_legend_image_filename': '',
                'projection': '',
                'submenu': '',
                'menu': 'other',
                'defined_by': 'USER',
                'open_in_mapview': false,
                'provider': ''
            }
        );
        //layersgridstore.add(newLayerRecord);

        var addLayerWin = new esapp.view.analysis.addEditLayer({
            params: {
                edit: false,
                layerrecord: newLayerRecord
            }
        });
        addLayerWin.show();
    }

    ,editLayer: function(grid, rowIndex, row){
        var user = esapp.getUser();
        var record = null;

        if(!isNaN(record)) {    // record is the rowIndex so get the record from the store through the rowIndex
            record = grid.getStore().getAt(rowIndex);
        }

        var edit = false;
        var view = true;
        if (record.get('defined_by') != 'JRC' || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
            edit = true;
            view = false;
        }
        //if (record.get('defined_by') != 'JRC') {
            var editLayerWin = new esapp.view.analysis.addEditLayer({
                params: {
                    new: false,
                    edit: edit,
                    view: view,
                    layerrecord: record
                }
            });
            editLayerWin.show();
        //}
    }

    ,deleteLayer: function(grid, rowIndex, row){
        var record = grid.getStore().getAt(rowIndex);
        if (record.get('deletable')){
            Ext.Msg.show({
                title: esapp.Utils.getTranslation('deletelayerquestion'),     // 'Delete layer definition?',
                message: esapp.Utils.getTranslation('deletelayerquestion2') + ' "' + record.get('layername') + '"?',
                buttons: Ext.Msg.OKCANCEL,
                icon: Ext.Msg.QUESTION,
                fn: function(btn) {
                    if (btn === 'ok') {
                        grid.getStore().remove(record);
                    }
                }
            });
        }
    }

});
