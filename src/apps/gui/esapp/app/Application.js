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

    //controllers: [
    //    'Root@esapp.controller'
    //],

    stores: [
         'LogoImages'
        ,'ProcessingStore'          // no autoload
        ,'i18nStore'
        ,'LanguagesStore'
        ,'SystemSettingsStore'
        ,'CategoriesStore'
        ,'FrequenciesStore'
        ,'DateFormatsStore'
        ,'DataTypesStore'
        ,'LogosMapView'
        ,'LayersStore'
        ,'LegendsStore'
        ,'EumetcastSourceStore'
        ,'InternetSourceStore'
        ,'ProductsInactiveStore'
        ,'ProductsActiveStore'      // no autoload
        ,'DataAcquisitionsStore'    // no autoload
        ,'IngestionsStore'          // no autoload
        ,'TimeseriesProductsStore'
        ,'TSDrawPropertiesStore'
        ,"ColorSchemesStore"
        ,'DataSetsStore'            // no autoload
    ],

    // create a reference in Ext.application so we can access it from multiple functions
    splashscreen: {},

    //init: function () {
    onBeforeLaunch: function () {
        //console.info('onBeforeLaunch');
        var me = this;
        //console.info(me);

        Ext.override(Ext.tip.QuickTip, {
            dismissDelay: 20000
        });

        Ext.tip.QuickTipManager.init();
        Ext.setGlyphFontFamily('FontAwesome');
        Ext.state.Manager.setProvider(Ext.create('Ext.state.CookieProvider'));

        Ext.Ajax.timeout = 300000; // 300 seconds
        //Ext.override(Ext.form.Basic, {     timeout: Ext.Ajax.timeout / 1000 });
        Ext.override(Ext.data.proxy.Server, {     timeout: Ext.Ajax.timeout });
        Ext.override(Ext.data.Connection, {     timeout: Ext.Ajax.timeout });

        esapp.globals = [];

        // Ext.data.StoreManager.lookup('TimeseriesProductsStore').load();

        esapp.globals['selectedLanguage'] = 'eng';
        Ext.data.StoreManager.lookup('LanguagesStore').load({
            callback: function(records, options, success){
                records.forEach(function(language) {
                    if (language.get('selected') == true){
                        esapp.globals['selectedLanguage'] = language.get('langcode')
                    }
                });

                Ext.data.StoreManager.lookup('i18nStore').load({
                    params:{lang:esapp.globals['selectedLanguage']},
                    callback: function(records, options, success){

                        // start the mask on the body and get a reference to the mask
                        var splashscreen = Ext.getBody().mask(esapp.Utils.getTranslation('splashscreenmessage'), 'splashscreen');
                        // fade out the body mask
                        splashscreen.fadeOut({
                            duration: 4000,
                            remove: true
                        });

                        Ext.Loader.loadScript({
                            url: 'app/CustomVTypes.js',
                            onLoad: function (options) {
                                //console.info('CustomVTypes');
                            }
                        });

                        //Ext.apply(Ext.form.VTypes, {
                        //    GeoJSON:  function(v) {
                        //        v = v.replace(/^\s|\s$/g, ""); //trims string
                        //        if (v.match(/([^\/\\]+)\.(geojson)$/i) )
                        //            return true;
                        //        else
                        //            return false;
                        //    },
                        //    GeoJSONText: esapp.Utils.getTranslation('vtype_geojson')    // 'Must be a .geojson file.'
                        //});
                        //
                        //Ext.create('esapp.view.main.Main');

                        var taskLaunch = new Ext.util.DelayedTask(function() {
                            me.launch();
                        });
                        taskLaunch.delay(500);

                    }
                });

                //if (esapp.globals['selectedLanguage'] == 'fra')
                //    Ext.require('Ext.locale.fr');
                //else Ext.require('Ext.locale.en');
                //
                //Ext.getCmp("languageCombo").setValue(esapp.globals['selectedLanguage']);
                //console.info(esapp.globals['selectedLanguage']);

                if (esapp.globals['selectedLanguage'] == 'fra') {

                    var url = '../static/ext/packages/ext-locale/build/ext-locale-fr.js';
                    Ext.Loader.loadScript({
                        url: url,
                        onLoad: function (options) {
                            //console.info('French local loaded!');
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
            }
        });


        esapp.globals['typeinstallation'] = 'full';
        esapp.globals['role'] = 'pc2';
        esapp.globals['mode'] = 'nominal';
        Ext.Ajax.request({
            method: 'POST',
            url: 'typeinstallation',
            success: function(response, opts){
                var resp = Ext.JSON.decode(response.responseText);
                if (resp.typeinstallation != ''){
                    esapp.globals['typeinstallation'] = resp.typeinstallation;
                }
                if (resp.role != ''){
                    esapp.globals['role'] = resp.role;
                }
                if (resp.mode != ''){
                    esapp.globals['mode'] = resp.mode;
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
        //this.callParent();
    },

    launch: function () {
        //console.info('launch');
        // Ext.getBody().addCls('graybgcolor');

        //var link = '<link rel="icon" href="resources/img/africa.ico" type="image/gif" sizes="16x16">'
        var link = document.createElement('link');
        link.type = 'image/gif';  // 'image/ico';
        link.rel = 'icon';
        link.href = 'resources/img/africa.ico';
        link.sizes = '16x16';
        document.getElementsByTagName('head')[0].appendChild(link);


        if (esapp.globals['typeinstallation'] == 'windows'){
            Ext.data.StoreManager.lookup('DataSetsStore').load();
        }
        else {
            if (esapp.globals['role'] == 'pc2') {
                Ext.data.StoreManager.lookup('ProductsActiveStore').load();
                Ext.data.StoreManager.lookup('DataAcquisitionsStore').load();
                Ext.data.StoreManager.lookup('IngestionsStore').load();
            }
            if (esapp.globals['role'] == 'pc3' && esapp.globals['mode'] == 'recovery'){
                Ext.data.StoreManager.lookup('ProductsActiveStore').load();
                Ext.data.StoreManager.lookup('DataAcquisitionsStore').load();
                Ext.data.StoreManager.lookup('IngestionsStore').load();
            }
            Ext.data.StoreManager.lookup('ProcessingStore').load();
            Ext.data.StoreManager.lookup('DataSetsStore').load();
        }

        // var delay = 500;
        // if (!Ext.data.StoreManager.lookup('TimeseriesProductsStore').isLoaded()){
        //     delay = 2000;
        // }

        var taskMain = new Ext.util.DelayedTask(function() {
            Ext.create('esapp.view.main.Main');
        });
        taskMain.delay(500);

        this.callParent();
    }
});


