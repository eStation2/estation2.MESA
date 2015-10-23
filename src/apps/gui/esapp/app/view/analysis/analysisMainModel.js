Ext.define('esapp.view.analysis.analysisMainModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-analysismain',

    stores: {
        products: {
            model: 'esapp.model.TimeseriesProduct'
            ,session: true
            ,autoLoad:false
            ,loadMask: true

            ,sorters: {property: 'order_index', direction: 'DESC'}

            ,grouper:{
                     // property: 'cat_descr_name',
                     groupFn : function (item) {
                         return "<span style='display: none;'>" + item.get('order_index') + "</span>" + esapp.Utils.getTranslation(item.get('category_id'))
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
            model: 'esapp.model.TimeserieProductMapSet'
            ,session: true
        },
        timeseriesmapsetdatasets:{
            model: 'esapp.model.TimeserieProductMapSetDataSet'
            ,session: true
        },
        years:{
            //model: 'esapp.model.Year'
            fields: ['year'],
            data: [
                {year: 2000},
                {year: 2001},
                {year: 2002},
                {year: 2003},
                {year: 2004},
                {year: 2005},
                {year: 2006},
                {year: 2007},
                {year: 2008},
                {year: 2009},
                {year: 2010},
                {year: 2011},
                {year: 2012},
                {year: 2013},
                {year: 2014},
                {year: 2015}
            ]
        }
    }

});
