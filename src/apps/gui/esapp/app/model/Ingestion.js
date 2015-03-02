Ext.define('esapp.model.Ingestion', {
    extend : 'esapp.model.Base',

    // idProperty : 'productID',
    fields: [
       {name: 'productID'}, // , reference: { parent: 'ProductAcquisition' }},
       {name: 'productcode'},
       {name: 'subproductcode'},
       {name: 'version'},
       {name: 'mapsetcode'},
       {name: 'defined_by'},
       {name: 'activated', type: 'boolean'},
       {name: 'mapsetname'},
       {name: 'completeness_id', mapping:'productID'}
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
       {name: 'id', mapping:'productID'},
       {name: 'firstdate'},
       {name: 'lastdate'},
       {name: 'totfiles'},
       {name: 'missingfiles'}
    ]
    ,hasMany:[
        { model: 'esapp.model.Intervals', name: 'intervals'}
    ]
});

Ext.define('esapp.model.Intervals', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'fromdate'},
       {name: 'todate'},
       {name: 'intervaltype'},
       {name: 'intervalpercentage', type:'int'}
    ]
});
