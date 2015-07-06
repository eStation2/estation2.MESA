Ext.define('esapp.model.TimeseriesProduct', {
    extend : 'esapp.model.Base',

//    idProperty : 'productID',
    fields: [
       {name: 'productID', type: 'string', mapping: 'productID'},
       {name: 'productcode', mapping: 'productcode'},
       {name: 'subproductcode', mapping: 'subproductcode'},
       {name: 'version', mapping: 'version'},
       {name: 'defined_by', mapping: 'defined_by'},
       {name: 'product_type', mapping: 'product_type'},
       {name: 'activated', type: 'boolean', mapping: 'activated'},
       {name: 'prod_descriptive_name', mapping: 'prod_descriptive_name'},
       {name: 'description', mapping: 'description'},
       {name: 'category_id', mapping: 'category_id'},
       {name: 'cat_descr_name', mapping: 'cat_descr_name'},
       {name: 'order_index', mapping: 'order_index'}
    ]

    ,autoLoad: false
    ,autoSync: false
    ,remoteSort: false
    ,remoteGroup: false
    ,loadMask: true

    ,proxy: {
        type: 'rest',
        // url: '',
        appendId: false,
        actionMethods: {
            create: 'POST',
            read: 'GET',
            update: 'POST',
            destroy: 'POST'
        },
        api: {
            read: 'analysis/timeseriesproduct',
            create: 'analysis/timeseriesproduct/create',
            update: 'analysis/timeseriesproduct/update',
            destroy: 'analysis/timeseriesproduct/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'products'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'products'
        },
        listeners: {
            exception: function(proxy, response, operation){
                Ext.MessageBox.show({
                    title: 'TIMESERIES PRODUCT MODEL - REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.MessageBox.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }

});


Ext.define('esapp.model.TimeserieProductMapSet', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'productID', reference:'TimeseriesProduct', type: 'string'},
        {name: 'mapsetcode'},
        {name: 'defined_by'},
        {name: 'descriptive_name'},
        {name: 'description'},
        {name: 'srs_wkt'},
        {name: 'upper_left_long'},
        {name: 'pixel_shift_long'},
        {name: 'rotation_factor_long'},
        {name: 'upper_left_lat'},
        {name: 'pixel_shift_lat'},
        {name: 'rotation_factor_lat'},
        {name: 'pixel_size_x'},
        {name: 'pixel_size_y'},
        {name: 'footprint_image'}
    ]
});


Ext.define('esapp.model.TimeserieProductMapSetDataSet', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'mapsetcode', reference:'TimeserieProductMapSet'},
       {name: 'productID'},
       {name: 'productcode'},
       {name: 'subproductcode'},
       {name: 'version'},
       {name: 'defined_by'},
       {name: 'activated', type: 'boolean'},
       {name: 'product_type'},
       {name: 'prod_descriptive_name'},
       {name: 'description'}
    ]
});

//
//Ext.define('esapp.model.Year', {
//    extend : 'esapp.model.Base',
//
//    fields: [
//       {name: 'year'}
//    ],
//    data: [
//        {year: 2010},
//        {year: 2011},
//        {year: 2012},
//        {year: 2013},
//        {year: 2014},
//        {year: 2015}
//    ]
//});


