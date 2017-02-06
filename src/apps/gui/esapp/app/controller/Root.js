/**
 * The main application controller. This is a good place to handle things like routes.
 */
Ext.define('esapp.controller.Root', {
    extend: 'Ext.app.Controller',

//    requires: [
//         //'Ext.app.bindinspector.*',
//        'Ext.app.*',
//        'Ext.window.Toast',
//        'Ext.state.CookieProvider',
//        'Ext.tip.QuickTipManager',
//        'Ext.Msg',
//        'Ext.data.StoreManager',
//
//        'esapp.Utils'
//
//        //,'esapp.view.main.Main'
//        //'esapp.*'
//    ],
//
//    onLaunch: function(){
//        console.info('root controler onLaunch');
//        Ext.tip.QuickTipManager.init();
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
//    },


    // create a reference in Ext.application so we can access it from multiple functions
    init: function () {

        this.callParent(arguments);
    }
});
