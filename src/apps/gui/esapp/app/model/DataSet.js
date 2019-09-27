Ext.define('esapp.model.DataSet', {
    extend : 'esapp.model.Base',

//    idProperty : 'productid',
    fields: [
       {name: 'productid', type: 'string', mapping: 'productid'},
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
//    ,associations:[
//        {
//            type: 'hasMany',
////            model: 'esapp.model.ProductMapset',
//            model: 'ProductMapset',
//            name: 'productmapsets'
//        }
//    ]
});


Ext.define('esapp.model.ProductMapSet', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'productid', reference:'DataSet', type: 'string'},
        {name: 'productcode'},
        {name: 'version'},
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
//    ,associations:[
//        {
//            type: 'hasMany',
//            model: 'MapSetDataSet',
////            model: 'esapp.model.MapSetDataSet',
//            name: 'mapsetdatasets'
//        }
//    ]
});


Ext.define('esapp.model.MapSetDataSet', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'mapsetcode', reference:'ProductMapSet'},
        {name: 'mapset_descriptive_name'},
        {name: 'datasetID'},
        {name: 'productcode'},
        {name: 'subproductcode'},
        {name: 'version'},
        {name: 'defined_by'},
        {name: 'activated', type: 'boolean'},
        {name: 'product_type'},
        {name: 'prod_descriptive_name'},
        {name: 'description'},
        {name: 'display_index', type: 'number'},
        {name: 'datasetcompletenessimage'},
        {name: 'datasetcompleteness_id', mapping:'datasetID'}
    ]
    ,associations:[
        {
            type: 'hasOne',
            model: 'DataSetCompleteness',
            name : 'datasetcompleteness'
        }
    ]
});

Ext.define('esapp.model.DataSetCompleteness', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'id', mapping:'datasetID'},
       {name: 'firstdate'},
       {name: 'lastdate'},
       {name: 'totfiles'},
       {name: 'missingfiles'}
    ]
    ,associations:[
        {
            type: 'hasMany',
            model: 'DataSetIntervals',
            name: 'datasetintervals'
        }
    ]
});

Ext.define('esapp.model.DataSetIntervals', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'fromdate'},
       {name: 'todate'},
       {name: 'intervaltype'},
       {name: 'intervalpercentage', type:'int'}
    ]
});
