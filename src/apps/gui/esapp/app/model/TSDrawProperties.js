Ext.define('esapp.model.TSDrawProperties', {
    extend: 'esapp.model.Base',

    fields: [
        {name: 'productcode'},
        {name: 'subproductcode'},
        {name: 'version'},
        {name: 'tsname_in_legend'},
        {name: 'charttype'},
        {name: 'linestyle'},
        {name: 'linewidth', type: 'integer'},
        {name: 'color'},
        {name: 'yaxe_id'}

        // {name: 'title'},
        // {name: 'title_color'},
        // {name: 'unit'},
        // {name: 'min', type: 'number'},
        // {name: 'max', type: 'number'},
        // {name: 'opposite', type: 'boolean'}
        // {name: 'aggregation_type'},
        // {name: 'aggregation_min', type: 'number'},
        // {name: 'aggregation_max', type: 'number'}
    ]
});
