Ext.define('esapp.view.help.helpModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.help-help',
    stores: {
        documentation: {
            fields: ['name', 'thumb', 'url', 'type'],

            proxy: {
                type: 'ajax',
                //url: 'resources/data/docs_data_'+esapp.globals['selectedLanguage']+'.json',
                url: 'help',
                extraParams: {
                    type: 'docs',
                    lang : esapp.globals['selectedLanguage']
                },
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
                //url: 'resources/data/links_data_'+esapp.globals['selectedLanguage']+'.json',
                url: 'help',
                extraParams: {
                    type: 'links',
                    lang: esapp.globals['selectedLanguage']
                },
                reader: {
                    type: 'json'
                }
            },

            autoLoad: true
        },
        notes: {
            fields: ['name', 'thumb', 'url', 'type'],

            proxy: {
                type: 'ajax',
                url: 'help',
                extraParams: {
                    type: 'notes',
                    lang: esapp.globals['selectedLanguage']
                },
                reader: {
                    type: 'json'
                }
            },

            autoLoad: true
        }
    }

});
