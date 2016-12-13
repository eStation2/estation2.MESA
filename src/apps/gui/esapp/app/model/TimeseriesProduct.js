Ext.define('esapp.model.TimeseriesProduct', {
    extend : 'esapp.model.Base',

    //childType: 'esapp.model.TimeserieProductMapSet',

    //entityName: 'TimeseriesProduct',
    //idProperty: 'productid',
    fields: [
        //{name: 'itemtype', mapping: 'itemtype'},
        {name: 'cat_descr_name', mapping: 'cat_descr_name'},
        {name: 'category_id', mapping: 'category_id'},
        {name: 'order_index', mapping: 'order_index'},
        {name: 'productid', type: 'string', mapping: 'productid'},
        {name: 'productcode', mapping: 'productcode'},
        {name: 'version', mapping: 'version'},
        {name: 'subproductcode', mapping: 'subproductcode'},
        //{name: 'mapsetcode', mapping: 'mapsetcode'},
        {name: 'descriptive_name', mapping: 'descriptive_name'},
        {name: 'description', mapping: 'description'}
        //{name: 'years', mapping: 'years'}

        //{name: 'defined_by', mapping: 'defined_by'},
        //{name: 'product_type', mapping: 'product_type'},
        //{name: 'activated', type: 'boolean', mapping: 'activated'},
        //{name: 'prod_descriptive_name', mapping: 'prod_descriptive_name'},
    ]

    //,autoLoad: true
    //,autoSync: false
    //,remoteSort: false
    //,remoteGroup: false
    //,loadMask: true
    //
    //,proxy: {
    //    type: 'ajax',
    //    url: 'analysis/timeseriesproduct',
    //    reader: {
    //         type: 'json'
    //        ,typeProperty: 'itemtype'
    //        ,successProperty: 'success'
    //        ,rootProperty: 'products'
    //        ,messageProperty: 'message'
    //    },
    //    listeners: {
    //        exception: function(proxy, response, operation){
    //            // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
    //            console.info('TIMESERIES PRODUCT MODEL - REMOTE EXCEPTION - Reload timeseries product grid!');
    //
    //            //Ext.Msg.show({
    //            //    title: 'TIMESERIES PRODUCT MODEL - REMOTE EXCEPTION',
    //            //    msg: operation.getError(),
    //            //    icon: Ext.Msg.ERROR,
    //            //    buttons: Ext.Msg.OK
    //            //});
    //        }
    //    }
    //}

});


Ext.define('esapp.model.TimeserieProductMapSet', {
    extend : 'esapp.model.Base',

    //childType: 'esapp.model.TimeserieProductMapSetDataSet',
    //entityName: 'TimeseriesMapset',
    //idProperty: 'productmapsetid',
    fields: [
        //{name: 'productid', reference:'TimeseriesProduct', type: 'string'},
        {name: 'productmapsetid', mapping: 'productmapsetid'},
        {name: 'productid',  type: 'string'},
        //{name: 'itemtype', mapping: 'itemtype'},
        //{name: 'cat_descr_name', mapping: 'cat_descr_name'},
        //{name: 'category_id', mapping: 'category_id'},
        //{name: 'order_index', mapping: 'order_index'},
        //{name: 'productcode', mapping: 'productcode'},
        //{name: 'version', mapping: 'version'},
        //{name: 'subproductcode', mapping: 'subproductcode'},
        {name: 'mapsetcode', mapping: 'mapsetcode'},
        {name: 'descriptive_name', mapping: 'descriptive_name'},
        {name: 'description', mapping: 'description'}
        //{name: 'years', mapping: 'years'}

        //{name: 'mapsetcode'},
        //{name: 'defined_by'},
        //{name: 'descriptive_name'},
        //{name: 'description'},
        //{name: 'srs_wkt'},
        //{name: 'upper_left_long'},
        //{name: 'pixel_shift_long'},
        //{name: 'rotation_factor_long'},
        //{name: 'upper_left_lat'},
        //{name: 'pixel_shift_lat'},
        //{name: 'rotation_factor_lat'},
        //{name: 'pixel_size_x'},
        //{name: 'pixel_size_y'},
        //{name: 'footprint_image'}
    ]
});


Ext.define('esapp.model.TimeserieProductMapSetDataSet', {
    extend : 'esapp.model.Base',

    //entityName: 'TimeseriesSubproduct',
    //idProperty: 'subproductid',
    fields: [
        //{name: 'mapsetcode', reference:'TimeserieProductMapSet'},
        {name: 'mapsetcode', mapping:'mapsetcode'},
        {name: 'subproductid', type: 'string', mapping: 'subproductid'},
        //{name: 'itemtype', mapping: 'itemtype'},
        //{name: 'cat_descr_name', mapping: 'cat_descr_name'},
        //{name: 'category_id', mapping: 'category_id'},
        //{name: 'order_index', mapping: 'order_index'},
        {name: 'productcode', mapping: 'productcode'},
        {name: 'version', mapping: 'version'},
        {name: 'subproductcode', mapping: 'subproductcode'},
        {name: 'descriptive_name', mapping: 'descriptive_name'},
        {name: 'description', mapping: 'description'},
        {name: 'years', mapping: 'years'}


        //{name: 'productid'},
        //{name: 'productcode'},
        //{name: 'subproductcode'},
        //{name: 'version'},
        //{name: 'defined_by'},
        //{name: 'activated', type: 'boolean'},
        //{name: 'product_type'},
        ////{name: 'prod_descriptive_name'},
        //{name: 'descriptive_name'},
        //{name: 'description'}
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


