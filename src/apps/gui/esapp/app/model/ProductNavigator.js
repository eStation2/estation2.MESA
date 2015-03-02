Ext.define('esapp.model.ProductNavigator', {
    extend : 'esapp.model.Base',

//    idProperty : 'productID',
    fields: [
       {name: 'productID', type: 'string', mapping: 'productID'},
       {name: 'productcode', mapping: 'productcode'},
       {name: 'subproductcode', mapping: 'subproductcode'},
       {name: 'version', mapping: 'version'},
       {name: 'defined_by', mapping: 'defined_by'},
       {name: 'product_type', mapping: 'product_type'},
       {name: 'activated', type: 'boolean', mapping: 'activated'},
       {name: 'prod_descriptive_name', mapping: 'prod_descriptive_name'},
       {name: 'description', mapping: 'description'},
       {name: 'category_id', mapping: 'category_id'},
       {name: 'cat_descr_name', mapping: 'cat_descr_name'},
       {name: 'order_index', mapping: 'order_index'}
    ]

    ,autoLoad: true
    ,autoSync: false
    ,remoteSort: false
    ,remoteGroup: false
    ,loadMask: true

    ,proxy: {
        type: 'rest',
        // url: '',
        appendId: false,
        actionMethods: {
            create: 'POST',
            read: 'GET',
            update: 'POST',
            destroy: 'POST'
        },
        api: {
            read: 'analysis/productnavigator',
            create: 'analysis/productnavigator/create',
            update: 'analysis/productnavigator/update',
            destroy: 'analysis/productnavigator/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'products'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'products'
        },
        listeners: {
            exception: function(proxy, response, operation){
                Ext.MessageBox.show({
                    title: 'PRODUCT NAVIGATOR STORE - REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.MessageBox.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }

});


Ext.define('esapp.model.ProductNavigatorMapSet', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'productID', reference:'ProductNavigator', type: 'string'},
        {name: 'mapsetcode'},
        {name: 'defined_by'},
        {name: 'descriptive_name'},
        {name: 'description'},
        {name: 'srs_wkt'},
        {name: 'upper_left_long'},
        {name: 'pixel_shift_long'},
        {name: 'rotation_factor_long'},
        {name: 'upper_left_lat'},
        {name: 'pixel_shift_lat'},
        {name: 'rotation_factor_lat'},
        {name: 'pixel_size_x'},
        {name: 'pixel_size_y'},
        {name: 'footprint_image'}
    ]
});


Ext.define('esapp.model.ProductNavigatorMapSetDataSet', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'mapsetcode', reference:'ProductNavigatorMapSet'},
       {name: 'datasetID'},
       {name: 'productcode'},
       {name: 'subproductcode'},
       {name: 'version'},
       {name: 'defined_by'},
       {name: 'mapsetcode'},
       {name: 'activated', type: 'boolean'},
       {name: 'product_type'},
       {name: 'prod_descriptive_name'},
       {name: 'description'}
        ,{name: 'datasetcompleteness_id', mapping:'datasetID'}
    ]
    ,associations:[
        {
            type: 'hasOne',
            model: 'ProductNavigatorDataSetCompleteness',
            name : 'productnavigatordatasetcompleteness'
        }
    ]
});


Ext.define('esapp.model.ProductNavigatorDataSetCompleteness', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'id', mapping:'datasetID'},
       {name: 'firstdate'},
       {name: 'lastdate'},
       {name: 'totfiles'},
       {name: 'missingfiles'}
    ]
    ,associations:[
        {
            type: 'hasMany',
            model: 'ProductNavigatorDataSetIntervals',
            name: 'productnavigatordatasetintervals'
        }
    ]
});


Ext.define('esapp.model.ProductNavigatorDataSetIntervals', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'fromdate'},
       {name: 'todate'},
       {name: 'intervaltype'},
       {name: 'intervalpercentage', type:'int'}
    ]
});


Ext.define('esapp.model.ColorScheme', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'defaultlegend', mapping: 'defaultlegend'},
        {name: 'defaulticon', mapping: 'defaulticon'},
        {name: 'legend_id', mapping: 'legend_id'},
        {name: 'legendname', mapping: 'legendname'},
        {name: 'colorscheme', mapping: 'colorscheme'},
        {name: 'legendhtml', mapping: 'legendhtml'}
    ],

    proxy: {
        type: 'ajax',
        url: 'analysis/getcolorschemes',
        //params: params,
        //extraParams:{
        //    activated:'True'
        //},
        reader: {
            type: 'json',
            rootProperty: 'colorscheme',
            successProperty: 'success',
            messageProperty: 'message'
        },

        listeners: {
            exception: function(proxy, response, operation){
                Ext.MessageBox.show({
                    title: 'COLOR SCHEMES - REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.MessageBox.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }

    }
});
