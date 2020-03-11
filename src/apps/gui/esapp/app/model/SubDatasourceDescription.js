Ext.define('esapp.model.SubDatasourceDescription', {
    extend: 'esapp.model.Base',

    fields: [
        {name: 'pads_productcode'},
        {name: 'pads_version'},
        {name: 'pads_data_source_id'},
        {name: 'pads_type'},
        {name: 'datasource_descriptivename'},
        {name: 'productcode'},
        {name: 'subproductcode'},
        {name: 'version'},
        {name: 'datasource_descr_id'},
        {name: 'scale_factor', type: 'number'},
        {name: 'scale_offset', type: 'number'},
        {name: 'no_data', type: 'number', allowNull: true},
        {name: 'data_type_id'},
        {name: 'mask_min', type: 'number', allowNull: true},
        {name: 'mask_max', type: 'number', allowNull: true},
        {name: 're_process'},
        {name: 're_extract'},
        {name: 'scale_type'},
        {name: 'preproc_type'},
        {name: 'native_mapset'}
    ]

});
