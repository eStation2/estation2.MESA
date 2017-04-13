Ext.define("esapp.view.datamanagement.DataManagement",{
    "extend": "Ext.grid.Panel",
    //"controller": "datamanagement-datamanagement",
    //"viewModel": {
    //    "type": "datamanagement-datamanagement"
    //},
    xtype  : 'datamanagement-main',

    name:'datamanagementmain',

    requires: [
        //'esapp.view.datamanagement.DataManagementModel',
        //'esapp.view.datamanagement.DataManagementController',
        //'esapp.view.datamanagement.ProductMapSet',
        //'esapp.view.datamanagement.MapSetDataSet',
        //'esapp.view.datamanagement.sendRequest',

        'Ext.grid.column.Widget',
        'Ext.grid.column.Action',
        'Ext.grid.column.Template',
        'Ext.XTemplate'
    ],

    store: 'DataSetsStore',
    session: false,

    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable :false,
        markDirty: false,
        resizable: false,
        disableSelection: true,
        trackOver: false
    },
    //selType: 'cellmodel',
    //selModel: {
    //    listeners:{}
    //},

    bufferedRenderer: true,

    collapsible: false,
    enableColumnMove: false,
    enableColumnResize: false,
    multiColumnSort: false,
    columnLines: false,
    rowLines: true,
    frame: false,
    border: false,

    //layout: 'fit',

    features: [{
        id: 'prodcat',
        ftype: 'grouping',
        groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
        hideGroupedHeader: true,
        enableGroupingMenu: false,
        startCollapsed : true,
        groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product category'
    }],

    //listeners: {
    //    cellclick : function(view, cell, cellIndex, record, row, rowIndex, e) {
    //        //e.stopPropagation();
    //        return false;
    //    }
    //},
    //listeners: {
    //    viewready: function (){
    //        //this.suspendEvents(true);
    //        var groupFeature = this.getView().getFeature('prodcat');
    //        var me = this;
    //        //console.info('me.firstGroupKey defined in afterrender In viewready: ' + me.firstGroupKey);
    //
    //        if ( !this.getStore().isLoaded() ){
    //            var task = new Ext.util.DelayedTask(function(){
    //                if (me.firstGroupKey != 'undefined') {
    //                    groupFeature.expand(me.firstGroupKey, true);
    //                } else {
    //                    groupFeature.expand("<span style='display: none;'>1</span>"+esapp.Utils.getTranslation('vegetation'), true);  // rainfall
    //                }
    //            });
    //            task.delay(2000);
    //
    //        } else {
    //            if (me.firstGroupKey != 'undefined') {
    //                groupFeature.expand(me.firstGroupKey, true);
    //            } else {
    //                groupFeature.expand("<span style='display: none;'>1</span>"+esapp.Utils.getTranslation('vegetation'), true);  // rainfall
    //            }
    //        }
    //        //this.resumeEvents();
    //    }
    //},

    initComponent: function () {
        var me = this;

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            items: [{
                text: esapp.Utils.getTranslation('expandall'),    // 'Expand All',
                handler: function(btn) {
                    var view = btn.up().up().getView();
                    view.getFeature('prodcat').expandAll();
                    view.refresh();
                }
            }, {
                text: esapp.Utils.getTranslation('collapseall'),    // 'Collapse All',
                handler: function(btn) {
                    var view = btn.up().up().getView();
                    view.getFeature('prodcat').collapseAll();
                    view.refresh();
                }
            //}, {
            //    text: esapp.Utils.getTranslation('myrequests'),    // 'My requests',
            //    handler: function(btn) {
            //
            //    }
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

        //me.listeners = {
        //    viewready: function(gridpanel,func){
        //        //Ext.toast({ html: 'viewready', title: 'viewready', width: 200, align: 't' });
        //
        //        var task = new Ext.util.DelayedTask(function() {
        //            var view = gridpanel.getView();
        //            view.getFeature('prodcat').expandAll();
        //            view.refresh();
        //        });
        //
        //        task.delay(1000);
        //    }
        //};

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
            header: '<div class="grid-header-style">' + esapp.Utils.getTranslation('productcategories') + '</div>',
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
                header: esapp.Utils.getTranslation('product'),    // 'Product',
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
                header: esapp.Utils.getTranslation('actions'),    // 'Actions',
                width: 70,
                align:'center',
                menuDisabled: true,
                stopSelection: false,
                items: [{
                    icon: 'resources/img/icons/download.png',
                    tooltip: esapp.Utils.getTranslation('tipcompletedatasetall'),    // 'Complete all product data sets (all mapsets and its subproducts).',
                    scope: me,
                    handler: function (grid, rowIndex, colIndex, icon, e, record) {
                        //var rec = grid.getStore().getAt(rowIndex);

                        var sendRequestWin = new esapp.view.datamanagement.sendRequest({
                            params: {
                                level: 'product',
                                record: record
                            }
                        });
                        sendRequestWin.show();
                    }
                }]
            }]
        }, {
            header:  '<div class="grid-header-style">' + esapp.Utils.getTranslation('datasetcompleteness') + '</div>',
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
                //dataIndex: 'productmapsets',
                minWidth: 1025,
                bodyPadding:0,

                header: ' <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 215px; left: 0px; tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('mapset') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 70px; right: auto; left: 215px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('actions') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 215px; right: auto; left: 285px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('subproduct') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 360px; right: auto; left: 505px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('status') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 70px;  left: 865px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('actions') + '</span>' +
                '           </div>' +
                '       </div>',
                listeners: {
                  render: function(column){
                      //column.titleEl.removeCls('x-column-header-inner');
                  }
                },
                widget: {
                    xtype: 'productmapsetgrid',
                    widgetattached: false
                }
                ,onWidgetAttach: function(col,widget, record) {
                    Ext.suspendLayouts();
                    if (!widget.widgetattached) {
                        widget.getStore().setData(record.getData().productmapsets);
                        widget.widgetattached = true;
                    }
                    //me.updateLayout();
                    //var productmapsets = record.getData().productmapsets;
                    //var newstore = Ext.create('Ext.data.JsonStore', {
                    //    model: 'ProductMapSet',
                    //    data: productmapsets
                    //});
                    //widget.setStore(newstore);
                    Ext.resumeLayouts(true);
                }
            }]
        }];

        me.callParent();

        //me.groupingFeature = me.view.getFeature('prodcat');
        //
        //me.mon(me, 'afterrender', me.onAfterRender, me);
    }

    //,onAfterRender: function() {
    //    var me = this;
    //    me.getStore().load({
    //        callback:function(){
    //            me.firstGroupKey = me.getStore().getGroups().items[0].getGroupKey();
    //            //console.info(me.firstGroupKey);
    //            //me.view.getFeature('prodcat').expand(me.firstGroupKey, true);
    //        }
    //    });
    //}
});