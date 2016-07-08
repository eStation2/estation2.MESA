Ext.define('esapp.model.TSDrawProperties', {
    extend: 'esapp.model.Base',

    fields: [
        {name: 'productcode'},
        {name: 'subproductcode'},
        {name: 'version'},
        {name: 'title'},
        {name: 'unit'},
        {name: 'min', type: 'number'},
        {name: 'max', type: 'number'},
        {name: 'oposite', type: 'boolean'},
        {name: 'tsname_in_legend'},
        {name: 'charttype'},
        {name: 'linestyle'},
        {name: 'linewidth', type: 'integer'},
        {name: 'color'},
        {name: 'yaxes_id'},
        {name: 'title_color'}
        //{name: 'aggregation_type'},
        //{name: 'aggregation_min', type: 'number'},
        //{name: 'aggregation_max', type: 'number'}
    ]
});
