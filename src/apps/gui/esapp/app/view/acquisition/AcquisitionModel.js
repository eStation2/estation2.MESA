Ext.define('esapp.view.acquisition.AcquisitionModel', {
     extend: 'Ext.app.ViewModel'
    ,alias: 'viewmodel.acquisition'

//    ,stores: {
//        products: {
//             source: 'ProductsActiveStore'
//             model: 'esapp.model.ProductAcquisition'
//            ,session: true
//            ,autoLoad: true
//            ,remoteSort: false
//            ,remoteGroup: false
//            ,grouper:{
//                     // property: 'cat_descr_name',
//                     groupFn : function (item) {
//                         return "<span style='display: none;'>" + item.get('order_index') + "</span>" + item.get('cat_descr_name')
////                                "</span><span class='group-header-style'>" + item.get('cat_descr_name') + "</span>"
//                     },
//                     sortProperty: 'order_index'
//            }
//            ,filters: [ {
//                 property:'activated'
//                ,value:true
//                ,anyMatch:true
//            }]
            // ,sorters: {property: 'order_index', direction: 'ASC'}
            // ,groupField: 'cat_descr_name'
            // ,groupDir:'ASC'
//        }
//    }
});
