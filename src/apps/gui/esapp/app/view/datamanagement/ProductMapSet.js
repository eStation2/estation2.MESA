
Ext.define("esapp.view.datamanagement.ProductMapSet",{
    "extend": "Ext.grid.Panel",

    //"controller": "datamanagement-productmapset",
    //
    //"viewModel": {
    //    "type": "datamanagement-productmapset"
    //},

    "xtype"  : 'productmapsetgrid',

    requires: [
        //'esapp.view.datamanagement.ProductMapSetModel',
        //'esapp.view.datamanagement.ProductMapSetController'

        ,'Ext.grid.column.Widget'
        ,'Ext.grid.column.Action'
    ],
    store : {
        model: 'ProductMapSet'
    },
    // session: false,

    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable: false,
        markDirty: false,
        resizable: false,
        disableSelection: true,
        trackOver: false,
        preserveScrollOnRefresh: false,
        preserveScrollOnReload: false,
        focusable: false,
        forceFit: false
    },

    // selType: 'cellmodel',
    // selModel: {listeners:{}},
    // selModel: null,

    // bufferedRenderer: true,

    hideHeaders: true,
    columnLines: false,
    rowLines: false,
    minHeight: 65,
    focusable: false,
    forceFit: false,
    scrollToTop: false,
    focusOnToFront: false,

    // layout: 'fit',
    // autoHeight: true,

    margin: '0 0 25 0',    // (top, right, bottom, left).

    initComponent: function () {
        var me = this;

        // function disableGridListeners(view, listeners) {
        //     var managedListeners = view.managedListeners || [],
        //         len = managedListeners.length;
        //     // console.info('disableGridListeners: ' + listeners);
        //     // console.info(view);
        //     // console.info(listeners);
        //     // console.info(managedListeners);
        //     for (var i = 0; i < len; i++) {
        //         if (Ext.Array.contains(listeners, managedListeners[i].ename)) {
        //             console.info('remove listener: ' + managedListeners[i].ename);
        //             view.removeManagedListenerItem(true, managedListeners[i]);
        //             len -= 1;
        //         }
        //     }
        // }
        //
        // function showGridListeners(view) {
        //     var managedListeners = view.managedListeners || [],
        //         i = 0,
        //         len = managedListeners.length;
        //
        //     for (; i < len; i++) {
        //         console.info(managedListeners[i].ename);
        //     }
        // }

        // me.listeners = {
        //     // itemmousedown: function(view){
        //     //     // view.fireEvent('scrolltoselection');
        //     //     console.info('itemmousedown productmapset');
        //     //     view.suspendEvents(false);
        //     // },
        //     // scrolltoselection: function () {
        //     //     var record = this.getSelection();
        //     //     if (record.length > 0)
        //     //         this.ensureVisible(record[0], {focus: true});
        //     // }
        //     // cellclick : function(view, cell, cellIndex, record, row, rowIndex, e) {
        //     //    //e.stopPropagation();
        //     //    return false;
        //     // },
        //     // beforerender: function () {
        //     //    Ext.util.Observable.capture(me, function (e) { console.log('productmapsetgrid - ' + e);});
        //     //    // me.ownerGrid.updateLayout();
        //     //    //console.info('ProductMapSet: beforerender event called');
        //     //    var me = this,
        //     //        record = me.getWidgetRecord();
        //     //    Ext.suspendLayouts();
        //     //    if (record.getData() != null && record.getData().hasOwnProperty('productmapsets')) {
        //     //        var productmapsets = record.getData().productmapsets;
        //     //        var newstore = Ext.create('Ext.data.JsonStore', {
        //     //            model: 'ProductMapSet',
        //     //            data: productmapsets
        //     //        });
        //     //        me.setStore(newstore);
        //     //    }
        //     //    Ext.resumeLayouts(true);
        //     // },
        //     // rowmousedown: {},
        //     // itemmousedown: {},
        //     // focusenter: {},
        //     afterrender: function (view) {
        //         me.updateLayout();
        //         Ext.util.Observable.capture(me, function (e) { console.log('productmapsetgrid - ' + e);});
        //         // showGridListeners(view);
        //         // var listenersArr = Ext.Array.push('focusenter', 'mousedown', 'rowmousedown', 'itemmousedown', 'beforeitemmousedown');
        //         // disableGridListeners(view, listenersArr);
        //         // view.suspendEvents(false);
        //         // view.clearManagedListeners();
        //         // console.info('afterrender productmapset');
        //         // console.info(view);
        //         // view.updateLayout();
        //     }
        //     // ,focusenter: function(view){
        //     //     view.suspendEvents(false);
        //     //     view.suspendEvent('focusenter');
        //     //     view.suspendEvent('focusleave');
        //     // }
        // };

        me.defaults = {
            menuDisabled: true,
            draggable:false,
            groupable:false,
            hideable: false,
            variableRowHeight: false
        };

        me.columns = [{
            header: '', // 'Mapset',
            dataIndex: 'descriptive_name',
            width: 205
        },{
            xtype: 'actioncolumn',
            width: 65,
            align:'center',
            stopSelection: false,
            items: [{
                icon: 'resources/img/icons/download.png',
                tooltip: esapp.Utils.getTranslation('tipcompletedatasetmapset'),    // 'Complete all data sets for this product\'s mapset',
                scope: me,
                handler: function (grid, rowIndex) {
                    var rec = grid.getStore().getAt(rowIndex);

                    var sendRequestWin = new esapp.view.datamanagement.sendRequest({
                        params: {
                            level: 'mapset',
                            record: rec
                        }
                    });
                    sendRequestWin.show();
                }
            }]
        }, {
            header: '',
            xtype: 'widgetcolumn',
            width: 725,
            // height: 360,
            // maxHeight: 360,
            // variableRowHeight: false,
            widget: {
                xtype: 'mapsetdatasetgrid',
                widgetattached: false
            },
            // listeners: {
            //     afterrender: function (widget) {
            //         Ext.util.Observable.capture(widget, function (e) { console.log('widget mapsetdatasetgrid - ' + widget.id + ' - ' + e);});
            //         // console.info('afterrender widget mapsetdatasetgrid');
            //         // widget.suspendEvents(false);
            //         // console.info(widget);
            //         // var listenersArr = Ext.Array.push('focusleave', 'focusenter');
            //         // disableGridListeners(widget, listenersArr);
            //         // widget.clearManagedListeners();
            //         // view.updateLayout();
            //     }
            //     // ,focusenter: function(widget){
            //     //     widget.suspendEvents(false);
            //     //     widget.suspendEvent('focusenter');
            //     //     widget.suspendEvent('focusleave');
            //     // }
            // },
            onWidgetAttach: function(col, widget, record) {
                if (!widget.widgetattached) {
                    // Ext.suspendLayouts();
                    widget.getStore().setData(record.getData().mapsetdatasets);
                    // var sorters = widget.getStore().getSorters();
                    // sorters.add('display_index');
                    // sorters.add('prod_descriptive_name');
                    // sorters.add('version');  , {property: 'prod_descriptive_name', direction: 'ASC'}, {property: 'version', direction: 'ASC'}
                    // var sorters = [{property: 'order_index', direction: 'ASC'}];
                    // widget.getStore().setSorters(sorters);
                    // widget.getStore().sort(sorters);

                    widget.widgetattached = true;
                    // Ext.resumeLayouts(true);
                }

                //var mapsetdatasets = record.getData().mapsetdatasets;
                //var newstore = Ext.create('Ext.data.JsonStore', {
                //    model: 'MapSetDataSet',
                //    data: mapsetdatasets
                //});
                //widget.setStore(newstore);
            }
        }];

        me.callParent();
    }

});