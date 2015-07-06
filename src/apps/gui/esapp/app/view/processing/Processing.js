
Ext.define("esapp.view.processing.Processing",{
    "extend": "Ext.grid.Panel",
    "controller": "processing-processing",
    "viewModel": {
        "type": "processing-processing"
    },
    xtype  : 'processing-main',

    name:'processingmain',

    requires: [
        'esapp.view.processing.ProcessingModel',
        'esapp.view.processing.ProcessingController',
        'esapp.view.processing.ProcessInputProducts',
        'esapp.view.processing.ProcessFinalOutputSubProducts',

        'Ext.grid.column.Widget',
        'Ext.grid.column.Template',
        'Ext.grid.column.Check',
        'Ext.button.Split',
        'Ext.menu.Menu',
        'Ext.XTemplate'
    ],

    store: 'ProcessingStore',

    // title: 'Processing Dashboard',
    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable:false,
        markDirty: false,
        resizable:false,
        disableSelection: true,
        trackOver:true
    },

    collapsible: false,
    enableColumnMove:false,
    enableColumnResize:false,
    multiColumnSort: false,
    columnLines: false,
    rowLines: true,
    frame: false,
    border: false,

    features: [{
        id: 'processprodcat',
        ftype: 'grouping',
        groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
        hideGroupedHeader: true,
        enableGroupingMenu: false,
        startCollapsed : false,
        groupByText: 'Product category'
    }],

    initComponent: function () {
        var me = this;

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            items: [{
                text: 'Expand All',
                handler: function(btn) {
                    var view = btn.up().up().getView();
                    view.getFeature('processprodcat').expandAll();
                    view.refresh();
                }
            }, {
                text: 'Collapse All',
                handler: function(btn) {
                    var view = btn.up().up().getView();
                    view.getFeature('processprodcat').collapseAll();
                    view.refresh();
                }
            }, '->',
            {
                xtype: 'servicemenubutton',
                service: 'processing',
                text: 'Processing',
                handler: 'checkStatusServices',
                listeners : {
                    afterrender: 'checkStatusServices'
                }
            },
            '->',
            {
                xtype: 'button',
                iconCls: 'fa fa-refresh fa-2x',
                style: { color: 'gray' },
                enableToggle: false,
                scale: 'medium',
                handler:  function(btn) {
                    var processingstore  = Ext.data.StoreManager.lookup('ProcessingStore');

                    if (processingstore.isStore) {
                        processingstore.load();
                    }
                }
            }]
        });

        me.defaults = {
            variableRowHeight : true,
            menuDisabled: true,
            sortable: false,
            groupable:true,
            draggable:false,
            hideable: true
        };

        me.columns = [{
            header: '<div class="grid-header-style">Processing inputs</div>',
            menuDisabled: true,
            variableRowHeight: true,
            defaults: {
                menuDisabled: true,
                variableRowHeight: true,
                sortable: false,
                groupable: true,
                draggable: false,
                hideable: true
            },
            columns: [{
                xtype: 'widgetcolumn',
                width: 625,
                bodyPadding: 0,

                header: ' <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 260px; left: 0px; tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Product</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 150px; right: auto; left: 260px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Sub Product</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 200px;  left: 410px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Mapset</span>' +
                '           </div>' +
                '       </div>',
                listeners: {
                    render: function (column) {
                        column.titleEl.removeCls('x-column-header-inner');
                    }
                },
                onWidgetAttach: function (widget, record) {
                    Ext.suspendLayouts();
                    var inputproducts = record.getData().inputproducts;
                    var newstore = Ext.create('Ext.data.JsonStore', {
                        model: 'InputProducts',
                        data: inputproducts
                    });
                    widget.setStore(newstore);
                    Ext.resumeLayouts(true);
                },
                widget: {
                    xtype: 'process-inputproductgrid'
                }
            }]
        },{
            header: '<div class="grid-header-style">Algorithm</div>',
            menuDisabled: true,
            variableRowHeight : true,
            defaults: {
                menuDisabled: true,
                variableRowHeight : true,
                sortable: false,
                groupable:true,
                draggable:false,
                hideable: true
            },
            columns: [{
                header: 'Type',
                width: 150,
                dataIndex: 'algorithm',
                cellWrap:true
            },{
                header: 'Options',
                width: 150,
                cellWrap:true
            },{
                xtype: 'actioncolumn',
                header: 'Active',
                hideable: false,
                hidden: false,
                width: 65,
                align: 'center',
                shrinkWrap: 0,
                items: [{
                    // scope: me,
                    // handler: me.onToggleActivation
                    getClass: function(v, meta, rec) {
                        if (rec.get('process_activated')) {
                            return 'activated';
                        } else {
                            return 'deactivated';
                        }
                    },
                    getTip: function(v, meta, rec) {
                        if (rec.get('process_activated')) {
                            return 'Deactivate Product';
                        } else {
                            return 'Activate Product';
                        }
                    },
                    handler: function(grid, rowIndex, colIndex) {
                        var rec = grid.getStore().getAt(rowIndex),
                            action = (rec.get('process_activated') ? 'deactivated' : 'activated');
                        //Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                        rec.get('process_activated') ? rec.set('process_activated', false) : rec.set('process_activated', true);
                    }
                }]
            }]
        }, {
            header:  '<div class="grid-header-style">Processing outputs</div>',
            menuDisabled: true,
            variableRowHeight : true,
            defaults: {
                menuDisabled: true,
                variableRowHeight : true,
                sortable: false,
                groupable:true,
                draggable:false,
                hideable: true
            }
            ,columns: [{
                xtype: 'widgetcolumn',
                width: 700,
                bodyPadding:0,

                header: ' <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 250px; left: 0px; tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Product</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 200px; right: auto; left: 250px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Mapset</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 150px; right: auto; left: 450px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Sub Product</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 70px;  left: 600px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Active</span>' +
                '           </div>' +
                '       </div>',
                listeners: {
                  render: function(column){
                      column.titleEl.removeCls('x-column-header-inner');
                  }
                },
                onWidgetAttach: function(widget, record) {
                    Ext.suspendLayouts();
                    var processrec = record.getData();
                    var outputproducts = processrec.outputproducts;

                    var newstore = Ext.create('Ext.data.JsonStore', {
                        model: 'OutputProducts',
                        data: outputproducts
                        ,storeId : 'OutputProductsStore' + processrec.process_id
                        ,autoSync: true
                        ,requires : [
                            'esapp.model.OutputProducts'
                            //'Ext.data.proxy.Rest'
                        ]
                        ,proxy: {
                            type: 'ajax',
                            url:'processing/update',
                            appendId: false,
                            //api: {
                            //    read: 'processing'
                            //    ,create: 'processing/create'
                            //    ,update: 'processing/update'
                            //    ,destroy: 'processing/delete'
                            //},
                            //reader: {
                            //     type: 'json'
                            //    ,successProperty: 'success'
                            //    ,rootProperty: 'process'
                            //    ,messageProperty: 'message'
                            //},
                            writer: {
                                type: 'json',
                                writeAllFields: false,
                                allowSingle : true,
                                encode: false,
                                rootProperty: 'processoutputproduct',
                                allDataOptions: {
                                    associated: false,
                                    changes: true,
                                    critical: true
                                }
                            },
                            listeners: {
                                exception: function(proxy, response, operation){
                                    Ext.MessageBox.show({
                                        title: 'PROCESSING OUTPUT PRODUCTS STORE - REMOTE EXCEPTION',
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
                },
                widget: {
                    xtype: 'process-finaloutputsubproducts-grid'
                }
            }]
        }];

        me.callParent();
    }
});
