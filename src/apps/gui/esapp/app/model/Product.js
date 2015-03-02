Ext.define('esapp.model.Product', {
    extend : 'esapp.model.Base',
//    extend: 'Ext.data.Model',

    idProperty : 'productID',
    fields: [
       {name: 'productID'},
       {name: 'productcode'},
       {name: 'subproductcode'},
       {name: 'version'},
       {name: 'defined_by'},
       {name: 'product_type'},
       {name: 'activated', type: 'boolean'},
       {name: 'prod_descriptive_name'},
       {name: 'description'},
       {name: 'category_id'},
       {name: 'cat_descr_name'},
       {name: 'order_index'}
    ]

//    ,grouper:{
//             // property: 'cat_descr_name',
//             groupFn : function (item) {
//                 return "<span style='display: none;'>" + item.get('order_index') + "</span>" + item.get('cat_descr_name')
//                        // "</span><span class='group-header-style'>" + item.get('cat_descr_name') + "</span>"
//             },
//             sortProperty: 'order_index'
//    }

//    ,proxy: {
//        type: 'ajax',
//        url: 'pa',
////        extraParams:{
////            activated:'True'
////        },
//        reader: {
//            type: 'json'
//            ,rootProperty: 'products'
//        }
//    }

//    ,hasMany: [{
//        model: 'DataAcquisition'
//        ,storeConfig: {
//            type: 'dataacquisitions'
//        }
//	}]

//    ,oneToMany: 'DataAcquisition'

//    requires:[
//        'esapp.model.DataAcquisition'
//    ],
//
//    hasMany:[
//        {
//            foreignKey: 'productID',
//            associationKey: 'dataacquisitions',
//            name: 'dataacquisitions',
//            model: 'esapp.model.DataAcquisition'
//        }
//    ]

//    associations: [{
//        model: 'DataAcquisition',
//        type: 'hasMany',
//        autoLoad: true
//    }]
//    ,hasMany: 'DataAcquisition'
});