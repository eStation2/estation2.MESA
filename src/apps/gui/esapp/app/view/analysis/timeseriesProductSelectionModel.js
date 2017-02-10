Ext.define('esapp.view.analysis.timeseriesProductSelectionModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-timeseriesproductselection',

    stores: {
        categories: {
            source: 'CategoriesStore'
        },
        products: {
            source: 'TimeseriesProductsStore',
            session: true,

            model: 'esapp.model.TimeseriesProduct'
            //,session: false
            //,autoLoad: false
            //,loadMask: true
            //
            ,sorters: {property: 'order_index', direction: 'DESC'}

            ,grouper:{
                     groupFn : function (item) {
                         return item.get('group_product_descriptive_name');
                         //return esapp.Utils.getTranslation(item.get('category_id'));
                         //return "<span style='display: none;'>" + item.get('order_index') + "</span>" + esapp.Utils.getTranslation(item.get('category_id'))
                         //return item.get('cat_descr_name')
                     },
                     property: 'group_product_descriptive_name',
                     sortProperty: 'productmapsetid'
            }
        },

        selectedtimeseriesmapsetdatasets:{
            model: 'esapp.model.SelectedTimeseriesMapSetDataSet'
            ,session: true
        },

        timeseriesdrawproperties: {
            source: 'TSDrawPropertiesStore',
            model: 'esapp.model.TSDrawProperties',
            session: true
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
