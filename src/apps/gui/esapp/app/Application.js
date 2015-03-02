/**
 * The main application class. An instance of this class is created by app.js when it calls
 * Ext.application(). This is the ideal place to handle application launch and initialization
 * details.
 */
Ext.define('esapp.Application', {
    extend: 'Ext.app.Application',

    name: 'esapp',

    requires: [
        // 'Ext.app.bindinspector.*',
        'Ext.app.*',
        'Ext.window.Toast',
        'Ext.state.CookieProvider',
        'Ext.window.MessageBox',
        'Ext.tip.QuickTipManager',
        'esapp.*'
    ],

    views: [
        'header.Header',

        'dashboard.Dashboard',

        'acquisition.Acquisition',
        //'acquisition.DataAcquisition',
        //'acquisition.Ingestion',
        //'acquisition.product.editProduct',
        //'acquisition.product.selectProduct',

        'processing.Processing',
        //'processing.ProductMapSet',
        //'processing.MapSetFinalOutputSubProduct',

        'datamanagement.DataManagement',
        //'datamanagement.ProductMapSet',
        //'datamanagement.MapSetDataSet',

        'analysis.analysisMain',

        'system.systemsettings',

        'widgets.datasetCompletenessChart',
        'widgets.ServiceMenuButton'


    ],

    controllers: [
        'Root@esapp.controller'
    ],

    stores: [
         'LogoImages'
        ,'ProductsActiveStore'
        ,'ProductsInactiveStore'
        ,'DataAcquisitionsStore'
        ,'IngestionsStore'
        ,'DataSetsStore'
        ,'ProcessingStore'
        ,'SystemSettingsStore'
        //,'ProductNavigatorStore'
    ],

    models: ['ProductNavigator', 'ProductNavigatorMapSet', 'ProductNavigatorMapSetDataSet'],

//    onBeforeLaunch: function () {
//
//        this.callParent();
//    },

    launch: function () {
        // TODO - Launch the application
        // Ext.getBody().addCls('graybgcolor');
        Ext.setGlyphFontFamily('FontAwesome');
        // Ext.setGlyphFontFamily('Pictos');
        Ext.tip.QuickTipManager.init();
        Ext.state.Manager.setProvider(Ext.create('Ext.state.CookieProvider'));


//        Ext.define('Ext.LazyItems', {
//            extend: 'Ext.AbstractPlugin',
//
//             alias: 'plugin.lazyitems',
//
//            init: function(comp) {
//                this.callParent(arguments);
//
//                if (this.items) {
//                    // Eager instantiation means create the child items now
//                    if (this.eagerInstantiation) {
//                        this.items = comp.prepareItems(this.items);
//                    }
//                }
//
//                // We need to jump in right before the beforeRender call
//                comp.beforeRender = Ext.Function.createInterceptor(comp.beforeRender, this.beforeComponentRender, this);
//            },
//
//            // Add the child items at the last possible moment.
//            beforeComponentRender: function() {
//                this.cmp.add(this.items);
//
//                // Remove the interceptor
//                delete this.cmp.beforeComponentRender;
//            }
//        });

        // Capture events to console
        // by changing "fireEvent" in the below code to "doFireEvent", non-custom events like tap and release will be revealed.
//        Ext.Component.prototype.fireEvent = Ext.Function.createInterceptor(Ext.Component.prototype.fireEvent, function() {
//          console.log(this.$className, arguments, this);
//          return true;
//        });

        //        // No mouse version
        //        Ext.Component.prototype.fireEvent =
        //        Ext.Function.createInterceptor(Ext.Component.prototype.fireEvent, function() {
        //          if (arguments && arguments[0].indexOf("mouse") === -1 && arguments[0] != "uievent") {
        //            console.log(this.$className, arguments, this);
        //          }
        //          return true;
        //        });


//        Ext.Msg.show({title: 'Built using Sencha Ext JS ' + Ext.getVersion('extjs'), closable: true});

//        Ext.util.Observable.capture(Ext.getCmp('my-comp'), console.info)

//        Ext.define('Ext.override.grid.column.Widget', {
//            override: 'Ext.grid.column.Widget',
//            privates: {
//                onViewRefresh: function(view, records) {
//                    var me = this,
//                        rows = view.all,
//                        hasAttach = !! me.onWidgetAttach,
//                        oldWidgetMap = me.liveWidgets,
//                        dataIndex = me.dataIndex,
//                        isFixedSize = me.isFixedSize,
//                        cell, widget, el, width, recordId,
//                        itemIndex, recordIndex, record, id, lastBox;
//                    if (me.rendered && !me.hidden) {
//                        me.liveWidgets = {};
//                        Ext.suspendLayouts();
//                        for (itemIndex = rows.startIndex, recordIndex = 0; itemIndex <= rows.endIndex; itemIndex++, recordIndex++) {
//                            record = records[recordIndex];
//                            if (record.isNonData) {
//                                continue;
//                            }
//                            recordId = record.internalId;
//                            cell = view.getRow(rows.item(itemIndex)).cells[me.getVisibleIndex()].firstChild;
//                            widget = me.liveWidgets[recordId] = oldWidgetMap[recordId] || me.getFreeWidget();
//                            delete oldWidgetMap[recordId];
//                            lastBox = me.lastBox;
//                            if (lastBox && !isFixedSize && width === undefined) {
//                                width = lastBox.width - parseInt(me.getCachedStyle(cell, 'padding-left'), 10) - parseInt(me.getCachedStyle(cell, 'padding-right'), 10);
//                            }
//                            Ext.fly(cell).empty();
//                            if (el = (widget.el || widget.element)) {
//                                cell.appendChild(el.dom);
//                                if (!isFixedSize) {
//                                    widget.setWidth(width);
//                                }
//                            } else {
//                                if (!isFixedSize) {
//                                    widget.width = width;
//                                }
//                                widget.render(cell);
//                            }
//                            if (widget.defaultBindProperty && dataIndex) {
//                                widget.setConfig(widget.defaultBindProperty, records[recordIndex].get(dataIndex));
//                            }
//                            widget.$widgetRecord = record;
//                            widget.$widgetColumn = me;
//                            if (hasAttach) {
//                                me.onWidgetAttach(widget, record);
//                            }
//                        }
//                        Ext.resumeLayouts(true);
//                        for (id in oldWidgetMap) {
//                            widget = oldWidgetMap[id];
//                            widget.$widgetRecord = widget.$widgetColumn = null;
//                            me.freeWidgetStack.unshift(widget);
//                            Ext.detachedBodyEl.dom.appendChild((widget.el || widget.element).dom);
//                        }
//                    }
//                }
//            }
//        });

    }
});


