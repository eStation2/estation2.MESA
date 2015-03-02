Ext.define("esapp.view.datamanagement.DataManagement",{
    "extend": "Ext.grid.Panel",
    "controller": "datamanagement-datamanagement",
    "viewModel": {
        "type": "datamanagement-datamanagement"
    },
    xtype  : 'datamanagement-main',

    name:'datamanagementmain',

    requires: [
        'esapp.view.datamanagement.DataManagementModel',
        'esapp.view.datamanagement.DataManagementController',
        'esapp.view.datamanagement.ProductMapSet',
        'esapp.view.datamanagement.MapSetDataSet',

        'Ext.grid.column.Widget',
        'Ext.grid.column.Template',
        'Ext.grid.column.Check',
        'Ext.button.Split',
        'Ext.menu.Menu',
        'Ext.XTemplate',
        'Ext.util.DelayedTask'
    ],

    store: 'DataSetsStore',

    // title: 'Data Management Dashboard',
    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable:false,
        markDirty: false,
        resizable:false,
        disableSelection: true,
        trackOver:true
    },

    bufferedRenderer: false,
    collapsible: false,
    enableColumnMove:false,
    enableColumnResize:false,
    multiColumnSort: false,
    columnLines: false,
    rowLines: true,
    frame: false,
    border: false,

    features: [{
        id: 'prodcat',
        ftype: 'grouping',
        groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
        hideGroupedHeader: true,
        enableGroupingMenu: false,
        startCollapsed : true,
        groupByText: 'Product category'
    }],

    listeners: {
        viewready: function (){
            //this.suspendEvents(true);
            var groupFeature = this.getView().getFeature('prodcat');
            var me = this;
            if ( !this.getStore().isLoaded() ){
                var task = new Ext.util.DelayedTask(function(){
                    if (this.firstGroupKey != 'undefined') {
                        groupFeature.expand(me.firstGroupKey, true);
                    } else {
                        groupFeature.expand("<span style='display: none;'>1</span>Vegetation", true);  // rainfall
                    }
                });
                task.delay(5000);

            } else {
                if (this.firstGroupKey != 'undefined') {
                    groupFeature.expand(me.firstGroupKey, true);
                } else {
                    groupFeature.expand("<span style='display: none;'>1</span>Vegetation", true);  // rainfall
                }
            }
            //this.resumeEvents();
        }
    },

    initComponent: function () {
        var me = this;

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            items: [{
                text: 'Expand All',
                handler: function(btn) {
                    var view = btn.up().up().getView();
                    view.getFeature('prodcat').expandAll();
                    view.refresh();
                }
            }, {
                text: 'Collapse All',
                handler: function(btn) {
                    var view = btn.up().up().getView();
                    view.getFeature('prodcat').collapseAll();
                    view.refresh();
                }
            }, {
                text: 'My requests',
                handler: function(btn) {

                }
            },
            // add a vertical separator bar between toolbar items
            //'-', // same as {xtype: 'tbseparator'} to create Ext.toolbar.Separator
            '->', // same as { xtype: 'tbfill' }
            {
                xtype: 'button',
                iconCls: 'fa fa-refresh fa-2x',
                style: { color: 'gray' },
                enableToggle: false,
                scale: 'medium',
                handler:  function(btn) {
                    var datasetsstore  = Ext.data.StoreManager.lookup('DataSetsStore');

                    if (datasetsstore.isStore) {
                        datasetsstore.load();
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
//            }, {
//                xtype: 'checkcolumn',
//                header: 'Active',
//                width: 65,
//                dataIndex: 'activated',
//                stopSelection: false,
//                hideable: true,
//                hidden:false,
//                disabled: true
            },{
                xtype: 'actioncolumn',
                header: 'Actions',
                width: 70,
                align:'center',
                items: [{
                    icon: 'resources/img/icons/download.png',
                    tooltip: 'Complete all product data sets (all mapsets and its subproducts).',
                    scope: me,
                    handler: function (grid, rowIndex) {
                        Ext.toast({
                            html: 'Show window which proposes places to send a request to complete all product data sets.',
                            title: 'Request to complete all product data sets.',
                            width: 200,
                            align: 't'
                        });
                    }
                }]
            }]
        }, {
            header:  '<div class="grid-header-style">Data set completeness</div>',
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
                width: 1015,
                bodyPadding:0,

                header: ' <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 215px; left: 0px; tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Mapset</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 70px; right: auto; left: 215px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Actions</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 215px; right: auto; left: 285px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Sub Product</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 360px; right: auto; left: 505px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Status</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 70px;  left: 865px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">Actions</span>' +
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
                        model: 'ProductMapSet',
                        data: productmapsets
                    });
                    widget.setStore(newstore);
                    Ext.resumeLayouts(true);
                },
                widget: {
                    xtype: 'productmapsetgrid'
                }
            }]
        }];

        me.callParent();

        me.groupingFeature = me.view.getFeature('prodcat');

        me.mon(me, 'afterrender', me.onAfterRender, me);
    }

    ,onAfterRender: function() {
        var me = this;
        me.getStore().load({
            callback:function(){
                me.firstGroupKey = me.getStore().getGroups().items[0].getGroupKey();
                //me.view.getFeature('prodcat').expand(firstGroupKey, true);
            }
        });
    }
});