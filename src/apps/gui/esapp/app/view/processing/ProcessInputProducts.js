
Ext.define("esapp.view.processing.ProcessInputProducts",{
    "extend": "Ext.grid.Panel",
    "controller": "processing-inputproduct",
    "viewModel": {
        "type": "processing-inputproduct"
    },

    "xtype"  : 'process-inputproductgrid',

    requires: [
        'esapp.view.processing.ProcessInputProductsModel',
        'esapp.view.processing.ProcessInputProductsController'
    ],

    store : null,

    cls: 'grid-color-yellow',

    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable: false,
        markDirty: false,
        resizable: false,
        disableSelection: true,
        trackOver: false
    },
    hideHeaders: true,
    columnLines: false,
    rowLines:false,

    initComponent: function () {
        var me = this;

        //me.listeners = {
        //    afterrender: function(grid){
        //        // prevent bubbling of the events
        //        grid.getEl().swallowEvent([
        //            'mousedown', 'mouseup', 'click',
        //            'contextmenu', 'mouseover', 'mouseout',
        //            'dblclick', 'mousemove'
        //        ]);
        //    }
        //};

        me.defaults = {
            menuDisabled: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false
        };

        me.columns = [{
            xtype:'templatecolumn',
            header: '', // 'Productcode',
            tpl: new Ext.XTemplate(
                    '<b>{productcode}</b>' +
                    '<tpl if="version != \'undefined\'">',
                        '<b> - {version}</b>',
                    '</tpl>',
                    '</br>' +
                    '<b class="smalltext" style="color:darkgrey;">{prod_descriptive_name}</b>' +
                    '</br>'
                ),
            width: 250,
            cellWrap:true
        }, {
            header: '', // 'Subproductcode',
            dataIndex: 'subproductcode',
            width: 150
        }, {
            header: '', // 'Mapsetcode',
            dataIndex: 'mapsetcode',
            width: 200
        //}, {
        //    header: '',
        //    xtype: 'widgetcolumn',
        //    width: 280,
        //    widget: {
        //        xtype: 'mapset_finaloutput_subproduct_grid'
        //        // ,height:80
        //    },
        //    onWidgetAttach: function(widget, record) {
        //        Ext.suspendLayouts();
        //        var mapset_finaloutput_subproduct = record.getData().mapsetoutputproducts; //mapset_finaloutput_subproduct;
        //        //console.info(mapset_finaloutput_subproduct);
        //        var newstore = Ext.create('Ext.data.JsonStore', {
        //            model: 'MapSetFinalOutputSubProducts',
        //            data: mapset_finaloutput_subproduct
        //            ,storeId : 'MapSetFinalOutputSubProductsStore' + mapset_finaloutput_subproduct.datasetID
        //            ,autoSync: true
        //            ,requires : [
        //                'esapp.model.MapSetFinalOutputSubProducts',
        //                'Ext.data.proxy.Rest'
        //            ]
        //            ,proxy: {
        //                type: 'rest',
        //                appendId: false,
        //                api: {
        //                    read: 'processing',
        //                    create: 'processing/create',
        //                    update: 'processing/update',
        //                    destroy: 'processing/delete'
        //                },
        //                reader: {
        //                     type: 'json'
        //                    ,successProperty: 'success'
        //                    ,rootProperty: 'products'
        //                    ,messageProperty: 'message'
        //                },
        //                writer: {
        //                    type: 'json',
        //                    writeAllFields: true,
        //                    rootProperty: 'products'
        //                },
        //                listeners: {
        //                    exception: function(proxy, response, operation){
        //                        Ext.Msg.show({
        //                            title: 'PROCESSING STORE - REMOTE EXCEPTION',
        //                            msg: operation.getError(),
        //                            icon: Ext.Msg.ERROR,
        //                            buttons: Ext.Msg.OK
        //                        });
        //                    }
        //                }
        //            }
        //        });
        //        widget.setStore(newstore);
        //        Ext.resumeLayouts(true);
        //    }
        }];

        me.callParent();
    }

});
