Ext.define('esapp.view.help.helpModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.help-help',
    stores: {
        documentation: {
            fields: ['name', 'thumb', 'url', 'type'],

            proxy: {
                type: 'ajax',
                url: 'resources/data/docs_data_'+esapp.globals['selectedLanguage']+'.json',

                reader: {
                    type: 'json'
                }
            },

            autoLoad: true
        },
        weblinks: {
            fields: ['name', 'thumb', 'url', 'type'],

            proxy: {
                type: 'ajax',
                url: 'resources/data/links_data_'+esapp.globals['selectedLanguage']+'.json',

                reader: {
                    type: 'json'
                }
            },

            autoLoad: true
        }
    }

});
