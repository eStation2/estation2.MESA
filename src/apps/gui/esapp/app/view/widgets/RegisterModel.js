Ext.define('esapp.view.widgets.RegisterModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.widgets-register',
    stores: {
        users:{
            fields: [
                {name: 'username'},
                {name: 'userid'},
                {name: 'email'},
                {name: 'userlevel'}
            ],
            sorters: {property: 'username', direction: 'ASC'}

            ,autoLoad: true

            ,proxy: {
                type : 'ajax',
                actionMethods: { create: 'POST', read: 'POST', update: 'POST', destroy: 'POST' },
                url : 'users',
                extraParams:{
                    lang: 'eng'     // esapp.globals['selectedLanguage']
                },
                reader: {
                     type: 'json'
                    ,successProperty: 'success'
                    ,rootProperty: 'users'
                    ,messageProperty: 'message'
                },
                listeners: {
                    exception: function(proxy, response, operation){
                        // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)
                        console.info('USER STORE - REMOTE EXCEPTION - Reload browser window!');

                    }
                }
            }

        }
        // chained store for grid
        //,users:{
        //    source:'{serverlayerfiles}'
        //}
    }

});
