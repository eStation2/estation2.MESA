Ext.define('esapp.view.analysis.timeseriesProductSelectionModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-timeseriesproductselection',

    stores: {
        categories: {
            source: 'CategoriesStore',
            session: true
            // ,proxy:{
            //   extraParams: {all: false}
            // }
        },
        products: {
            source: 'TimeseriesProductsStore',
            session: true,

            model: 'esapp.model.TimeseriesProduct'
            //,session: false
            //,autoLoad: false
            ,loadMask: true
            //
            ,sorters: [{property: 'mapsetcode', direction: 'DESC'}]

            ,grouper:{
                     groupFn : function (item) {
                         var version = item.get('version') != 'undefined' ? item.get('version') : '';
                         return item.get('group_product_descriptive_name') + ' - <b class="smalltext" style="color:black">' +  version + ' - ' + item.get('productcode') + '</b>';
                         // return item.get('group_product_descriptive_name');
                         //return esapp.Utils.getTranslation(item.get('category_id'));
                         //return "<span style='display: none;'>" + item.get('order_index') + "</span>" + esapp.Utils.getTranslation(item.get('category_id'))
                         //return item.get('cat_descr_name')
                     },
                     property: 'group_product_descriptive_name'
                     // sortProperty: 'display_index'
                     // sortProperty: 'productmapsetid'
            }
        },

        selectedtimeseriesmapsetdatasets:{
            model: 'esapp.model.SelectedTimeseriesMapSetDataSet'
            ,session: true
        },

        productcolorschemes: {
            model: 'esapp.model.ProductNavigatorDatasetColorScheme',
            session: true
            //fields: [
            //    {name: 'default_legend', mapping: 'default_legend'},
            //    {name: 'defaulticon', mapping: 'defaulticon'},
            //    {name: 'legend_id', mapping: 'legend_id'},
            //    {name: 'legend_name', mapping: 'legend_name'},
            //    {name: 'colorschemeHTML', mapping: 'colorschemeHTML'},
            //    {name: 'legendHTML', mapping: 'legendHTML'},
            //    {name: 'legendHTMLVertical', mapping: 'legendHTMLVertical'}
            //],
            //
            //proxy: {
            //    type: 'ajax',
            //    url: 'analysis/getproductcolorschemes',
            //    //params: params,
            //    //extraParams:{
            //    //    activated:'True'
            //    //},
            //    reader: {
            //        type: 'json',
            //        rootProperty: 'legends',
            //        successProperty: 'success',
            //        messageProperty: 'message'
            //    },
            //
            //    listeners: {
            //        exception: function(proxy, response, operation){
            //            // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
            //            console.info('COLOR SCHEMES MODEL - REMOTE EXCEPTION');
            //            //Ext.Msg.show({
            //            //    title: 'COLOR SCHEMES - REMOTE EXCEPTION',
            //            //    msg: operation.getError(),
            //            //    icon: Ext.Msg.ERROR,
            //            //    buttons: Ext.Msg.OK
            //            //});
            //        }
            //    }
            //
            //}
        },

        timeseriesdrawproperties: {
            // source: 'TSDrawPropertiesStore',
            model: 'esapp.model.TSDrawProperties',
            session: true,
            autoLoad: false,
            autoSync: false,

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
        },

        years:{
            model: 'esapp.model.Year',
            session: true,
            //fields: ['year'],
            sorters: {property: 'year', direction: 'DESC'}
        }

        //productmapsets: {
        //    model: 'esapp.model.TimeserieProductMapSet'
        //    ,session: true
        //},
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
    }

});
