Ext.define('esapp.view.analysis.ProductNavigatorModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-productnavigator',

    stores: {
        products: {
            //source: 'ProductNavigatorStore'
            model: 'esapp.model.ProductNavigator'
            ,session: true
            ,autoLoad:false
            ,loadMask: true

            ,sorters: {property: 'order_index', direction: 'DESC'}

            ,grouper:{
                     // property: 'cat_descr_name',
                     groupFn : function (item) {
                         return "<span style='display: none;'>" + item.get('order_index') + "</span>" + item.get('cat_descr_name')
                         //return item.get('cat_descr_name')
                     },
                     sortProperty: 'order_index'
            }
            ,listeners: {
                write: function(store, operation){
                    Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 300, align: 't' });
                }
            }
        },
        productmapsets: {
            model: 'esapp.model.ProductNavigatorMapSet'
            ,session: true
        },
        mapsetdatasets: {
            model: 'esapp.model.ProductNavigatorMapSetDataSet'
            ,session: true
        },
        colorschemes: {
            model: 'esapp.model.ColorScheme'
            ,session: true
        }
    }

    //,links: {
    //    products: {
    //        reference: 'esapp.model.ProductNavigator'
    //        ,create: true
    //        //,id: 1
    //    }
    //}

});
