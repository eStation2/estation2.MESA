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
        'Ext.Msg',
        'Ext.data.StoreManager',

        'esapp.Utils'

        //,'esapp.view.main.Main'
        //'esapp.*'
    ],

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

    controllers: [
        'Root@esapp.controller'
    ],

    stores: [
         'LogoImages'
        ,'i18nStore'
        ,'LanguagesStore'
        ,'CategoriesStore'
        ,'ProductsActiveStore'
        ,'ProductsInactiveStore'
        ,'DataAcquisitionsStore'
        ,'DataSetsStore'
        ,'ProcessingStore'
        ,'IngestionsStore'
        ,'IPSettingsStore'
        //,'ProductNavigatorStore'  // using viewmodel model binding, which is loaded onAfterRender
        ,'SystemSettingsStore'
        ,'TimeLineStore'
    ],

    //models: [
        //'ProductNavigator',
        //'ProductNavigatorMapSet',
        //'ProductNavigatorMapSetDataSet',
        //'TimeseriesProduct',
        //'esapp.model.Dashboard',
        //'esapp.model.Version',
        //'esapp.model.Themas',
        //'esapp.model.InternetSource',
        //'esapp.model.EumetcastSource'
        ////,'TimeserieProductMapSet'
        ////,'TimeserieProductMapSetDataSet'
    //],

    // create a reference in Ext.application so we can access it from multiple functions
    splashscreen: {},

    init: function () {
        //console.info('init');
        Ext.tip.QuickTipManager.init();

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
                //console.info(esapp.globals['selectedLanguage']);

                Ext.data.StoreManager.lookup('i18nStore').load({
                    params:{lang:esapp.globals['selectedLanguage']},
                    callback: function(records, options, success){

                        // start the mask on the body and get a reference to the mask
                        splashscreen = Ext.getBody().mask(esapp.Utils.getTranslation('splashscreenmessage'), 'splashscreen');

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

                        task.delay(6500);

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
            }
        });

        this.callParent();
    },

    launch: function () {
        //SenchaInspector.init();
        //console.info('launch');
        // Ext.getBody().addCls('graybgcolor');
        Ext.setGlyphFontFamily('FontAwesome');
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

        //Ext.data.StoreManager.lookup('CategoriesStore').load();

        this.callParent();

    }
});


