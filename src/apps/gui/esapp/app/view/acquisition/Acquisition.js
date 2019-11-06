
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
        // 'esapp.view.acquisition.product.selectProduct',
        //
        //'esapp.view.acquisition.editEumetcastSource',
        //'esapp.view.acquisition.editInternetSource',

        //'esapp.view.acquisition.product.editProduct',
        //'esapp.view.acquisition.product.InternetSourceAdmin',
        //'esapp.view.acquisition.product.EumetcastSourceAdmin',

        'Ext.window.Toast',
        'Ext.layout.container.Center',
        'Ext.grid.column.Widget',
        'Ext.grid.column.Template',
        'Ext.button.Split',
        'Ext.menu.Menu',
        'Ext.XTemplate',
        'Ext.grid.column.Action'
    ],

    name:'acquisitionmain',

    store: 'ProductsActiveStore',

    viewConfig: {
        stripeRows: true,
        enableTextSelection: true,
        draggable:false,
        markDirty: false,
        resizable:false,
        trackOver:true,
        scrollable: true,
        focusable: false,
        loadMask: false
        //focusOnToFront: false,
        //preserveScrollOnRefresh: false,
        //focusRow: Ext.emptyFn
    },

    // selModel: {listeners:{}},
    //selModel: Ext.create('Ext.selection.Model', { listeners: {} }),

    collapsible: false,
    suspendLayout: false,
    disableSelection: true,
    enableColumnMove: false,
    enableColumnResize: false,
    multiColumnSort: false,
    columnLines: false,
    rowLines: true,
    frame: false,
    border: false,
    bufferedRenderer: false,
    focusable: false,
    margin: '0 0 10 0',    // (top, right, bottom, left).
    session: true,

    layout: 'fit',

    config: {
        forceStoreLoad: false,
        dirtyStore: false
    },

    // listeners: {
        // groupclick: function( view, node, group, eOpts ) {
            //this.getController().renderHiddenColumnsWhenUnlocked();
        // }
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
    // },
    //
    //plugins:[{
    //    ptype:'lazyitems'
    //},{
    //    ptype:'cellediting'
    //}],
    // defaultListenerScope: true,


    initComponent: function () {
        var me = this;
        var user = esapp.getUser();

        // Ext.util.Observable.capture(this, function(e){console.log('Acquisition - ' + this.id + ': ' + e);});

        me.mon(me, {
            loadstore: function() {
                var productgridstore  = Ext.data.StoreManager.lookup('ProductsActiveStore');
                var acqgridsstore = Ext.data.StoreManager.lookup('DataAcquisitionsStore');
                var ingestiongridstore = Ext.data.StoreManager.lookup('IngestionsStore');
                var eumetcastsourcestore = Ext.data.StoreManager.lookup('EumetcastSourceStore');
                var internetsourcestore = Ext.data.StoreManager.lookup('InternetSourceStore');

                if (me.forceStoreLoad || me.dirtyStore || !productgridstore.isLoaded() || !acqgridsstore.isLoaded() || !ingestiongridstore.isLoaded()) {
                    var myLoadMask = new Ext.LoadMask({
                        msg    : esapp.Utils.getTranslation('loading'), // 'Loading...',
                        target : me
                    });
                    myLoadMask.show();

                    me.getView().getFeature('productcategories').collapseAll();
                    if (productgridstore.isStore) {
                        productgridstore.load({
                            callback: function(records, options, success) {
                                if (acqgridsstore.isStore) {
                                    acqgridsstore.load({
                                        callback: function(records, options, success) {
                                            if (ingestiongridstore.isStore) {
                                                ingestiongridstore.proxy.extraParams = {force: true};
                                                ingestiongridstore.load({
                                                    callback: function(records, options, success){
                                                        myLoadMask.hide();
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

                    me.forceStoreLoad = false;
                    me.dirtyStore = false;
                }
            }
        });

        me.listeners = {
            groupcollapse: function(view, node, group) {
                me.hideCompletenessTooltip();
            },
            groupexpand: function(view, node, group){
                me.hideCompletenessTooltip();

                // var taskRefresh = new Ext.util.DelayedTask(function() {
                //     view.refresh();
                // });
                // taskRefresh.delay(50);
            },
            afterrender: function(){
                var scroller = me.view.getScrollable();

                scroller.on('scroll', function(){
                    var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("_completness_tooltip") != -1}');
                    Ext.each(completenessTooltips, function(item) {
                       item.disable();
                       // item.hide();
                    });
                }, scroller, {single: false});

            }
        }

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
                hidden: ((esapp.Utils.objectExists(user) && user.userlevel < 2) ? false : true),
                iconCls: 'fa fa-lock fa-2x',  // 'fa-unlock' = xf09c  'fa-lock' = xf023
                enableToggle: true,
                scale: 'medium',
                handler:  function(btn) {
                    //Ext.suspendLayouts();
                    //var acq_main = Ext.ComponentQuery.query('panel[name=acquisitionmain]');
                    //var dataacquisitiongrids = Ext.ComponentQuery.query('dataacquisitiongrid');
                    //var ingestiongrids = Ext.ComponentQuery.query('ingestiongrid');
                    //var addproductbtn = Ext.ComponentQuery.query('panel[name=acquisitionmain] > toolbar > button[name=addproduct]');
                    //var checkColumns = Ext.ComponentQuery.query('panel[name=acquisitionmain] checkcolumn, dataacquisitiongrid checkcolumn, ingestiongrid checkcolumn');
                    //var actionColumns = Ext.ComponentQuery.query('panel[name=acquisitionmain] actioncolumn, dataacquisitiongrid actioncolumn, ingestiongrid actioncolumn');

                    if (btn.pressed){

                        btn.setIconCls('fa fa-unlock fa-2x');
                        // Ext.getCmp('addproduct').show();
                        Ext.getCmp('productadmin-acquisition-btn').show();

                        //me.getColumns()[0].show();  // Edit product action column
                        me.getColumns()[1].show();    // Activate Product column
                        me.getColumns()[2].setWidth(500);   // GET
                        me.getColumns()[2].setText(' <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable x-column-header-first" style="border-top: 0px; width: 265px; left: 0px;" tabindex="-1">' +
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

                        me.getColumns()[3].setWidth(785+70);   // INGESTION
                        me.getColumns()[3].setText(' <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 195px; right: auto; left: 0px; margin: 0px; top: 0px;" tabindex="-1">' +
                        '           <div data-ref="titleEl" class="x-column-header-inner">' +
                        '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('subproduct') + '</span>' +
                        '           </div>' +
                        '       </div>' +
                        '       <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 235px; right: auto; left: 195px; margin: 0px; top: 0px;" tabindex="-1">' +
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

                        me.getView().refresh();
                    }
                    else {
                        btn.setIconCls('fa fa-lock fa-2x');
                        // Ext.getCmp('addproduct').hide();
                        Ext.getCmp('productadmin-acquisition-btn').hide();

                        //me.getColumns()[0].hide();
                        me.getColumns()[1].hide();

                        me.getColumns()[2].setWidth(360);   // GET
                        me.getColumns()[2].setText(' <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable x-column-header-first" style="border-top: 0px; width: 230px; left: 0px;" tabindex="-1">' +
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

                        //me.getColumns()[3].setWidth(785);   // INGESTION      CREATES AN ERROR WHEN RESET BACK TO ORIGINAL WIDTH!!!
                        me.getColumns()[3].setText('<div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 160px; right: auto; left: 0px; margin: 0px; top: 0px;" tabindex="-1">' +
                                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('subproduct') + '</span>' +
                                '           </div>' +
                                '       </div>' +
                                '       <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 200px; right: auto; left: 160px; margin: 0px; top: 0px;" tabindex="-1">' +
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

                        me.getView().refresh();

                        //Ext.Object.each(dataacquisitiongrids, function(id, dataacquisitiongrid, myself) {
                        //    dataacquisitiongrid.columns[1].hide();  // Edit Data Source
                        //    dataacquisitiongrid.columns[2].hide();  // Store Native
                        //    //dataacquisitiongrid.columns[3].hide();
                        //});
                        //Ext.Object.each(ingestiongrids, function(id, ingestiongrid, myself) {
                        //    ingestiongrid.columns[0].hide();    // Add Mapset
                        //    //ingestiongrid.columns[0].updateLayout();
                        //    ingestiongrid.columns[3].hide();    // Delete Mapset
                        //    //ingestiongrid.columns[3].updateLayout();
                        //});
                    }

                    //me.getController().renderHiddenColumnsWhenUnlocked();
                    //
                    //Ext.resumeLayouts(true);
                    // acq_main.updateLayout();
                    //var toggleFn = newValue ? 'disable' : 'enable';
                    //Ext.each(this.query('button'), function(item) {
                    //    item[toggleFn]();
                    //});
                }
            }, ' ', ' ', {
            //     xtype: 'button',
            //     text: esapp.Utils.getTranslation('addproduct'),    // 'Add Product',
            //     id: 'addproduct',
            //     name: 'addproduct',
            //     iconCls: 'fa fa-plus-circle fa-2x',
            //     style: {color: 'green'},
            //     hidden: true,
            //     // glyph: 'xf055@FontAwesome',
            //     scale: 'medium',
            //     handler: 'selectProduct'
            // },{
                tooltip:  esapp.Utils.getTranslation('expandall'),    // 'Expand All',
                iconCls: 'expand',
                scale: 'medium',
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
                tooltip:  esapp.Utils.getTranslation('collapseall'),    // 'Collapse All',
                iconCls: 'collapse',
                scale: 'medium',
                handler: function(btn) {
                    var view = btn.up().up().getView();
                    view.getFeature('productcategories').collapseAll();
                }
            }, {
                xtype: 'tbfill'
            }, {
                xtype: 'button',
                text: esapp.Utils.getTranslation('PRODUCTS'),    // 'PRODUCTS',
                id: 'productadmin-acquisition-btn',
                name: 'productadmin-acquisition-btn',
                iconCls: 'fa fa-cog fa-2x',
                style: { color: 'gray' },
                hidden: true,
                scale: 'medium',
                handler: 'openProductAdmin'
            }, '->',
            {
                xtype: 'servicemenubutton',
                service: 'eumetcast',
                text:  esapp.Utils.getTranslation('eumetcast'),    // 'Eumetcast',
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
                    // var productgridstore  = Ext.data.StoreManager.lookup('ProductsActiveStore');
                    // var acqgridsstore = Ext.data.StoreManager.lookup('DataAcquisitionsStore');
                    // var ingestiongridstore = Ext.data.StoreManager.lookup('IngestionsStore');
                    // var eumetcastsourcestore = Ext.data.StoreManager.lookup('EumetcastSourceStore');
                    // var internetsourcestore = Ext.data.StoreManager.lookup('InternetSourceStore');
                    //var view = btn.up().up().getView();
                    var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("_completness_tooltip") != -1}');

                    Ext.each(completenessTooltips, function(item) {
                        item.hide();
                    });

                    me.forceStoreLoad = true;
                    me.fireEvent('loadstore');

                    // var myLoadMask = new Ext.LoadMask({
                    //     msg    : esapp.Utils.getTranslation('loading'), // 'Loading...',
                    //     target : me
                    // });
                    // myLoadMask.show();
                    //
                    // me.getView().getFeature('productcategories').collapseAll();
                    // if (productgridstore.isStore) {
                    //     //Ext.suspendLayouts();
                    //     productgridstore.load({
                    //         callback: function(records, options, success) {
                    //             if (acqgridsstore.isStore) {
                    //                 acqgridsstore.load({
                    //                     callback: function(records, options, success) {
                    //                         //me.getController().renderHiddenColumnsWhenUnlocked();
                    //
                    //                         if (ingestiongridstore.isStore) {
                    //                             ingestiongridstore.proxy.extraParams = {force: true};
                    //                             ingestiongridstore.load({
                    //                                 callback: function(records, options, success){
                    //                                     myLoadMask.hide();
                    //
                    //                                     //Ext.resumeLayouts(true);
                    //                                     //var view = btn.up().up().getView();
                    //                                     ////view.getFeature('productcategories').expandAll();
                    //                                     //view.refresh();
                    //                                 }
                    //                             });
                    //                         }
                    //                     }
                    //                 });
                    //             }
                    //         }
                    //     });
                    // }
                    //
                    // //Ext.resumeLayouts(true);
                    //
                    // eumetcastsourcestore.load();
                    // internetsourcestore.load();

                    me.getController().checkStatusServices();
                    //me.getController().renderHiddenColumnsWhenUnlocked();
                }
            }]
        });

        me.defaults = {
            menuDisabled: true,
            sortable: false,
            groupable:false,
            draggable:false,
            hideable: false,
            stopSelection: true
        };

        me.columns = [
        {
            header: '<div class="grid-header-style">' + esapp.Utils.getTranslation('productcategories') + '</div>',
            menuDisabled: true,
            defaults: {
                menuDisabled: true,
                sortable: false,
                groupable:false,
                draggable:false,
                hideable: false,
                stopSelection: true
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
                        '<b class="smalltext" style="color:darkgrey;">'+esapp.Utils.getTranslation('productcode')+': {productcode}</b>' +
                        '</br>' +
                        '<b class="smalltext" style="color:darkgrey;">'+esapp.Utils.getTranslation('provider')+': {provider}</b>' +
                        '</br>'
                    ),
                width: 330,
                cellWrap:true,
                variableRowHeight:false
            },{
                xtype: 'actioncolumn',
                header: esapp.Utils.getTranslation('active'),   // 'Active',
                hideable: true,
                hidden: Ext.getCmp('lockunlock').pressed ? false : true,
                width: 65,
                align: 'center',
                shrinkWrap: 0,
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
                    // isDisabled: function(view, rowIndex, colIndex, item, record) {
                    //     // Returns true if 'editable' is false (, null, or undefined)
                    //     return false // !record.get('editable');
                    // },
                    handler: function(grid, rowIndex, colIndex, icon, e, record) {
                        var rec = record;
                        // var action = (rec.get('activated') ? 'deactivated' : 'activated');
                        // Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                        rec.get('activated') ? rec.set('activated', false) : rec.set('activated', true);

                        // Ext.data.StoreManager.lookup('ProductsInactiveStore').reload();
                        // me.getController().renderHiddenColumnsWhenUnlocked();
                    }
                }]
            }]
        }, {
            header:  '<div class="grid-header-style">' + esapp.Utils.getTranslation('get') + '</div>',
            id:'acquisitioncolumn',
            menuDisabled: true,
            defaults: {
                menuDisabled: true,
                sortable: false,
                groupable:false,
                draggable:false,
                hideable: false,
                stopSelection: true
            },
            columns: [{
                xtype: 'widgetcolumn',
                width: Ext.getCmp('lockunlock').pressed ? 500 : 360,
                variableRowHeight:false,

                header: ' <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable x-column-header-first" style="border-top: 0px; width: 230px; left: 0px;" tabindex="-1">' +
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

                // listeners: {
                //     render: function(column){
                //         //column.titleEl.removeCls('x-column-header-inner');
                //     }
                // },
                widget: {
                    xtype: 'dataacquisitiongrid',
                    widgetattached: false
                },
                onWidgetAttach: function(col, widget, record) {
                    //console.info(widget.lookupViewModel());
                    var daStore = widget.getViewModel().get('productdatasources');
                    //Ext.suspendLayouts();
                    if (!widget.widgetattached) {
                        //if (daStore.getFilters().items.length == 0) {
                        daStore.setFilters({
                            property: 'productid'
                            , value: record.id
                            , anyMatch: true
                        });
                        //Ext.resumeLayouts(true);
                        //}
                        widget.widgetattached = true;
                    }
                }
            }]
        }, {
            header:  '<div class="grid-header-style">' + esapp.Utils.getTranslation('ingestion') + '</div>',
            menuDisabled: true,
            defaults: {
                menuDisabled: true,
                sortable: false,
                groupable:false,
                draggable:false,
                hideable: false,
                stopSelection: true
            }
            ,columns: [{
                xtype: 'widgetcolumn',
                width: Ext.getCmp('lockunlock').pressed ? 785+70 : 785,
                bodyPadding:5,

                header:
                '       <div class="x-column-header x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 160px; right: auto; left: 0px; margin: 0px; top: 0px;" tabindex="-1">' +
                '           <div data-ref="titleEl" class="x-column-header-inner">' +
                '               <span data-ref="textEl" class="x-column-header-text">' + esapp.Utils.getTranslation('subproduct') + '</span>' +
                '           </div>' +
                '       </div>' +
                '       <div class="x-column-header  x-column-header-align-left x-box-item x-column-header-default x-unselectable" style="border-top: 0px; width: 200px; left: 160px;" tabindex="-1">' +
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
                // listeners: {
                //     render: function(column){
                //         //column.titleEl.removeCls('x-column-header-inner');
                //     }
                // },
                widget: {
                    xtype: 'ingestiongrid',
                    widgetattached: false
                },
                onWidgetAttach: function(col, widget, record) {
                    var daStore = widget.getViewModel().get('productingestions');
                    // Ext.suspendLayouts();
                    if (!widget.widgetattached) {
                        //if (daStore.getFilters().items.length == 0) {
                        daStore.setFilters({
                            property: 'productid'
                            , value: record.id
                            , anyMatch: true
                        });
                        //Ext.resumeLayouts(true);
                        //}
                        widget.widgetattached = true;
                    }
                    // Ext.resumeLayouts(true);
                }
            }]
        },{
            xtype: 'actioncolumn',
            text: esapp.Utils.getTranslation('log'),    // 'Log',
            width: 70,
            menuDisabled: true,
            align:'center',
            stopSelection: true,
            items: [{
                iconCls:'log-icon',
                width:32,
                height:32,
                tooltip: esapp.Utils.getTranslation('showingestionlog'),     // 'Show log of this Ingestion',
                scope: me,
                handler: function (grid, rowIndex, colIndex, icon, e, record) {
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

        me.callParent();
    }
    ,hideCompletenessTooltip: function(){
        // Hide the visible completness tooltips
        var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("_completness_tooltip") != -1}');
        Ext.each(completenessTooltips, function(item) {
           item.hide();
        });
    }
});