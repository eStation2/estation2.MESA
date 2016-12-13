Ext.define('esapp.view.analysis.timeseriesProductSelectionModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-timeseriesproductselection',

    stores: {
        products: {
             model: 'esapp.model.TimeseriesProduct'
            ,session: true
            ,autoLoad: true
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
        },

        productmapsets: {
            model: 'esapp.model.TimeserieProductMapSet'
            ,session: true
        },

        timeseriesmapsetdatasets:{
            model: 'esapp.model.TimeserieProductMapSetDataSet'
            ,session: true
        },

        //,years:{
        //    //model: 'esapp.model.Year'
        //    fields: ['year'],
        //    sorters: {property: 'year', direction: 'DESC'},
        //    data: [
        //        {year: 2000},
        //        {year: 2001},
        //        {year: 2002},
        //        {year: 2003},
        //        {year: 2004},
        //        {year: 2005},
        //        {year: 2006},
        //        {year: 2007},
        //        {year: 2008},
        //        {year: 2009},
        //        {year: 2010},
        //        {year: 2011},
        //        {year: 2012},
        //        {year: 2013},
        //        {year: 2014},
        //        {year: 2015},
        //        {year: 2016},
        //        {year: 2017},
        //        {year: 2018},
        //        {year: 2019},
        //        {year: 2020}
        //    ]
        //}

        timeseriesdrawproperties: {
            model: 'esapp.model.TSDrawProperties',
            autoLoad: true,
            autoSync: true,
            session: true,

            proxy: {
                type: 'rest',

                appendId: false,

                api: {
                    read: 'analysis/gettimeseriesdrawproperties',
                    create: 'analysis/gettimeseriesdrawproperties/create',
                    update: 'analysis/gettimeseriesdrawproperties/update',
                    destroy: 'analysis/gettimeseriesdrawproperties/delete'
                },
                reader: {
                     type: 'json'
                    ,successProperty: 'success'
                    ,rootProperty: 'tsdrawproperties'
                    ,messageProperty: 'message'
                },
                writer: {
                    type: 'json',
                    writeAllFields: true,
                    rootProperty: 'tsdrawproperties'
                },
                listeners: {
                    exception: function(proxy, response, operation){
                        console.info('TIMESERIES DRAW PROPERTIES VIEW MODEL - REMOTE EXCEPTION - Error querying the time series draw properties!');
                    }
                }
            }
            ,listeners: {
                update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
                    // This event is triggered on every change made in a record!
                    //console.info('record updated!');
                },
                write: function(store, operation){
                    var result = Ext.JSON.decode(operation.getResponse().responseText);
                    if (!operation.success) {
                        //console.info(store);
                        //console.info(operation);
                    }
                }
            }
        }
    }

});
