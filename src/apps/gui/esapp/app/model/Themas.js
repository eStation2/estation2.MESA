Ext.define('esapp.model.Themas', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'thema_id'},
       {name: 'thema_description'}
    ]

    ,autoLoad: true

    ,proxy: {
        type : 'ajax',
        url : 'systemsettings/getthemas',
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'themas'
            ,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('THEMAS MODEL - REMOTE EXCEPTION - Reopen Thema selection window!');

                //Ext.Msg.show({
                //    title: 'THEMAS MODEL- REMOTE EXCEPTION',
                //    msg: operation.getError(),
                //    icon: Ext.Msg.ERROR,
                //    buttons: Ext.Msg.OK
                //});
            }
        }
    }

});