Ext.define('esapp.store.TimeseriesProductsStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.timeseriesproducts',

    //requires : [
    //    //'esapp.model.TimeseriesProduct'
    //    'esapp.model.TimeserieProductMapSet',
    //    'esapp.model.TimeserieProductMapSetDataSet'
    //],

    model: 'esapp.model.TimeseriesProduct',

    storeId : 'TimeseriesProductsStore'

    //,session: false
    ,autoLoad: true
    ,loadMask: false

    //,sorters: {property: 'order_index', direction: 'DESC'}
    //
    //,grouper:{
    //         groupFn : function (item) {
    //             return item.get('group_product_descriptive_name');
    //             //return esapp.Utils.getTranslation(item.get('category_id'));
    //             //return "<span style='display: none;'>" + item.get('order_index') + "</span>" + esapp.Utils.getTranslation(item.get('category_id'))
    //             //return item.get('cat_descr_name')
    //         },
    //         property: 'group_product_descriptive_name',
    //         sortProperty: 'productmapsetid'
    //}

    ,proxy: {
        type: 'ajax',
        url: 'analysis/timeseriesproduct',
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'products'
            ,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('TIMESERIES PRODUCT VIEW MODEL - REMOTE EXCEPTION - Reload timeseries product grid!');
            }
        }
    }
});
