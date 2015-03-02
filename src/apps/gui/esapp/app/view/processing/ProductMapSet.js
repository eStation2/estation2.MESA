
Ext.define("esapp.view.processing.ProductMapSet",{
    "extend": "Ext.grid.Panel",
    "controller": "processing-productmapset",
    "viewModel": {
        "type": "processing-productmapset"
    },

    "xtype"  : 'process-productmapsetgrid',

    requires: [
        'esapp.view.processing.ProductMapSetModel',
        'esapp.view.processing.ProductMapSetController'

        ,'Ext.grid.column.Widget'
    ],

    store : null,

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

        me.defaults = {
            menuDisabled: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false
        };

        me.columns = [{
            header: '', // 'Mapset',
            dataIndex: 'descriptive_name',
            width: 200
        }, {
            header: '',
            xtype: 'widgetcolumn',
            width: 280,
            widget: {
                xtype: 'mapset_finaloutput_subproduct_grid'
                // ,height:80
            },
            onWidgetAttach: function(widget, record) {
                Ext.suspendLayouts();
                var mapset_finaloutput_subproduct = record.getData().mapsetoutputproducts; //mapset_finaloutput_subproduct;
                //console.info(mapset_finaloutput_subproduct);
                var newstore = Ext.create('Ext.data.JsonStore', {
                    model: 'MapSetFinalOutputSubProducts',
                    data: mapset_finaloutput_subproduct
                    ,storeId : 'MapSetFinalOutputSubProductsStore' + mapset_finaloutput_subproduct.datasetID
                    ,autoSync: true
                    ,requires : [
                        'esapp.model.MapSetFinalOutputSubProducts',
                        'Ext.data.proxy.Rest'
                    ]
                    ,proxy: {
                        type: 'rest',
                        appendId: false,
                        api: {
                            read: 'processing',
                            create: 'processing/create',
                            update: 'processing/update',
                            destroy: 'processing/delete'
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
                                    title: 'PROCESSING STORE - REMOTE EXCEPTION',
                                    msg: operation.getError(),
                                    icon: Ext.MessageBox.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        }
                    }
                });
                widget.setStore(newstore);
                Ext.resumeLayouts(true);
            }
        }];

        me.callParent();
    }

});
