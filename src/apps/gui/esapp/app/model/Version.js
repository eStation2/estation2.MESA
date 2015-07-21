Ext.define('esapp.model.Version', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'version'}
    ]

    ,autoLoad: true

    ,proxy: {
        type : 'ajax',
        url : 'systemsettings/getversions',
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'versions'
            //,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                Ext.MessageBox.show({
                    title: 'VERSIONS MODEL- REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.MessageBox.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }
});
