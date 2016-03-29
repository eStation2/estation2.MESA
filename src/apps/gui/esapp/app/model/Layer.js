Ext.define('esapp.model.Layer', {
    extend: 'esapp.model.Base',

    fields: [
        {name: 'layerid'},
        {name: 'layerlevel'},
        {name: 'layername'},
        {name: 'description'},
        {name: 'layerpath'},
        {name: 'filename'},
        {name: 'layerorderidx'},
        {name: 'layertype'},
        {name: 'polygon_outlinecolor'},
        {name: 'polygon_outlinewidth'},
        {name: 'polygon_fillcolor'},
        {name: 'polygon_fillopacity'},
        {name: 'feature_display_column'},
        {name: 'feature_highlight_outlinecolor'},
        {name: 'feature_highlight_outlinewidth'},
        {name: 'feature_highlight_fillcolor'},
        {name: 'feature_highlight_fillopacity'},
        {name: 'feature_selected_outlinecolor'},
        {name: 'feature_selected_outlinewidth'},
        {name: 'enabled'},
        {name: 'deletable'},
        {name: 'background_legend_image_filename'},
        {name: 'projection'},
        {name: 'submenu'},
        {name: 'menu'}
    ]

    //,autoLoad: true
    //,autoSync: false
    ////,session: true
    //
    //,proxy: {
    //    type: 'rest',
    //
    //    appendId: false,
    //
    //    api: {
    //        read: 'layers',
    //        create: 'layers/create',
    //        update: 'layers/update',
    //        destroy: 'layers/delete'
    //    },
    //    reader: {
    //         type: 'json'
    //        ,successProperty: 'success'
    //        ,rootProperty: 'layers'
    //        ,messageProperty: 'message'
    //    },
    //    writer: {
    //        type: 'json',
    //        writeAllFields: true,
    //        rootProperty: 'layers'
    //    },
    //    listeners: {
    //        exception: function(proxy, response, operation){
    //            // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
    //            console.info('LAYERS STORE - REMOTE EXCEPTION');
    //        }
    //    }
    //}
    //,listeners: {
    //    //update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
    //    //    // This event is triggered on every change made in a record!
    //    //},
    //    write: function(store, operation){
    //        var result = Ext.JSON.decode(operation.getResponse().responseText);
    //        if (operation.success) {
    //           Ext.toast({ html: result.message, title: esapp.Utils.getTranslation('layerupdated'), width: 200, align: 't' });
    //        }
    //    }
    //}
});
