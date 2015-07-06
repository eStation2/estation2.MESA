/**
 * The main application controller. This is a good place to handle things like routes.
 */
Ext.define('esapp.controller.Root', {
    extend: 'Ext.app.Controller',

    //requires: [
    //     //'Ext.app.bindinspector.*',
    //    'Ext.app.*',
    //    'Ext.window.Toast',
    //    'Ext.state.CookieProvider',
    //    'Ext.window.MessageBox',
    //    'Ext.tip.QuickTipManager'
    //    //'esapp.Utils',
    //    //,'esapp.view.main.Main'
    //    //'esapp.*'
    //],
    //
    //views: [
    //    'header.Header',
    //    'dashboard.Dashboard',
    //    'acquisition.Acquisition',
    //    'processing.Processing',
    //    'datamanagement.DataManagement',
    //    'analysis.analysisMain',
    //    'system.systemsettings',
    //    'widgets.datasetCompletenessChart',
    //    'widgets.ServiceMenuButton'
    //],
    //
    //controllers: [
    //    'Root@esapp.controller'
    //],
    //
    //stores: [
    //     'LogoImages'
    //    ,'LanguagesStore'
    //    ,'i18nStore'
    //    ,'ProductsActiveStore'
    //    ,'ProductsInactiveStore'
    //    ,'DataAcquisitionsStore'
    //    ,'IngestionsStore'
    //    ,'DataSetsStore'
    //    ,'ProcessingStore'
    //    ,'SystemSettingsStore'
    //    //,'ProductNavigatorStore'
    //],
    //
    //models: [
    //    'ProductNavigator',
    //    'ProductNavigatorMapSet',
    //    'ProductNavigatorMapSetDataSet',
    //    'TimeseriesProduct'
    //    //,'TimeserieProductMapSet'
    //    //,'TimeserieProductMapSetDataSet'
    //],

    //// create a reference in Ext.application so we can access it from multiple functions
    //splashscreen: {},
    init: function () {
        console.info('Root controller Init()');
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
        //        //Ext.getCmp("languageCombo").setValue(esapp.globals['selectedLanguage']);
        //
        //        Ext.data.StoreManager.lookup('i18nStore').load({
        //            params:{lang:esapp.globals['selectedLanguage']},
        //            callback: function(records, options, success){
        //                //Ext.create('esapp.view.main.Main');
        //            }
        //        });
        //    }
        //});

        this.callParent(arguments);
    }
});
