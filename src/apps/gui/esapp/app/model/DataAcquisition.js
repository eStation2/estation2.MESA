Ext.define('esapp.model.DataAcquisition', {
    extend : 'esapp.model.Base',
//    extend: 'Ext.data.Model',
//    alias: 'model.dataacquisitions',

//    idProperty : 'productID',
    fields: [
       {name: 'productID'}, //, reference: { parent: 'ProductAcquisition' }},
       {name: 'productcode'},
       {name: 'subproductcode'},
       {name: 'version'},

       {name: 'data_source_id'},
       {name: 'defined_by'},
       {name: 'type'},
       {name: 'activated', type: 'boolean'},
       {name: 'store_original_data', type: 'boolean'},
       {name: 'latest'},
       {name: 'lenght_proc_list'},
       {name: 'time_latest_copy'},
       {name: 'time_latest_exec'}
    ]

//    ,manyToOne: 'ProductAcquisition'
});