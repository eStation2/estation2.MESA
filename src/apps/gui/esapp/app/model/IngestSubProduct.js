Ext.define('esapp.model.IngestSubProduct', {
    extend : 'esapp.model.Base',

    // idProperty : 'productid',

    fields: [
        {name: 'productid'},
        {name: 'productcode'},
        {name: 'orig_subproductcode'},
        {name: 'subproductcode'},
        {name: 'version'},
        {name: 'defined_by'},
        {name: 'activated', type: 'boolean'},
        {name: 'category_id'},
        {name: 'product_type'},
        {name: 'descriptive_name'},
        {name: 'description'},
        {name: 'provider'},
        {name: 'frequency_id'},
        {name: 'date_format'},
        {name: 'scale_factor', type: 'number', allowNull: true},
        {name: 'scale_offset', type: 'number', allowNull: true},
        {name: 'nodata', type: 'number', allowNull: true},
        {name: 'mask_min', type: 'number', allowNull: true},
        {name: 'mask_max', type: 'number', allowNull: true},
        {name: 'unit'},
        {name: 'data_type_id'},
        {name: 'masked', type: 'boolean'},
        {name: 'enable_in_timeseries', type: 'boolean'},
        {name: 'timeseries_role'},
        {name: 'display_index', type: 'number', allowNull: true}
    ]
});