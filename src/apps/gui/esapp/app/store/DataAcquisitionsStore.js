Ext.define('esapp.store.DataAcquisitionsStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.dataacquisitions',

    requires : [
        'esapp.model.DataAcquisition'
    ],

    model: 'esapp.model.DataAcquisition',

    storeId : 'DataAcquisitionsStore'

//    session: true,
    ,autoLoad: true
    ,autoSync: true
    ,remoteSort: false

//    sorters: {property: 'productcode', direction: 'ASC'}

    ,proxy: {
        type: 'rest',
        // url: 'dataacquisition',
        appendId: false,
        api: {
            read: 'dataacquisition',
            create: 'dataacquisition/create',
            update: 'dataacquisition/update',
            destroy: 'dataacquisition/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'dataacquisitions'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'dataacquisitions'
        },
        listeners: {
            exception: function(proxy, response, operation){
                Ext.MessageBox.show({
                    title: 'ACQUISITION STORE- REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.MessageBox.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }

    ,listeners: {
        write: function(store, operation){
            Ext.toast({ html: operation.getResultSet().message, title: "Get update", width: 300, align: 't' });
        }
    }
});






//var data = {
//    "success": true,
//    "DataAcquisition": [{
//         "productID": "vgt_ndvi_vgt_ndvi_native_undefined",
//         "productcode": "vgt_ndvi",
//         "subproductcode": "vgt_ndvi_native",
//         "version": "undefined",
//         "data_source_id": "EO:EUM:DAT:SPOT:S10NDVI",
//         "defined_by": "JRC",
//         "type": "EUMETCAST",
//         "activated": true,
//         "store_original_data": false,
//         "latest": "05/06/2014"
//    }]
//};
//
//esapp.store.DataAcquisitionsStore.loadData(data);