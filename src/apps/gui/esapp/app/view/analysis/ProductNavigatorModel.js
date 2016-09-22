Ext.define('esapp.view.analysis.ProductNavigatorModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-productnavigator',

    stores: {
        products: {
            model: 'esapp.model.ProductNavigator'
            ,session: true
            ,autoLoad:false
            ,loadMask: true

            ,sorters: {property: 'order_index', direction: 'DESC'}

            ,grouper:{
                groupFn : function (item) {
                    return esapp.Utils.getTranslation(item.get('category_id'));
                    //return "<span style='display: none;'>" + item.get('order_index') + "</span>" + esapp.Utils.getTranslation(item.get('category_id'))
                 //return item.get('cat_descr_name')
                },
                property: 'order_index',
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
            model: 'esapp.model.ProductNavigatorMapSetDataSet',
            sorters: [{
                property: 'subproductcode',
                direction: 'ASC'
            }],
            //sortRoot: 'prod_descriptive_name',
            //sortOnLoad: true,
            //remoteSort: false,
            session: true
        },
        colorschemes: {
            model: 'esapp.model.ColorScheme'
            ,session: true
        }
    }
});
