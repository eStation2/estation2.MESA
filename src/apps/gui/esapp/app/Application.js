/**
 * The main application class. An instance of this class is created by app.js when it calls
 * Ext.application(). This is the ideal place to handle application launch and initialization
 * details.
 */
Ext.define('esapp.Application', {
    extend: 'Ext.app.Application',

    name: 'esapp',

    requires: [
         //'Ext.app.bindinspector.*',
        'Ext.app.*',
        'Ext.window.Toast',
        'Ext.state.CookieProvider',
        'Ext.tip.QuickTipManager',

        'esapp.Utils'
        //,'esapp.view.main.Main'
        //'esapp.*'
    ],

    views: [
        'header.Header'
        //'dashboard.Dashboard',
        //'acquisition.Acquisition',
        //'processing.Processing',
        //'datamanagement.DataManagement',
        //'analysis.analysisMain',
        //'system.systemsettings',
        //'widgets.datasetCompletenessChart',
        //'widgets.ServiceMenuButton'
    ],

    controllers: [
        'Root@esapp.controller'
    ],

    stores: [
         'LogoImages'
        ,'LanguagesStore'
        ,'i18nStore'
        ,'ProductsActiveStore'
        ,'ProductsInactiveStore'
        ,'DataAcquisitionsStore'
        ,'IngestionsStore'
        ,'DataSetsStore'
        ,'ProcessingStore'
        ,'SystemSettingsStore'
        ,'IPSettingsStore'
        ,'CategoriesStore'
        //,'ProductNavigatorStore'
    ],

    models: [
        'ProductNavigator',
        'ProductNavigatorMapSet',
        'ProductNavigatorMapSetDataSet',
        'TimeseriesProduct',
        'esapp.model.Dashboard',
        'esapp.model.Version',
        'esapp.model.Themas',
        'esapp.model.InternetSource',
        'esapp.model.EumetcastSource'
        //,'TimeserieProductMapSet'
        //,'TimeserieProductMapSetDataSet'
    ],

    // create a reference in Ext.application so we can access it from multiple functions
    splashscreen: {},

    init: function () {
        //console.info('Application Init()');

        Ext.tip.QuickTipManager.init();

        // start the mask on the body and get a reference to the mask
        splashscreen = Ext.getBody().mask('Loading eStation2, please stand by ...', 'splashscreen');

        this.callParent();
    },

    //onBeforeLaunch: function () {
    //    //console.info("onbeforelaunch!!!");
    //
    //    this.callParent();
    //},

    launch: function () {
        //console.info("launch!!!");
        //SenchaInspector.init();

        Ext.Ajax.timeout = 300000; // 300 seconds
        Ext.override(Ext.form.Basic, {     timeout: Ext.Ajax.timeout / 1000 });
        Ext.override(Ext.data.proxy.Server, {     timeout: Ext.Ajax.timeout });
        Ext.override(Ext.data.Connection, {     timeout: Ext.Ajax.timeout });

        // Ext.getBody().addCls('graybgcolor');
        Ext.setGlyphFontFamily('FontAwesome');
        // Ext.setGlyphFontFamily('Pictos');
        Ext.tip.QuickTipManager.init();
        Ext.state.Manager.setProvider(Ext.create('Ext.state.CookieProvider'));

        //var link = '<link rel="icon" href="resources/img/africa.ico" type="image/gif" sizes="16x16">'
        var link = document.createElement('link');
        link.type = 'image/gif';  // 'image/ico';
        link.rel = 'icon';
        link.href = 'resources/img/africa.ico';
        link.sizes = '16x16';
        document.getElementsByTagName('head')[0].appendChild(link);


        // quick and dirty override to have the language combo work
        Ext.tab.Bar.prototype.beforeFocusableChildFocus = function(child, e) {
            var me = this,
                mixin = me.mixins.focusablecontainer;

            mixin.beforeFocusableChildFocus.call(me, child, e);

            if (!child.active && Ext.isFunction(child.activate)) {
                child.activate();
            }

            me.doActivateTab(child);
        };

        Ext.data.StoreManager.lookup('CategoriesStore').load();

        esapp.globals = [];
        esapp.globals['selectedLanguage'] = 'eng';
        Ext.data.StoreManager.lookup('LanguagesStore').load({
            callback: function(records, options, success){
                records.forEach(function(language) {
                    if (language.get('selected') == true){
                        esapp.globals['selectedLanguage'] = language.get('langcode')
                    }
                });
                //if (esapp.globals['selectedLanguage'] == 'fra')
                //    Ext.require('Ext.locale.fr');
                //else Ext.require('Ext.locale.en');

                //Ext.getCmp("languageCombo").setValue(esapp.globals['selectedLanguage']);
                //console.info(esapp.globals['selectedLanguage']);

                Ext.data.StoreManager.lookup('i18nStore').load({
                    params:{lang:esapp.globals['selectedLanguage']},
                    callback: function(records, options, success){

                        Ext.create('esapp.view.main.Main');

                        if (esapp.globals['selectedLanguage'] == 'fra') {
                            Highcharts.setOptions({
                                lang: {
                                    contextButtonTitle: 'Graphique menu contextuel',  // 'Chart context menu',
                                    downloadJPEG: 'Télécharger image JPEG',  // 'Download JPEG image',
                                    downloadPDF: 'Télécharger le document PDF',  // 'Download PDF document',
                                    downloadPNG: 'Télécharger l\'image PNG',  // 'Download PNG image',
                                    downloadSVG: 'Télécharger image vectorielle SVG',  // 'Download SVG vector image',
                                    drillUpText: 'Retour à {series.name}',  // 'Back to {series.name}',
                                    loading: 'Chargement...',  // 'Loading...',
                                    noData: 'Aucune donnée à afficher',  // 'No data to display',
                                    printChart: 'Imprimer tableau',  // 'Print chart',
                                    resetZoom: 'Réinitialiser zoom',  // 'Reset zoom',
                                    resetZoomTitle: 'Niveau de zoom réinitialiser 1:1',  // 'Reset zoom level 1:1',
                                    shortMonths: [ "Janv." , "Févr." , "Mars" , "Avril" , "Mai" , "Juin" , "Juil." , "Août" , "Sept." , "Oct." , "Nov." , "Déc."],
                                    months: ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
                                    weekdays: ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
                                }
                            });
                        }
                    }
                });
            }
        });

        var task = new Ext.util.DelayedTask(function() {
            // fade out the body mask
            splashscreen.fadeOut({
                duration: 500,
                remove: true
            });

            // fade out the message
            splashscreen.next().fadeOut({
                duration: 500,
                remove: true
            });

        });

        task.delay(2000);

        //Ext.create('esapp.view.main.Main',{renderTo: Ext.getBody()});
        //mainview = Ext.create('esapp.view.main.Main',{});
        //mainview.show();
        //Ext.getCmp("languageCombo").setValue(esapp.globals['selectedLanguage']);

        this.callParent();

        //esapp.globals = [];
        //esapp.globals['selectedLanguage'] = 'eng';
        //Ext.data.StoreManager.lookup('LanguagesStore').load({
        //    callback: function(records, options, success){
        //        records.forEach(function(language) {
        //            if (language.get('selected') == true){
        //                esapp.globals['selectedLanguage'] = language.get('langcode')
        //            }
        //        });
        //
        //        Ext.getCmp("languageCombo").setValue(esapp.globals['selectedLanguage']);
        //
        //        Ext.data.StoreManager.lookup('i18nStore').load({
        //            params:{lang:esapp.globals['selectedLanguage']},
        //            callback: function(records, options, success){
        //                //Ext.create('esapp.view.main.Main');
        //            }
        //        });
        //    }
        //});

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


