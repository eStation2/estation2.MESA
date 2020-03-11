Ext.define('esapp.model.DataAcquisition', {
    extend : 'esapp.model.Base',
    //alias: 'model.dataacquisitions',

    //idProperty : 'productid',
    fields: [
       {name: 'productid'}, //, reference: { parent: 'ProductAcquisition' }},
       {name: 'productcode'},
       {name: 'subproductcode'},
       {name: 'version'},

       {name: 'data_source_id'},
       {name: 'defined_by'},
       {name: 'type'},
       {name: 'activated', type: 'boolean'},
       {name: 'store_original_data', type: 'boolean'},
       {name: 'latest'},
       {name: 'length_proc_list'},
       {name: 'time_latest_copy'},
       {name: 'time_latest_exec'}
    ]

    //,manyToOne: 'ProductAcquisition'
});