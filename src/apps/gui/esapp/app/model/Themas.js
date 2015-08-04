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
                Ext.Msg.show({
                    title: 'THEMAS MODEL- REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }

});