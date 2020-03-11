
Ext.define("esapp.view.acquisition.DataAcquisition",{
    "extend": "Ext.grid.Panel",

    "controller": "dataacquisition",

    "viewModel": {
        "type": "dataacquisition"
    },

    "xtype"  : 'dataacquisitiongrid',

    requires: [
        'esapp.view.acquisition.DataAcquisitionModel',
        'esapp.view.acquisition.DataAcquisitionController',
        'esapp.view.acquisition.logviewer.LogView',

        'esapp.view.acquisition.editEumetcastSource',
        'esapp.view.acquisition.editInternetSource',

        'Ext.grid.column.Action'
        //'Ext.grid.column.Check'
    ],

    // get the chained store from view model
    bind:{
        store:'{productdatasources}'
    },

    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable: false,
        markDirty: false,
        resizable: false,
        disableSelection: true,
        trackOver: true,
        forceFit: true,
        focusable: false,
        loadMask: false
        //focusOnToFront: false,
        //preserveScrollOnRefresh: false,
        //focusable: false

        //focusRow: Ext.emptyFn
        //,height:70
        //,getRowClass: function (record, rowIndex, rp, store) {
        //    rp.tstyle += 'height: 70px;';
        //    //if(record.id == 439){ //id is some field from the store model
        //    //     rp.tstyle += 'height: 70px;';
        //    //}
        //    //
        //    ////or
        //    //if(rowIndex == 1){
        //    //     rp.tstyle += 'height: 50px;';
        //    //}
        //}
    },

    // selModel: {listeners:{}},
    // selModel: Ext.create('Ext.selection.Model', { listeners: {} }),

    cls: 'grid-color-yellow',

    hideHeaders: true,
    columnLines: false,
    rowLines: false,
    collapsible: false,
    variableRowHeight : false,
    bufferedRenderer: false,
    focusable: false,
    layout: 'fit',

    //listeners: {
        //cellclick: function (x, y) {
        //    console.info('DataAcquisition cellclick');
        //    console.info(this);
        //},
        //cellmousedown: function (x, y)  {
            //Ext.util.Observable.capture(this, function(e){console.log('DataAquisition - ' + x.id + ': ' + e);});
            //console.info('DataAcquisition cellmousedown');
            //console.info(this);
            //this.suspendEvent('containerclick');
        //},
        //selectionchange: function (x, y)  {
        //    console.info('DataAcquisition selectionchange');
        //    console.info(this);
        //},
        //rowclick: function (x, y)  {
        //    console.info('DataAcquisition rowclick');
        //    console.info(this);
        //},
        //itemclick: function (x, y)  {
        //    console.info('DataAcquisition itemclick');
        //    console.info(this);
        //},
        //containerclick: function (x, y)  {
        //    console.info('DataAcquisition containerclick');
        //    console.info(this);
        //},
        //groupchange: function (x, y)  {
        //    console.info('DataAcquisition groupchange');
        //    console.info(this);
        //}
    //},
    //listeners: {
    //    celldblclick: function(grid, el, colIndex, record){
    //        //console.info(record);
    //        var data_source_id = record.get('data_source_id');
    //        if (record.get('type') == 'INTERNET'){
    //            var editInternetSourceWin = new esapp.view.acquisition.editInternetSource({
    //                data_source_id: data_source_id
    //            });
    //            editInternetSourceWin.show();
    //        }
    //        else if (record.get('type') == 'EUMETCAST'){
    //            //var eumetcaststore = Ext.data.StoreManager.lookup('EumetcastSourceStore');
    //            //var eumetcastsource_record = eumetcaststore.findRecord('eumetcast_id', data_source_id, 0, true, false, true);
    //
    //            var editEumetcastSourceWin = new esapp.view.acquisition.editEumetcastSource({
    //                data_source_id: data_source_id
    //                //,viewModel: {
    //                //        // If we are passed a record, a copy of it will be created in the newly spawned session.
    //                //        // Otherwise, create a new phantom record in the child.
    //                //        links: {
    //                //            theEumetcastSource: eumetcastsource_record
    //                //        }
    //                //}
    //            });
    //            //editEumetcastSourceWin.down('grid').getStore().load();
    //            editEumetcastSourceWin.show();
    //        }
    //    }
        //,viewready: function (grid) {
        //    var view = grid.view;
        //
        //    // record the current cellIndex
        //    grid.mon(view, {
        //        uievent: function (type, view, cell, recordIndex, cellIndex, e) {
        //            grid.cellIndex = cellIndex;
        //            grid.recordIndex = recordIndex;
        //        }
        //    });
        //
        //    grid.tip = Ext.create('Ext.tip.ToolTip', {
        //        target: view.el,
        //        delegate: '.x-grid-cell',
        //        trackMouse: false,
        //        renderTo: Ext.getBody()
        //        //listeners: {
        //        //    beforeshow: function updateTipBody(tip) {
        //        //        if (grid.cellIndex == 0) {
        //        //            tip.enable();
        //        //            tip.show();
        //        //        }
        //        //        else {
        //        //            //tip.update('');
        //        //            tip.disable();
        //        //            tip.hide();
        //        //        }
        //        //    }
        //        //}
        //    });
        //
        //    var tipRenderer = function (e, t, grid){
        //        e.stopEvent();
        //        if (grid.cellIndex == 0) {
        //            var tipbody = esapp.Utils.getTranslation('doubleclicktoeditdatasource')+': ' + grid.getStore().getAt(grid.recordIndex).get('data_source_id');
        //            grid.tip.update(tipbody);
        //            grid.tip.show();
        //        }
        //    };
        //
        //    grid.getEl().on('mouseover', function(e,t,a){
        //        tipRenderer(e,t,grid);
        //    }, null, {delegate:'.x-grid-cell'});
        //
        //}
    //},
    //listeners: {
    //    beforerender:  function () {
    //        var me = this,
    //            record = me.getWidgetRecord();
    //        Ext.suspendLayouts();
    //        var daStore = me.getViewModel().get('productdatasources');
    //        if (daStore) {
    //            daStore.setFilters({
    //                property: 'productid'
    //                , value: record.id
    //                , anyMatch: true
    //            });
    //        }
    //        Ext.resumeLayouts(true);
    //    }
    //    //,mouseenter: {
    //        //element: 'el',
    //        //fn: function(){
    //        //    this.suspendEvents();
    //        //}
    //    //}
    //},

    initComponent: function () {
        var me = this;
        var user = esapp.getUser();

        me.defaults = {
            menuDisabled: true,
            draggable:false,
            groupable:false,
            hideable: false
        };

        me.columns = [{
            // text: '', // 'Type',
            width: 220,
            //dataIndex: 'type'
            xtype:'templatecolumn',
            tpl: new Ext.XTemplate(
                    '<b>{type}</b>   ' +
                    '</br>' +
                    '<b class="smalltext" style="color:darkgrey;">{data_source_id}</b>' +
                    '</br>' +
                    '<tpl if="time_latest_copy != \'\'">',
                        '<b class="smalltext" style="color:lightgrey;">'+esapp.Utils.getTranslation('lastcopied')+': {time_latest_copy}</b>' +
                        '</br>' +
                    '</tpl>',
                    '<tpl if="time_latest_exec != \'\'">',
                        '<b class="smalltext" style="color:lightgrey;">'+esapp.Utils.getTranslation('lastexecuted')+': {time_latest_exec}</b>' +
                    '</tpl>',
                    '</br>'
                ),
            cellWrap:true
            //,tdCls: 'cursorpointer'
        },{
            xtype: 'actioncolumn',
            // header: 'Active',
            hideable: false,
            hidden: Ext.getCmp('lockunlock').pressed ? false : true,
            width: 35,
            align: 'center',
            stopSelection: false,
            items: [{
                // scope: me,
                disabled: false,
                getClass: function(v, meta, rec) {
                    if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)){
                        return 'edit16';
                    }
                    else {
                        return 'vieweye18';
                    }
                },
                getTip: function(v, meta, rec) {
                    if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)){
                        return esapp.Utils.getTranslation('editdatasource')+' ' + rec.get('data_source_id');
                    }
                    else {
                        return esapp.Utils.getTranslation('viewdatasource')+' ' + rec.get('data_source_id');
                    }

                },
                handler: function(grid, rowIndex, colIndex) {
                    var record = grid.getStore().getAt(rowIndex);
                    var data_source_id = record.get('data_source_id');
                    // console.info(record);
                    // console.info(data_source_id);

                    var edit = false;
                    var view = true;
                    if (!record.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)){
                        edit = true;
                        view = false;
                    }

                    if (record.get('type') == 'INTERNET'){
                        // data_source_id = record.get('internet_id');
                        var editInternetSourceWin = new esapp.view.acquisition.editInternetSource({
                            params: {
                                create: false,
                                edit: edit,
                                view: view,
                                internetsourcerecord: record,
                                data_source_id: data_source_id
                            }
                        });
                        editInternetSourceWin.show();
                    }
                    else if (record.get('type') == 'EUMETCAST'){
                        //var eumetcaststore = Ext.data.StoreManager.lookup('EumetcastSourceStore');
                        //var eumetcastsource_record = eumetcaststore.findRecord('eumetcast_id', data_source_id, 0, true, false, true);

                        var editEumetcastSourceWin = new esapp.view.acquisition.editEumetcastSource({
                            params: {
                                create: false,
                                edit: edit,
                                view: view,
                                eumetcastsourcerecord: record,
                                data_source_id: data_source_id
                            }
                            //,viewModel: {
                            //        // If we are passed a record, a copy of it will be created in the newly spawned session.
                            //        // Otherwise, create a new phantom record in the child.
                            //        links: {
                            //            theEumetcastSource: eumetcastsource_record
                            //        }
                            //}
                        });
                        //editEumetcastSourceWin.down('grid').getStore().load();
                        editEumetcastSourceWin.show();
                    }
                }
            }]
        //}, {
        //    // text: '', // 'Latest Acquired',
        //    width: 110,
        //    dataIndex: 'time_latest_copy',
        //    hidden: true
        //}, {
        //    // text: '', // 'Latest Acquired',
        //    width: 110,
        //    dataIndex: 'time_latest_exec',
        //    hidden: true
        }, {
            xtype: 'actioncolumn',
            // header: 'Store Native',
            hideable: true,
            hidden: Ext.getCmp('lockunlock').pressed ? false : true,
            width: 100,
            align: 'center',
            stopSelection: false,
            items: [{
                // scope: me,
                disabled: false,
                style: {"line-height": "70px"},
                getClass: function(v, meta, rec) {
                    if (rec.get('store_original_data')) {
                        return 'activated';
                    } else {
                        return 'deactivated';
                    }
                },
                getTip: function(v, meta, rec) {
                    if (rec.get('store_original_data')) {
                        return esapp.Utils.getTranslation('tipdeactivatestoreoriginalget');     // 'Deactivate store original data for this Get';
                    } else {
                        return esapp.Utils.getTranslation('tipactivatestoreoriginalget');     // 'Activate store original data for this Get';
                    }
                },
                handler: function(grid, rowIndex, colIndex) {
                    var rec = grid.getStore().getAt(rowIndex),
                        action = (rec.get('store_original_data') ? 'deactivated' : 'activated');
                    // Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                    rec.get('store_original_data') ? rec.set('store_original_data', false) : rec.set('store_original_data', true);
                }
            }]
        }, {
            xtype: 'actioncolumn',
            // header: 'Active',
            hideable: false,
            hidden:false,
            // disabled: true,
            width: 65,
            align: 'center',
            stopSelection: false,
            items: [{
                // scope: me,
                disabled: false,
                getClass: function(v, meta, rec) {
                    if (rec.get('activated')) {
                        return 'activated';
                    } else {
                        return 'deactivated';
                    }
                },
                getTip: function(v, meta, rec) {
                    if (rec.get('activated')) {
                        return esapp.Utils.getTranslation('tipdeactivateget');     // 'Deactivate Get';
                    } else {
                        return esapp.Utils.getTranslation('tipactivateget');     // 'Activate Get';
                    }
                },
                handler: function(grid, rowIndex, colIndex) {
                    var rec = grid.getStore().getAt(rowIndex),
                        action = (rec.get('activated') ? 'deactivated' : 'activated');
                    // Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                    rec.get('activated') ? rec.set('activated', false) : rec.set('activated', true);
                }
            }]
        },{
            xtype: 'actioncolumn',
            width: 55,
            //height:40,
            align:'center',
            stopSelection: false,
            items: [{
                //icon: 'resources/img/icons/file-extension-log-icon-32x32.png',
                iconCls:'log-icon',
                width:32,
                height:32,
                tooltip: esapp.Utils.getTranslation('showgetlog'),     // 'Show log of this Get',
                scope: me,
                handler: function (grid, rowIndex, colIndex, icon) {
                    var rec = grid.getStore().getAt(rowIndex);
                    var logViewWin = new esapp.view.acquisition.logviewer.LogView({
                        params: {
                            logtype: 'get',
                            record: rec
                        }
                    });
                    logViewWin.show();
                }
            }]
        }];

        me.callParent();
    }
});
