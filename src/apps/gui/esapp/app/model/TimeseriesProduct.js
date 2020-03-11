Ext.define('esapp.model.TimeseriesProduct', {
    extend : 'esapp.model.Base',

    //idProperty: 'productid',
    fields: [
        {name: 'category_id', mapping: 'category_id'},
        {name: 'cat_descr_name', mapping: 'cat_descr_name'},
        {name: 'order_index', mapping: 'order_index'},
        {name: 'productid', type: 'string', mapping: 'productid'},
        {name: 'productcode', mapping: 'productcode'},
        {name: 'version', mapping: 'version'},
        {name: 'subproductcode', mapping: 'subproductcode'},
        {name: 'productmapsetid', type: 'string', mapping: 'productmapsetid'},
        {name: 'display_index', type: 'integer'},
        {name: 'mapsetcode', mapping: 'mapsetcode'},
        {name: 'mapset_name', mapping: 'mapset_name'},
        {name: 'group_product_descriptive_name', mapping: 'group_product_descriptive_name'},
        {name: 'product_descriptive_name', mapping: 'product_descriptive_name'},
        {name: 'product_description', mapping: 'product_description'},
        {name: 'years', mapping: 'years'},
        {name: 'frequency_id', mapping: 'frequency_id'},
        {name: 'date_format', mapping: 'date_format'},
        {name: 'timeseries_role', mapping: 'timeseries_role'},
        {name: 'selected', mapping: 'selected'},
        {name: 'cumulative', mapping: 'cumulative'},
        {name: 'difference', mapping: 'difference'},
        {name: 'reference', mapping: 'reference'},
        {name: 'zscore', mapping: 'zscore'},
        {name: 'colorramp', mapping: 'colorramp'}
        //{name: 'product_type', mapping: 'product_type'},
    ]

});


Ext.define('esapp.model.SelectedTimeseriesMapSetDataSet', {
    extend : 'esapp.model.Base',

    //idProperty: 'subproductid',
    fields: [
        {name: 'category_id', mapping: 'category_id'},
        {name: 'cat_descr_name', mapping: 'cat_descr_name'},
        {name: 'order_index', mapping: 'order_index'},
        {name: 'productid', type: 'string', mapping: 'productid'},
        {name: 'productcode', mapping: 'productcode'},
        {name: 'version', mapping: 'version'},
        {name: 'subproductcode', mapping: 'subproductcode'},
        {name: 'productmapsetid', type: 'string', mapping: 'productmapsetid'},
        {name: 'mapsetcode', mapping: 'mapsetcode'},
        {name: 'mapset_name', mapping: 'mapset_name'},
        {name: 'group_product_descriptive_name', mapping: 'group_product_descriptive_name'},
        {name: 'product_descriptive_name', mapping: 'product_descriptive_name'},
        {name: 'product_description', mapping: 'product_description'},
        {name: 'years', mapping: 'years'},
        {name: 'frequency_id', mapping: 'frequency_id'},
        {name: 'date_format', mapping: 'date_format'},
        {name: 'timeseries_role', mapping: 'timeseries_role'},
        {name: 'selected', mapping: 'selected'},
        {name: 'cumulative', mapping: 'cumulative'},
        {name: 'difference', mapping: 'difference'},
        {name: 'reference', mapping: 'reference'},
        {name: 'zscore', mapping: 'zscore'},
        {name: 'colorramp', mapping: 'colorramp'}
        //{name: 'subproductid', type: 'string', mapping: 'subproductid'},
    ]
});


//Ext.define('esapp.model.TimeserieProductMapSet', {
//    extend : 'esapp.model.Base',
//
//    //childType: 'esapp.model.TimeserieProductMapSetDataSet',
//    //entityName: 'TimeseriesMapset',
//    //idProperty: 'productmapsetid',
//    fields: [
//        //{name: 'productid', reference:'TimeseriesProduct', type: 'string'},
//        {name: 'productmapsetid', mapping: 'productmapsetid'},
//        {name: 'productid',  type: 'string'},
//        //{name: 'itemtype', mapping: 'itemtype'},
//        //{name: 'cat_descr_name', mapping: 'cat_descr_name'},
//        //{name: 'category_id', mapping: 'category_id'},
//        //{name: 'order_index', mapping: 'order_index'},
//        //{name: 'productcode', mapping: 'productcode'},
//        //{name: 'version', mapping: 'version'},
//        //{name: 'subproductcode', mapping: 'subproductcode'},
//        {name: 'mapsetcode', mapping: 'mapsetcode'},
//        {name: 'descriptive_name', mapping: 'descriptive_name'},
//        {name: 'description', mapping: 'description'}
//        //{name: 'years', mapping: 'years'}
//
//        //{name: 'mapsetcode'},
//        //{name: 'defined_by'},
//        //{name: 'descriptive_name'},
//        //{name: 'description'},
//        //{name: 'srs_wkt'},
//        //{name: 'upper_left_long'},
//        //{name: 'pixel_shift_long'},
//        //{name: 'rotation_factor_long'},
//        //{name: 'upper_left_lat'},
//        //{name: 'pixel_shift_lat'},
//        //{name: 'rotation_factor_lat'},
//        //{name: 'pixel_size_x'},
//        //{name: 'pixel_size_y'},
//        //{name: 'footprint_image'}
//    ]
//});
