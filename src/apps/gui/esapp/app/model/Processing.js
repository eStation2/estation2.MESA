Ext.define('esapp.model.Processing', {
    extend : 'esapp.model.Base',
    idProperty: 'process_id',
    fields: [
        {name: 'category_id', mapping: 'category_id'},
        {name: 'cat_descr_name', mapping: 'cat_descr_name'},
        {name: 'order_index', mapping: 'order_index'},
        {name: 'process_id', mapping: 'process_id'},
        {name: 'process_defined_by', mapping: 'process_defined_by'},
        {name: 'process_activated', type: 'boolean', mapping: 'process_activated'},
        {name: 'output_mapsetcode', mapping: 'output_mapsetcode'},
        {name: 'derivation_method', mapping: 'derivation_method'},
        {name: 'algorithm', mapping: 'algorithm'},
        {name: 'priority', mapping: 'priority'}
    ]
});

Ext.define('esapp.model.InputProducts', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'process_id', reference:'Processing', type: 'string'},
        {name: 'productid', type: 'string', mapping: 'productid'},
        {name: 'productcode'},
        {name: 'subproductcode'},
        {name: 'version'},
        {name: 'defined_by'},
        {name: 'descriptive_name'},
        {name: 'description'},
        {name: 'product_type'},
        {name: 'date_format'},
        {name: 'start_date'},
        {name: 'end_date'},
        {name: 'mapsetcode'},
        {name: 'type'}
    ]
    //,associations:[
    //    {
    //        type: 'hasOne',
    //        model: 'ProcessingProductMapSet',
    //        name : 'inputproductmapset'
    //    }
    //]
});

Ext.define('esapp.model.OutputProducts', {
    extend : 'esapp.model.Base',
    //idProperty: 'process_id',
    fields: [
        {name: 'process_id', reference:'Processing', type: 'string', critical: true},
        {name: 'productid', type: 'string', mapping: 'productid'},
        {name: 'productcode', critical: true},
        {name: 'subproductcode', critical: true},
        {name: 'version', critical: true},
        {name: 'mapsetcode', critical: true},
        {name: 'subactivated', type: 'boolean'},
        {name: 'defined_by'},
        {name: 'descriptive_name'},
        {name: 'description'},
        {name: 'product_type'},
        {name: 'date_format'},
        {name: 'start_date'},
        {name: 'end_date'},
        {name: 'type'},
        {name: 'final'}
    ]
    //,associations:[
    //    {
    //        type: 'hasOne',
    //        model: 'ProcessingProductMapSet',
    //        name : 'outputproductmapset'
    //    }
    //]
});

Ext.define('esapp.model.ProcessingProductMapSet', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'productid', reference:'InputProducts', type: 'string'},
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



