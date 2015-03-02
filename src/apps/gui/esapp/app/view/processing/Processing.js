
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
        'esapp.view.processing.ProductMapSet',
        'esapp.view.processing.MapSetFinalOutputSubProduct',

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

        me.columns = [
        {
            header: '<div class="grid-header-style">Product categories</div>',
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
                xtype:'templatecolumn',
                header: 'Product',
                tpl: new Ext.XTemplate(
                        '<b>{prod_descriptive_name}</b>' +
                        '<tpl if="version != \'undefined\'">',
                            '<b class="smalltext"> - {version}</b>',
                        '</tpl>',
                        '</br><span class="smalltext">' +
                        '<b style="color:darkgrey">{productcode}</b>' +
                        '<p>{description}</p>' +
                        '</span></br>'
                    ),
                width: 450,
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
                        if (rec.get('activated')) {
                            return 'activated';
                        } else {
                            return 'deactivated';
                        }
                    },
                    getTip: function(v, meta, rec) {
                        if (rec.get('activated')) {
                            return 'Deactivate Product';
                        } else {
                            return 'Activate Product';
                        }
                    },
                    handler: function(grid, rowIndex, colIndex) {
                        var rec = grid.getStore().getAt(rowIndex),
                            action = (rec.get('activated') ? 'deactivated' : 'activated');
                        //Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                        rec.get('activated') ? rec.set('activated', false) : rec.set('activated', true);
                    }
                }]
//            },{
//                xtype: 'checkcolumn',
//                header: 'Active',
//                width: 65,
//                dataIndex: 'activated',
//                stopSelection: false,
//                hideable: true,
//                hidden:false,
//                disabled: false,
//                listeners: {
//                  checkchange: function(chkBox, rowIndex, checked, eOpts){
//                      var myTitle = ""
//                      if (checked)  myTitle = "Activate Processing Chain";
//                      else myTitle = "De-activate Processing Chain";
//                      Ext.toast({ html: 'Checkbox clicked!', title: myTitle, width: 200, align: 't' });
//                  }
//                }
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
                width: 500,
                bodyPadding:0,

                header: ' <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 210px; left: 0px; tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Mapset</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 190px; right: auto; left: 210px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Sub Product</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 70px;  left: 400px; margin: 0px; top: 0px;" tabindex="-1">' +
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
                    var productmapsets = record.getData().productmapsets;
                    var newstore = Ext.create('Ext.data.JsonStore', {
                        model: 'ProcessingProductMapSet',
                        data: productmapsets
                    });
                    widget.setStore(newstore);
                    Ext.resumeLayouts(true);
                },
                widget: {
                    xtype: 'process-productmapsetgrid'
                }
            }]
        }];

        me.callParent();
    }
});
