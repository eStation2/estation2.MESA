Ext.define('esapp.model.Ingestion', {
    extend : 'esapp.model.Base',

    // idProperty : 'productid',
    fields: [
       {name: 'productid'}, // , reference: { parent: 'ProductAcquisition' }},
       {name: 'productcode'},
       {name: 'subproductcode'},
       {name: 'version'},
       {name: 'mapsetcode'},
       {name: 'defined_by'},
       {name: 'activated', type: 'boolean'},
       {name: 'mapsetname'},
       {name: 'datasetcompletenessimage'},
       {name: 'completeness_id', mapping:'productid'}
    ]
    ,associations:[
        {
            type: 'hasOne',
            model: 'esapp.model.Completeness',
            name : 'completeness'
        }
    ]
});

Ext.define('esapp.model.Completeness', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'id', mapping:'productid'},
       {name: 'firstdate'},
       {name: 'lastdate'},
       {name: 'totfiles'},
       {name: 'missingfiles'},
       {name: 'interval_id', mapping:'productid'}
    ]
    ,hasMany:[
        { model: 'esapp.model.Intervals', name: 'intervals'}
    ]
});

Ext.define('esapp.model.Intervals', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'id', mapping:'productid'},
       {name: 'fromdate'},
       {name: 'todate'},
       {name: 'intervaltype'},
       {name: 'intervalpercentage', type:'int'}
    ]
});
