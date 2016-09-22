
Ext.define('esapp.view.acquisition.Acquisition',{
    extend: "Ext.grid.Panel",

    controller: 'acquisition',

    viewModel: {
        type: 'acquisition'
    },

    xtype  : 'acquisition-main',

    requires: [
        'esapp.view.acquisition.AcquisitionModel',
        'esapp.view.acquisition.AcquisitionController',
        //'esapp.view.acquisition.DataAcquisition',
        //'esapp.view.acquisition.Ingestion',
        //'esapp.view.acquisition.product.selectProduct',
        //
        //'esapp.view.acquisition.editEumetcastSource',
        //'esapp.view.acquisition.editInternetSource',

        //'esapp.view.acquisition.product.editProduct',
        //'esapp.view.acquisition.product.InternetSourceAdmin',
        //'esapp.view.acquisition.product.EumetcastSourceAdmin',

        'Ext.window.Toast',
        'Ext.layout.container.Center',
        //'Ext.grid.plugin.CellEditing',
        'Ext.grid.column.Widget',
        //'Ext.grid.column.Boolean',
        'Ext.grid.column.Template',
        //'Ext.grid.column.Check',
        'Ext.button.Split',
        'Ext.menu.Menu',
        'Ext.XTemplate',
        'Ext.grid.column.Action'
    ],

    name:'acquisitionmain',

    store: 'ProductsActiveStore',

    //features: [{
    //    id: 'productcategories',
    //    ftype: 'grouping',
    //    groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
    //    hideGroupedHeader: true,
    //    enableGroupingMenu: false,
    //    startCollapsed : true,
    //    groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product categories'
    //}],

    viewConfig: {
        stripeRows: true,
        enableTextSelection: true,
        draggable:false,
        markDirty: false,
        resizable:false,
        trackOver:true
        //focusOnToFront: false,
        //preserveScrollOnRefresh: false,
        //focusable: false
        //focusRow: Ext.emptyFn
    },

    //selType: '',
    //selModel: {
    //    //preventFocus: true,
    //    //selectionMode: 'SIMPLE',
    //    listeners: {
    //        focuschange: function(selmodel, oldFocused, newFocused ,eOpts) {
    //            console.info('focuschange');
    //            console.info(selmodel);
    //            console.info(oldFocused);
    //            console.info(newFocused);
    //            console.info(eOpts);
    //
    //
    //            //return null;
    //            //
    //            //selmodel.selectPrevious(false, false);
    //            //oldFocused = null;
    //            //newFocused = null;
    //            //selmodel.navigationModel.lastFocused = null;
    //            if (oldFocused == 'undefined' || oldFocused == 'null' || oldFocused == null){
    //                Ext.suspendLayouts();
    //            }
    //            else {
    //                Ext.resumeLayouts(true);
    //            }
    //            //selmodel.clearSelections();
    //        }
    //
    //        //,lastfocuschanged: function (oldFocused, newFocused, supressFocus) {
    //        //    console.info('lastfocuschanged');
    //        //    console.info(this);
    //        //    console.info(oldFocused);
    //        //    console.info(newFocused);
    //        //    console.info(supressFocus);
    //        //}
    //        //,beforeselect: function (record , index , eOpts) {
    //        //    console.info('beforeselect');
    //        //    console.info(this);
    //        //    this.selectPrevious(false, false);
    //        //    //return null;
    //        //    //this.clearSelections();
    //        //}
    //        //,selection: function (record , index , eOpts) {
    //        //    console.info('selection');
    //        //    console.info(this);
    //        //    //return null;
    //        //    //this.clearSelections();
    //        //}
    //        //,selectionchange: function (selected , eOpts) {
    //        //    console.info('selectionchange');
    //        //    console.info(this);
    //        //    //return null;
    //        //    //this.clearSelections();
    //        //}
    //    }
    //},
    //selModel: {listeners:{}},
    //selModel: Ext.create('Ext.selection.Model', { listeners: {} }),

    collapsible: false,
    suspendLayout:false,
    disableSelection: true,
    enableColumnMove:false,
    enableColumnResize:false,
    multiColumnSort: false,
    columnLines: false,
    rowLines: true,
    frame: false,
    border: false,
    bufferedRenderer: false,
    variableRowHeight:true,
    forceFit: false,

    session:true,

    listeners: {
        groupclick: function( view, node, group, eOpts ) {
            this.getController().renderHiddenColumnsWhenUnlocked();
        }
        //,afterrender: function (view) {
        //    //this.getView().getFeature('productcategories').collapseAll();
        //}
        //,beforerender: function (){
        //
        //    //Ext.util.Observable.capture(this, function(e){console.log(this.id + ': ' + e);});
        //    Ext.util.Observable.capture(this.getSelectionModel(), function(e){ console.log('selModel - ' + this.id + ': ' + e);});
        //    Ext.util.Observable.capture(this, function(e){ console.log('acquisition-main - ' + this.id + ': ' + e);});
        //
        //    //this.getSelectionModel().setLocked(true);
        //    //this.getSelectionModel().removeListener('focuschange', this.getSelectionModel());
        //    //this.getSelectionModel().getNavigationModel().removeListener('navigate', this.getSelectionModel().getNavigationModel());
        //    //console.info(this.getSelectionModel());
        //}
    },

    //plugins:[{
    //    ptype:'lazyitems'
    //},{
    //    ptype:'cellediting'
    //}],
    // defaultListenerScope: true,


    initComponent: function () {
        var me = this;

        //Ext.util.Observable.capture(this, function(e){console.log('Acquisition - ' + this.id + ': ' + e);});

        me.features = [{
            id: 'productcategories',
            ftype: 'grouping',
            groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
            hideGroupedHeader: true,
            enableGroupingMenu: false,
            startCollapsed : true,
            groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product categories'
        }];

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            items: [{
                xtype: 'button',
                id: 'lockunlock',
                name: 'lockunlock',
                iconCls: 'fa fa-lock fa-2x',  // 'fa-unlock' = xf09c  'fa-lock' = xf023
                // style: { color: 'gray' },
                // glyph: 'xf023@FontAwesome',
                enableToggle: true,
                scale: 'medium',
                handler:  function(btn) {

                    //Ext.suspendLayouts();

                    var acq_main = Ext.ComponentQuery.query('panel[name=acquisitionmain]');
                    var dataacquisitiongrids = Ext.ComponentQuery.query('dataacquisitiongrid');
                    var ingestiongrids = Ext.ComponentQuery.query('ingestiongrid');
                    var addproductbtn = Ext.ComponentQuery.query('panel[name=acquisitionmain] > toolbar > button[name=addproduct]');
                    //var checkColumns = Ext.ComponentQuery.query('panel[name=acquisitionmain] checkcolumn, dataacquisitiongrid checkcolumn, ingestiongrid checkcolumn');
                    var actionColumns = Ext.ComponentQuery.query('panel[name=acquisitionmain] actioncolumn, dataacquisitiongrid actioncolumn, ingestiongrid actioncolumn');

                    if (btn.pressed){

                        btn.setIconCls('fa fa-unlock fa-2x');

                        acq_main[0].columns[2].setWidth(500);   // GET
                        acq_main[0].columns[2].setText(' <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable x-column-header-first" style="border-top: 0px; width: 265px; left: 0px; tabindex="-1">' +
                        '           <div data-ref="titleEl" class="x-column-header-inner">' +
                        '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('type') + '</span>' +
                        '           </div>' +
                        '       </div>' +
                        //'       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 110px; right: auto; left: 201px; margin: 0px; top: 0px;" tabindex="-1">' +
                        //'           <div data-ref="titleEl" class="x-column-header-inner">' +
                        //'               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('lastcopied') + '</span>' +
                        //'           </div>' +
                        //'       </div>' +
                        //'       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 110px; right: auto; left: 311px; margin: 0px; top: 0px;" tabindex="-1">' +
                        //'           <div data-ref="titleEl" class="x-column-header-inner">' +
                        //'               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('lastexecuted') + '</span>' +
                        //'           </div>' +
                        //'       </div>' +
                        '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 105px; left: 265px; margin: 0px; top: 0px;" tabindex="-1">' +
                        '           <div data-ref="titleEl" class="x-column-header-inner">' +
                        '               <span data-ref="textEl" class="x-column-header-text smalltext12">' + esapp.Utils.getTranslation('storenative') + '</span>' +
                        '           </div>' +
                        '       </div>' +
                        '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 65px; right: auto; left: 370px; margin: 0px; top: 0px;" tabindex="-1">' +
                        '           <div data-ref="titleEl" class="x-column-header-inner">' +
                        '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('active') + '</span>' +
                        '           </div>' +
                        '       </div>' +
                        '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 70px; left: 435px; margin: 0px; top: 0px;" tabindex="-1">' +
                        '           <div data-ref="titleEl" class="x-column-header-inner">' +
                        '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('log') + '</span>' +
                        '           </div>' +
                        '       </div>');

                        acq_main[0].columns[3].setWidth(785+70);   // INGESTION
                        acq_main[0].columns[3].setText(' <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 195px; right: auto; left: 0px; margin: 0px; top: 0px;" tabindex="-1">' +
                        '           <div data-ref="titleEl" class="x-column-header-inner">' +
                        '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('subproduct') + '</span>' +
                        '           </div>' +
                        '       </div>' +
                        '       <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 235px; left: 195px; tabindex="-1">' +
                        '           <div data-ref="titleEl" class="x-column-header-inner">' +
                        '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('mapset') + '</span>' +
                        '           </div>' +
                        '       </div>' +
                        '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 360px; right: auto; left: 430px; margin: 0px; top: 0px;" tabindex="-1">' +
                        '           <div data-ref="titleEl" class="x-column-header-inner">' +
                        '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('completeness') + '</span>' +
                        '           </div>' +
                        '       </div>' +
                        '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 70px; right: auto; left: 790px; margin: 0px; top: 0px;" tabindex="-1">' +
                        '           <div data-ref="titleEl" class="x-column-header-inner">' +
                        '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('active') + '</span>' +
                        '           </div>' +
                        //'       </div>' +
                        //'       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 70px;  left: 695px; margin: 0px; top: 0px;" tabindex="-1">' +
                        //'           <div data-ref="titleEl" class="x-column-header-inner">' +
                        //'               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('log') + '</span>' +
                        //'           </div>' +
                        '       </div>');

                        addproductbtn[0].show();
                        //acq_main[0].columns[0].show();  // Edit product action column
                        acq_main[0].columns[1].show();    // Activate Product column
                        //acq_main[0].columns[3].show();

                        Ext.Object.each(dataacquisitiongrids, function(id, dataacquisitiongrid, myself) {
                            dataacquisitiongrid.columns[1].show();      // Edit Data Source
                            //dataacquisitiongrid.columns[1].updateLayout();
                            dataacquisitiongrid.columns[2].show();      // Store Native
                            //dataacquisitiongrid.columns[2].updateLayout();
                            //dataacquisitiongrid.columns[2].show();   // Last executed
                            //dataacquisitiongrid.columns[3].show();   // Store Native
                        });

                        Ext.Object.each(ingestiongrids, function(id, ingestiongrid, myself) {
                            ingestiongrid.columns[0].show();    // Add Mapset
                            //ingestiongrid.columns[0].updateLayout();
                            ingestiongrid.columns[3].show();    // Delete Mapset
                            //ingestiongrid.columns[3].updateLayout();
                        });

                        //Ext.Object.each(checkColumns, function(id, chkCol, myself) {
                        //    chkCol.enable();
                        //});
                        // Enable action columns
                        //Ext.Object.each(actionColumns, function(id, actionCol, myself) {
                        //    actionCol.enable();
                        //    actionCol.items[0].disabled = false;
                        //    actionCol.enableAction(0);
                        //    actionCol.updateLayout();
                        //})
                    }
                    else {
                        btn.setIconCls('fa fa-lock fa-2x');

                        acq_main[0].columns[2].setWidth(360);   // GET
                        acq_main[0].columns[2].setText(' <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable x-column-header-first" style="border-top: 0px; width: 230px; left: 0px; tabindex="-1">' +
                                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('type') + '</span>' +
                                '           </div>' +
                                '       </div>' +
                                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 65px; left: 230px; margin: 0px; top: 0px;" tabindex="-1">' +
                                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('active') + '</span>' +
                                '           </div>' +
                                '       </div>' +
                                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 70px; left: 295px; margin: 0px; top: 0px;" tabindex="-1">' +
                                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('log') + '</span>' +
                                '           </div>' +
                                '       </div>');

                        acq_main[0].columns[3].setWidth(785);   // INGESTION
                        acq_main[0].columns[3].setText('<div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 160px; right: auto; left: 0px; margin: 0px; top: 0px;" tabindex="-1">' +
                                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('subproduct') + '</span>' +
                                '           </div>' +
                                '       </div>' +
                                '       <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 200px; left: 160px; tabindex="-1">' +
                                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('mapset') + '</span>' +
                                '           </div>' +
                                '       </div>' +
                                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 360px; right: auto; left: 360px; margin: 0px; top: 0px;" tabindex="-1">' +
                                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('completeness') + '</span>' +
                                '           </div>' +
                                '       </div>' +
                                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 70px; right: auto; left: 720px; margin: 0px; top: 0px;" tabindex="-1">' +
                                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('active') + '</span>' +
                                '           </div>' +
                                //'       </div>' +
                                //'       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 70px;  left: 695px; margin: 0px; top: 0px;" tabindex="-1">' +
                                //'           <div data-ref="titleEl" class="x-column-header-inner">' +
                                //'               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('log') + '</span>' +
                                //'           </div>' +
                                '       </div>');

                        addproductbtn[0].hide();
                        //acq_main[0].columns[0].hide();
                        acq_main[0].columns[1].hide();
                        //acq_main[0].columns[3].hide();
                        Ext.Object.each(dataacquisitiongrids, function(id, dataacquisitiongrid, myself) {
                            dataacquisitiongrid.columns[1].hide();  // Edit Data Source
                            dataacquisitiongrid.columns[2].hide();  // Store Native
                            //dataacquisitiongrid.columns[3].hide();
                        });
                        Ext.Object.each(ingestiongrids, function(id, ingestiongrid, myself) {
                            ingestiongrid.columns[0].hide();    // Add Mapset
                            //ingestiongrid.columns[0].updateLayout();
                            ingestiongrid.columns[3].hide();    // Delete Mapset
                            //ingestiongrid.columns[3].updateLayout();
                        });
                    }

                    //Ext.resumeLayouts(true);

                    // acq_main.updateLayout();
                    //var toggleFn = newValue ? 'disable' : 'enable';
                    //Ext.each(this.query('button'), function(item) {
                    //    item[toggleFn]();
                    //});
                }
            }, {
                xtype: 'button',
                text: esapp.Utils.getTranslation('addproduct'),    // 'Add Product',
                name: 'addproduct',
                iconCls: 'fa fa-plus-circle fa-2x',
                style: { color: 'green' },
                hidden: true,
                // glyph: 'xf055@FontAwesome',
                scale: 'medium',
                handler: 'selectProduct'
            },{
                text:  esapp.Utils.getTranslation('expandall'),    // 'Expand All',
                handler: function(btn) {
                    var view = btn.up().up().getView();
                    //Ext.suspendLayouts();
                    view.getFeature('productcategories').expandAll();
                    //Ext.resumeLayouts(true);
                    //me.getController().renderHiddenColumnsWhenUnlocked();
                    //view.refresh();
                    //view.updateLayout();
                }
            }, {
                text:  esapp.Utils.getTranslation('collapseall'),    // 'Collapse All',
                handler: function(btn) {
                    var view = btn.up().up().getView();
                    view.getFeature('productcategories').collapseAll();
                    //me.getController().renderHiddenColumnsWhenUnlocked();
                    //view.refresh();
                    //view.updateLayout();
                }
            }, '->',
            {
                xtype: 'servicemenubutton',
                service: 'eumetcast',
                text:  esapp.Utils.getTranslation('eumetcast'),    // 'Eumetcast',
                //listeners : {
                //    afterrender: 'checkStatusServices'
                //},
                handler: 'checkStatusServices'
            },
            // add a vertical separator bar between toolbar items
            '-', // same as {xtype: 'tbseparator'} to create Ext.toolbar.Separator
            {
                xtype: 'servicemenubutton',
                service: 'internet',
                text: esapp.Utils.getTranslation('internet'),    // 'Internet',
                handler: 'checkStatusServices'
            },
            '-',
            {
                xtype: 'servicemenubutton',
                service: 'ingest',
                text: esapp.Utils.getTranslation('ingest'),    // 'Ingest',
                handler: 'checkStatusServices'
            },
            {
                xtype: 'checkboxfield',
                boxLabel  : esapp.Utils.getTranslation('ingest_archives_from_eumetcast'),    // 'Ingest Archives from EUMETCast',
                name      : 'ingest_archives_from_eumetcast',
                inputValue: '1',
                id        : 'ingest_archives_from_eumetcast',
                //listeners: {
                //    boxclick: 'setIngestArchivesFromEumetcast'
                //}
                handler: 'setIngestArchivesFromEumetcast'
            },
            '->', // same as { xtype: 'tbfill' }
            {
                xtype: 'button',
                iconCls: 'fa fa-refresh fa-2x',
                style: { color: 'gray' },
                enableToggle: false,
                scale: 'medium',
                handler:  function(btn) {
                    var productgridstore  = Ext.data.StoreManager.lookup('ProductsActiveStore');
                    var acqgridsstore = Ext.data.StoreManager.lookup('DataAcquisitionsStore');
                    var ingestiongridstore = Ext.data.StoreManager.lookup('IngestionsStore');
                    var eumetcastsourcestore = Ext.data.StoreManager.lookup('EumetcastSourceStore');
                    var internetsourcestore = Ext.data.StoreManager.lookup('InternetSourceStore');

                    if (productgridstore.isStore) {
                        productgridstore.load({
                            callback: function(records, options, success) {
                                if (acqgridsstore.isStore) {
                                    acqgridsstore.load({
                                        callback: function(records, options, success) {
                                            //me.getController().renderHiddenColumnsWhenUnlocked();

                                            if (ingestiongridstore.isStore) {
                                                ingestiongridstore.load({
                                                    callback: function(records, options, success){
                                                        //var view = btn.up().up().getView();
                                                        ////view.getFeature('productcategories').expandAll();
                                                        //view.refresh();
                                                    }
                                                });
                                            }
                                        }
                                    });
                                }
                            }
                        });
                    }

                    eumetcastsourcestore.load();
                    internetsourcestore.load();

                    me.getController().checkStatusServices();
                }
            }]
        });

        //me.listeners = {
        //    viewready: function(gridpanel,func){
        //        //Ext.toast({ html: 'viewready', title: 'viewready', width: 200, align: 't' });
        //
        //        var task = new Ext.util.DelayedTask(function() {
        //            var view = gridpanel.getView();
        //            view.getFeature('productcategories').expandAll();
        //            view.refresh();
        //        });
        //
        //        task.delay(500);
        //    }
        //};

        me.defaults = {
            variableRowHeight: true,
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
            //    xtype: 'actioncolumn',
            //    hideable: true,
            //    hidden:true,
            //    width: 50,
            //    height: 50,
            //    align: 'center',
            //    shrinkWrap: 0,
            //    items: [{
            //        //icon: 'resources/img/icons/edit.png',
            //        getClass: function(v, meta, rec) {
            //            if (rec.get('defined_by') != 'JRC') {
            //                return 'editproduct';
            //            }
            //            else {
            //                return 'x-hide-display';
            //            }
            //        },
            //        getTip: function(v, meta, rec) {
            //            if (rec.get('defined_by') != 'JRC') {
            //                return esapp.Utils.getTranslation('editproduct');    // 'Edit Product',
            //            }
            //        },
            //        // iconCls: 'fa fa-edit fa-2x', // xf044
            //        // cls: 'fa fa-edit fa-2x', // xf044
            //        //tooltip: esapp.Utils.getTranslation('editproduct'),   // 'Edit Product',
            //        handler: 'editProduct'
            //    }]
            //}, {
                xtype:'templatecolumn',
                header: esapp.Utils.getTranslation('product'),   // 'Product',
                tpl: new Ext.XTemplate(
                        '<b>{prod_descriptive_name}</b>' +
                        '<tpl if="version != \'undefined\'">',
                            '<b class="smalltext"> - {version}</b>',
                        '</tpl>',
                        '</br>' +
                        '<b class="smalltext" style="color:darkgrey">'+esapp.Utils.getTranslation('productcode')+': {productcode}</b>' +
                        '</br>' +
                        '<b class="smalltext" style="color:darkgrey">'+esapp.Utils.getTranslation('provider')+': {provider}</b>' +
                        '</br>'
                    ),
                width: 330,
                cellWrap:true,
                variableRowHeight:true
            },{
                xtype: 'actioncolumn',
                header: esapp.Utils.getTranslation('active'),   // 'Active',
                hideable: true,
                hidden:true,
                width: 65,
                align: 'center',
                //stopSelection: false,
                shrinkWrap: 0,
                variableRowHeight:true,
                items: [{
                    getClass: function(v, meta, rec) {
                        if (rec.get('activated')) {
                            return 'activated';
                        } else {
                            return 'deactivated';
                        }
                    },
                    getTip: function(v, meta, rec) {
                        if (rec.get('activated')) {
                            return esapp.Utils.getTranslation('deactivateproduct');   // 'Deactivate Product';
                        } else {
                            return esapp.Utils.getTranslation('activateproduct');   // 'Activate Product';
                        }
                    },
                    isDisabled: function(view, rowIndex, colIndex, item, record) {
                        // Returns true if 'editable' is false (, null, or undefined)
                        return false // !record.get('editable');
                    },
                    handler: function(grid, rowIndex, colIndex, icon, e, record) {
                        var rec = record,   // grid.getStore().getAt(rowIndex),
                            action = (rec.get('activated') ? 'deactivated' : 'activated');
                        // Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                        rec.get('activated') ? rec.set('activated', false) : rec.set('activated', true);
                        //me.getController().renderHiddenColumnsWhenUnlocked();
                    }
                }]
//            }, {
//                xtype: 'checkcolumn',
//                header: 'Active',
//                width: 65,
//                dataIndex: 'activated',
//                stopSelection: false,
//                hideable: true,
//                hidden:true,
//                disabled: true,
//                listeners: {
//                  checkchange: function(chkBox, rowIndex, checked, eOpts){
////                      var myTitle = ""
////                      if (checked)  myTitle = "Activate Product";
////                      else myTitle = "De-activate Product";
////                      Ext.toast({ html: 'Checkbox clicked!', title: myTitle, width: 200, align: 't' });
//                  }
//                }
//                xtype: 'booleancolumn',
//                header: 'Active',
//                width: 80,
//                sortable: true,
//                dataIndex: 'activated',
//                stopSelection: false,
//                trueText: '&#x2713;',
//                falseText: '-',
//                align: 'center'
            }]
        }, {
            header:  '<div class="grid-header-style">' + esapp.Utils.getTranslation('get') + '</div>',
            id:'acquisitioncolumn',
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
                xtype: 'widgetcolumn',
                width: 360,
                variableRowHeight:true,

                header: ' <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable x-column-header-first" style="border-top: 0px; width: 230px; left: 0px; tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('type') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 65px; left: 230px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('active') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 70px; left: 295px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('log') + '</span>' +
                '           </div>' +
                '       </div>',

                listeners: {
                    render: function(column){
                        column.titleEl.removeCls('x-column-header-inner');
                    }
                },
                onWidgetAttach: function(col, widget, record) {
                    //console.info(widget.lookupViewModel());
                    var daStore = widget.getViewModel().get('productdatasources');
                    //if (daStore.getFilters().items.length == 0) {
                    //    Ext.suspendLayouts();
                        daStore.setFilters({
                            property: 'productid'
                            , value: record.id
                            , anyMatch: true
                        });
                        //Ext.resumeLayouts(true);
                    //}
                },
                widget: {
                    xtype: 'dataacquisitiongrid'
                }
            }]
        }, {
            header:  '<div class="grid-header-style">' + esapp.Utils.getTranslation('ingestion') + '</div>',
            menuDisabled: true,
            variableRowHeight : true,
            defaults: {
                menuDisabled: true,
                variableRowHeight : true,
                sortable: false,
                groupable:false,
                draggable:false,
                hideable: true
            }
            ,columns: [{
                xtype: 'widgetcolumn',
                width: 785,
                bodyPadding:5,
                variableRowHeight:true,

                header:
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 160px; right: auto; left: 0px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('subproduct') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 200px; left: 160px; tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('mapset') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 360px; right: auto; left: 360px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('completeness') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 70px; right: auto; left: 720px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('active') + '</span>' +
                '           </div>' +
                //'       </div>' +
                //'       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; border-right: 0px; width: 70px;  left: 695px; margin: 0px; top: 0px;" tabindex="-1">' +
                //'           <div data-ref="titleEl" class="x-column-header-inner">' +
                //'               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('log') + '</span>' +
                //'           </div>' +
                '       </div>',
                listeners: {
                    render: function(column){
                        column.titleEl.removeCls('x-column-header-inner');
                    }
                },
                widget: {
                    xtype: 'ingestiongrid'
                },
                onWidgetAttach: function(col, widget, record) {
                    var daStore = widget.getViewModel().get('productingestions');
                    //if (daStore.getFilters().items.length == 0) {
                    //    Ext.suspendLayouts();
                        daStore.setFilters({
                            property: 'productid'
                            , value: record.id
                            , anyMatch: true
                        });
                        //Ext.resumeLayouts(true);
                    //}
                }
            }]
        },{
            xtype: 'actioncolumn',
            text: esapp.Utils.getTranslation('log'),    // 'Log',
            //id: 'ingestionlogcolumn',
            width: 70,
            //height:40,
            menuDisabled: true,
            align:'center',
            stopSelection: false,
            variableRowHeight:true,
            //cls:'x-grid3-td-ingestionlogcolumn',
            items: [{
                //icon: 'resources/img/icons/file-extension-log-icon-32x32.png',
                iconCls:'log-icon',
                width:32,
                height:32,
                tooltip: esapp.Utils.getTranslation('showingestionlog'),     // 'Show log of this Ingestion',
                scope: me,
                handler: function (grid, rowIndex, colIndex, icon, e, record) {
                    //console.info(record);
                    //var recIndex = grid.getStore().indexOf(record);
                    //console.info(recIndex);
                    //console.info(rowIndex);
                    //var rec = grid.getStore().getAt(rowIndex);
                    //console.info(rec);
                    var logViewWin = new esapp.view.acquisition.logviewer.LogView({
                        params: {
                            logtype: 'ingest',
                            record: record
                        }
                    });
                    logViewWin.show();
                }
            }]
        }];

        //Ext.resumeLayouts(true);

        me.callParent();
    }
});