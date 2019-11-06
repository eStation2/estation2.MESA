
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
    bufferedRenderer: false,

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

    //selModel: {listeners:{}},

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
        startCollapsed : true,
        groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product category'
    }],

    //listeners: {
        //beforecellclick: function(view, td, cellIndex) {
        //    console.info('hallo cell: ' + cellIndex);
        //    if (cellIndex > 0) return false;    // check the cellIndex for whatever columns you need.
        //}
        //cellclick : function(view, cell, cellIndex, record, row, rowIndex, e) {
        //    //e.stopPropagation();
        //    //console.info('cellclick');
        //    return false;
        //}
    //},

    initComponent: function () {
        var me = this;

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            items: [{
                tooltip: esapp.Utils.getTranslation('expandall'),    // 'Expand All',
                iconCls: 'expand',
                scale: 'medium',
                handler: function(btn) {
                    var view = btn.up().up().getView();
                    view.getFeature('processprodcat').expandAll();
                    view.refresh();
                }
            }, {
                tooltip: esapp.Utils.getTranslation('collapseall'),    // 'Collapse All',
                iconCls: 'collapse',
                scale: 'medium',
                handler: function(btn) {
                    var view = btn.up().up().getView();
                    view.getFeature('processprodcat').collapseAll();
                    view.refresh();
                }
            }, '->',
            {
                xtype: 'servicemenubutton',
                service: 'processing',
                text: esapp.Utils.getTranslation('processing'),    // 'Processing',
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
                        processingstore.proxy.extraParams = {force: true};
                        processingstore.load();
                    }
                }
            }]
        });

        me.defaults = {
            variableRowHeight : true,
            menuDisabled: true,
            sortable: false,
            groupable:false,
            draggable:false,
            hideable: false,
            stopSelection: true
        };

        me.columns = [{
            header: '<div class="grid-header-style">' + esapp.Utils.getTranslation('processinginputs') + '</div>',
            menuDisabled: true,
            variableRowHeight: true,
            defaults: {
                menuDisabled: true,
                variableRowHeight: true,
                sortable: false,
                groupable: false,
                draggable: false,
                hideable: false,
                stopSelection: true
            },
            columns: [{
                xtype: 'widgetcolumn',
                width: 625,
                bodyPadding: 0,

                header: ' <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 260px; left: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('product') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 150px; right: auto; left: 260px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('subproduct') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 200px;  left: 410px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('mapset') + '</span>' +
                //'               <span data-ref="textEl" class="x-column-header-text"' + esapp.Utils.getTranslation('mapset') + '></span>' +
                '           </div>' +
                '       </div>',
                listeners: {
                    render: function (column) {
                        column.titleEl.removeCls('x-column-header-inner');
                    }
                },
                widget: {
                    xtype: 'process-inputproductgrid',
                    widgetattached: false
                },
                onWidgetAttach: function (col, widget, record) {
                    // console.info('inputproducts');
                    // console.info(record);
                    if (!widget.widgetattached) {
                        Ext.suspendLayouts();

                        var inputproducts = record.getData().inputproducts;
                        // console.info(inputproducts);
                        var newstore = Ext.create('Ext.data.JsonStore', {
                            model: 'InputProducts',
                            data: inputproducts
                        });
                        widget.setStore(newstore);
                        widget.widgetattached = true;

                        Ext.resumeLayouts(true);
                    }
                }
            }]
        },{
            header: '<div class="grid-header-style">' + esapp.Utils.getTranslation('algorithm') + '</div>',
            menuDisabled: true,
            variableRowHeight : true,
            defaults: {
                menuDisabled: true,
                variableRowHeight : true,
                sortable: false,
                groupable:false,
                draggable:false,
                hideable: false,
                stopSelection: true
            },
            columns: [{
                header: esapp.Utils.getTranslation('type'),    // 'Type',
                width: 150,
                dataIndex: 'algorithm',
                cellWrap:true
            },{
                header: esapp.Utils.getTranslation('options'),    // 'Options',
                width: 150,
                dataIndex: 'derivation_method',
                cellWrap:true
            },{
                xtype: 'actioncolumn',
                header: esapp.Utils.getTranslation('active'),    // 'Active',
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
                            return  esapp.Utils.getTranslation('deactivateprocess');   // 'Deactivate Process';
                        } else {
                            return  esapp.Utils.getTranslation('activateprocess');   // 'Activate Process';
                        }
                    },
                    handler: function(grid, rowIndex, colIndex, icon, e, record) {
                        var rec = record,   // grid.getStore().getAt(rowIndex),
                        action = (rec.get('process_activated') ? 'deactivated' : 'activated');
                        //console.info(rec);
                        rec.get('process_activated') ? rec.set('process_activated', false) : rec.set('process_activated', true);
                    }
                }]
            },{
                xtype: 'actioncolumn',
                text: esapp.Utils.getTranslation('log'),    // 'Log',
                id: 'processinglogcolumn',
                width: 75,
                height:40,
                menuDisabled: true,
                align:'center',
                stopSelection: false,
                // cls:'x-grid3-td-ingestionlogcolumn',
                items: [{
                    //icon: 'resources/img/icons/file-extension-log-icon-32x32.png',
                    iconCls:'log-icon',
                    width:32,
                    height:32,
                    tooltip: esapp.Utils.getTranslation('showprocessinglog'),     // 'Show log of this Ingestion',
                    scope: me,
                    handler: function (grid, rowIndex, colIndex, icon, e, record) {
                        var logViewWin = new esapp.view.acquisition.logviewer.LogView({
                            params: {
                                logtype: 'processing',
                                record: record
                            }
                        });
                        logViewWin.show();
                    }
                }]
            }]
        }, {
            header:  '<div class="grid-header-style">' + esapp.Utils.getTranslation('processingoutputs') + '</div>',
            menuDisabled: true,
            variableRowHeight : true,
            defaults: {
                menuDisabled: true,
                variableRowHeight : true,
                sortable: false,
                groupable:false,
                draggable:false,
                hideable: false,
                stopSelection: true
            }
            ,columns: [{
                xtype: 'widgetcolumn',
                width: 600,
                bodyPadding:0,

                header: ' <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 200px; left: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('subproductname') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 200px; right: auto; left: 200px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('mapset') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 200px; right: auto; left: 400px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('subproductcode') + '</span>' +
                '           </div>' +
                //'       </div>' +
                //'       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 70px;  left: 600px; margin: 0px; top: 0px;" tabindex="-1">' +
                //'           <div data-ref="titleEl" class="x-column-header-inner">' +
                //'               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('active') + '</span>' +
                //'           </div>' +
                '       </div>',
                listeners: {
                  render: function(column){
                      column.titleEl.removeCls('x-column-header-inner');
                  }
                },
                widget: {
                    xtype: 'process-finaloutputsubproducts-grid',
                    widgetattached: false
                },
                onWidgetAttach: function(col, widget, record) {
                    // console.info('outputproducts');
                    // console.info(record);
                    if (!widget.widgetattached) {
                        Ext.suspendLayouts();

                        var processrec = record.getData();
                        var outputproducts = processrec.outputproducts;

                        var newstore = Ext.create('Ext.data.JsonStore', {
                            model: 'OutputProducts',
                            data: outputproducts
                        });
                        widget.setStore(newstore);
                        widget.widgetattached = true;

                        Ext.resumeLayouts(true);
                    }
                }
            }]
        }];

        me.callParent();
    }
});
