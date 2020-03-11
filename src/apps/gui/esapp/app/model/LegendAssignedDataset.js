Ext.define('esapp.model.LegendAssignedDataset', {
    extend: 'esapp.model.Base',

    fields: [
        {name: 'legend_id', type:'number'},
        {name: 'productcode', type:'string'},
        {name: 'subproductcode', type:'string'},
        {name: 'version', type:'string'},
        {name: 'default_legend', type:'boolean'},
        {name: 'descriptive_name', type:'string'},
        {name: 'description', type:'string'}
    ]
});
