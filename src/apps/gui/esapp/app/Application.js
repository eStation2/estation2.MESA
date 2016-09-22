//Ext.Loader.setPath({
//    'Ext.ux.upload' : '/eStation2/lib/js/Ext.ux/extjs-upload-widget-master/lib/upload/'
//});


//Ext.override(Ext.selection.RowModel, {
//    onRowMouseDown: function(view, record, item, index, e) {
//        console.info('Ext.selection.RowModel - onRowMouseDown');
//
//        //IE fix: set focus to the first DIV in selected row
//        Ext.get(item).down('div').focus();
//
//        if (!this.allowRightMouseSelection(e)) {
//            return;
//        }
//        view.el.focus(200); // Focus the element in 0.2 seconds - time for the click to happen...
//        this.selectWithEvent(record, e);
//    }
//});


/**
 * The main application class. An instance of this class is created by app.js when it calls
 * Ext.application(). This is the ideal place to handle application launch and initialization
 * details.
 */
Ext.define('esapp.Application', {
    extend: 'Ext.app.Application',

    name: 'esapp',

    requires: [
        'esapp.Utils',
        'Ext.window.Toast',
        'Ext.state.CookieProvider',
        'Ext.tip.QuickTipManager'
        //,'esapp.view.main.Main'
    ],

    //requires: [
    //     //'Ext.app.bindinspector.*',
    //    //'Ext.app.*',
    //    'Ext.window.Toast',
    //    'Ext.state.CookieProvider',
    //    'Ext.tip.QuickTipManager',
    //    //'Ext.Msg',
    //    //'Ext.data.StoreManager',
    //
    //    'esapp.Utils'
    //
    //    //,'esapp.view.main.Main'
    //    //'esapp.*'
    //],

    //views:['help.help'],

    //views: [
    //    'header.Header',
    //    'dashboard.Dashboard',
    //    'acquisition.Acquisition',
    //    'processing.Processing',
    //    'datamanagement.DataManagement',
    //    'analysis.analysisMain',
    //    'system.systemsettings',
    //    'help.help',
    //    'widgets.datasetCompletenessChart',
    //    'widgets.ServiceMenuButton'
    //],

    //controllers: [
    //    'Root@esapp.controller'
    //],

    stores: [
         'LogoImages'
        ,'i18nStore'
        ,'LanguagesStore'
        ,'CategoriesStore'
        ,'FrequenciesStore'
        ,'DateFormatsStore'
        ,'DataTypesStore'
        ,'EumetcastSourceStore'
        ,'InternetSourceStore'
        ,'LayersStore'

        ,'ProductsActiveStore'
        ,'ProductsInactiveStore'
        ,'DataAcquisitionsStore'
        ,'IngestionsStore'
        ,'DataSetsStore'
        ,'ProcessingStore'

//        ,'IPSettingsStore'
        //,'ProductNavigatorStore'  // using viewmodel model binding, which is loaded onAfterRender
        ,'SystemSettingsStore'
        //,'TimeLineStore'
    ],

    //models: [
        //'EumetcastSource'
        //'ProductNavigator',
        //'ProductNavigatorMapSet',
        //'ProductNavigatorMapSetDataSet',
        //'TimeseriesProduct'
        //'esapp.model.Dashboard',
        //'esapp.model.Version',
        //'esapp.model.Themas',
        //'esapp.model.InternetSource',
        //'esapp.model.EumetcastSource'
        //,'TimeserieProductMapSet'
        //,'TimeserieProductMapSetDataSet'
    //],

    // create a reference in Ext.application so we can access it from multiple functions
    splashscreen: {},

    //init: function () {
    onBeforeLaunch: function () {
        console.info('onBeforeLaunch');
        var me = this;
        //console.info(me);

        Ext.tip.QuickTipManager.init();
        Ext.setGlyphFontFamily('FontAwesome');
        Ext.state.Manager.setProvider(Ext.create('Ext.state.CookieProvider'));

        Ext.Ajax.timeout = 300000; // 300 seconds
        //Ext.override(Ext.form.Basic, {     timeout: Ext.Ajax.timeout / 1000 });
        Ext.override(Ext.data.proxy.Server, {     timeout: Ext.Ajax.timeout });
        Ext.override(Ext.data.Connection, {     timeout: Ext.Ajax.timeout });

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
                console.info(esapp.globals['selectedLanguage']);

                if (esapp.globals['selectedLanguage'] == 'fra') {

                    var url = '../static/ext/packages/ext-locale/build/ext-locale-fr.js';
                    Ext.Loader.loadScript({
                        url: url,
                        onLoad: function (options) {
                            console.info('French local loaded!');
                        }
                    });

                    Highcharts.setOptions({
                        //global: {
                        //    canvasToolsURL: ''
                        //},
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
                            rangeSelectorFrom:'De',
                            rangeSelectorTo: 'à',
                            resetZoom: 'Réinitialiser zoom',  // 'Reset zoom',
                            resetZoomTitle: 'Niveau de zoom réinitialiser 1:1',  // 'Reset zoom level 1:1',
                            shortMonths: [ "Janv." , "Févr." , "Mars" , "Avril" , "Mai" , "Juin" , "Juil." , "Août" , "Sept." , "Oct." , "Nov." , "Déc."],
                            months: ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
                            weekdays: ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
                        }
                    });
                }

                console.info(esapp.Utils);

                Ext.data.StoreManager.lookup('i18nStore').load({
                    params:{lang:esapp.globals['selectedLanguage']},
                    callback: function(records, options, success){

                        Ext.apply(Ext.form.VTypes, {
                            GeoJSON:  function(v) {
                                v = v.replace(/^\s|\s$/g, ""); //trims string
                                if (v.match(/([^\/\\]+)\.(geojson)$/i) )
                                    return true;
                                else
                                    return false;
                            },
                            GeoJSONText: esapp.Utils.getTranslation('vtype_geojson')    // 'Must be a .geojson file.'
                        });

                        //Ext.create('esapp.view.main.Main');

                        me.launch();
                    }
                });
            }
        });

        //this.callParent();
    },

    launch: function () {
        console.info('launch');
        // Ext.getBody().addCls('graybgcolor');


        //var link = '<link rel="icon" href="resources/img/africa.ico" type="image/gif" sizes="16x16">'
        var link = document.createElement('link');
        link.type = 'image/gif';  // 'image/ico';
        link.rel = 'icon';
        link.href = 'resources/img/africa.ico';
        link.sizes = '16x16';
        document.getElementsByTagName('head')[0].appendChild(link);

        // start the mask on the body and get a reference to the mask
        splashscreen = Ext.getBody().mask(esapp.Utils.getTranslation('splashscreenmessage'), 'splashscreen');

        var task = new Ext.util.DelayedTask(function() {
            // fade out the body mask
            splashscreen.fadeOut({
                duration: 500,
                remove: true
            });

            //// fade out the message
            //splashscreen.fadeOut({
            //    duration: 500,
            //    remove: true
            //});

        });
        task.delay(2000);

        Ext.data.StoreManager.lookup('ProductsActiveStore').load();
////                        Ext.data.StoreManager.lookup('ProductsInactiveStore').load();
//        Ext.data.StoreManager.lookup('DataAcquisitionsStore').load();
//        Ext.data.StoreManager.lookup('IngestionsStore').load();
////                        Ext.data.StoreManager.lookup('DataSetsStore').load();
//        Ext.data.StoreManager.lookup('ProcessingStore').load();

        Ext.create('esapp.view.main.Main');

        this.callParent();
    }

//    launch: function () {
//
//        //SenchaInspector.init();
//        console.info('launch');
//        // Ext.getBody().addCls('graybgcolor');
//        Ext.setGlyphFontFamily('FontAwesome');
//        Ext.tip.QuickTipManager.init();
//        Ext.state.Manager.setProvider(Ext.create('Ext.state.CookieProvider'));
//
//        //var link = '<link rel="icon" href="resources/img/africa.ico" type="image/gif" sizes="16x16">'
//        var link = document.createElement('link');
//        link.type = 'image/gif';  // 'image/ico';
//        link.rel = 'icon';
//        link.href = 'resources/img/africa.ico';
//        link.sizes = '16x16';
//        document.getElementsByTagName('head')[0].appendChild(link);
//
//
//        //// quick and dirty override to have the language combo work
//        //Ext.tab.Bar.prototype.beforeFocusableChildFocus = function(child, e) {
//        //    var me = this,
//        //        mixin = me.mixins.focusablecontainer;
//        //
//        //    mixin.beforeFocusableChildFocus.call(me, child, e);
//        //
//        //    if (!child.active && Ext.isFunction(child.activate)) {
//        //        child.activate();
//        //    }
//        //
//        //    me.doActivateTab(child);
//        //};
//
//        //Ext.data.StoreManager.lookup('CategoriesStore').load();
//
//
//        Ext.Ajax.timeout = 300000; // 300 seconds
//        //Ext.override(Ext.form.Basic, {     timeout: Ext.Ajax.timeout / 1000 });
//        Ext.override(Ext.data.proxy.Server, {     timeout: Ext.Ajax.timeout });
//        Ext.override(Ext.data.Connection, {     timeout: Ext.Ajax.timeout });
//
//        esapp.globals = [];
//        esapp.globals['selectedLanguage'] = 'eng';
//        Ext.data.StoreManager.lookup('LanguagesStore').load({
//            callback: function(records, options, success){
//                records.forEach(function(language) {
//                    if (language.get('selected') == true){
//                        esapp.globals['selectedLanguage'] = language.get('langcode')
//                    }
//                });
//                //if (esapp.globals['selectedLanguage'] == 'fra')
//                //    Ext.require('Ext.locale.fr');
//                //else Ext.require('Ext.locale.en');
//
//                //Ext.getCmp("languageCombo").setValue(esapp.globals['selectedLanguage']);
//                //console.info(esapp.globals['selectedLanguage']);
//
//                Ext.data.StoreManager.lookup('i18nStore').load({
//                    params:{lang:esapp.globals['selectedLanguage']},
//                    callback: function(records, options, success){
//
//                        Ext.apply(Ext.form.VTypes, {
//                            GeoJSON:  function(v) {
//                                v = v.replace(/^\s|\s$/g, ""); //trims string
//                                if (v.match(/([^\/\\]+)\.(geojson)$/i) )
//                                    return true;
//                                else
//                                    return false;
//                            },
//                            GeoJSONText: esapp.Utils.getTranslation('vtype_geojson')    // 'Must be a .geojson file.'
//                        });
//
//                        // start the mask on the body and get a reference to the mask
//                        splashscreen = Ext.getBody().mask(esapp.Utils.getTranslation('splashscreenmessage'), 'splashscreen');
//
//                        var task = new Ext.util.DelayedTask(function() {
//                            // fade out the body mask
//                            splashscreen.fadeOut({
//                                duration: 500,
//                                remove: true
//                            });
//
//                            // fade out the message
//                            splashscreen.next().fadeOut({
//                                duration: 500,
//                                remove: true
//                            });
//
//                        });
//
//                        task.delay(3000);
//
//                        Ext.data.StoreManager.lookup('ProductsActiveStore').load();
////                        Ext.data.StoreManager.lookup('ProductsInactiveStore').load();
//                        Ext.data.StoreManager.lookup('DataAcquisitionsStore').load();
//                        Ext.data.StoreManager.lookup('IngestionsStore').load();
////                        Ext.data.StoreManager.lookup('DataSetsStore').load();
//                        Ext.data.StoreManager.lookup('ProcessingStore').load();
//
//                        Ext.create('esapp.view.main.Main');
//
//                        if (esapp.globals['selectedLanguage'] == 'fra') {
//                            Highcharts.setOptions({
//                                //global: {
//                                //    canvasToolsURL: ''
//                                //},
//                                lang: {
//                                    contextButtonTitle: 'Graphique menu contextuel',  // 'Chart context menu',
//                                    downloadJPEG: 'Télécharger image JPEG',  // 'Download JPEG image',
//                                    downloadPDF: 'Télécharger le document PDF',  // 'Download PDF document',
//                                    downloadPNG: 'Télécharger l\'image PNG',  // 'Download PNG image',
//                                    downloadSVG: 'Télécharger image vectorielle SVG',  // 'Download SVG vector image',
//                                    drillUpText: 'Retour à {series.name}',  // 'Back to {series.name}',
//                                    loading: 'Chargement...',  // 'Loading...',
//                                    noData: 'Aucune donnée à afficher',  // 'No data to display',
//                                    printChart: 'Imprimer tableau',  // 'Print chart',
//                                    rangeSelectorFrom:'De',
//                                    rangeSelectorTo: 'à',
//                                    resetZoom: 'Réinitialiser zoom',  // 'Reset zoom',
//                                    resetZoomTitle: 'Niveau de zoom réinitialiser 1:1',  // 'Reset zoom level 1:1',
//                                    shortMonths: [ "Janv." , "Févr." , "Mars" , "Avril" , "Mai" , "Juin" , "Juil." , "Août" , "Sept." , "Oct." , "Nov." , "Déc."],
//                                    months: ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
//                                    weekdays: ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
//                                }
//                            });
//                        }
//                    }
//                });
//            }
//        });
//
//        this.callParent();
//
//    }
});


