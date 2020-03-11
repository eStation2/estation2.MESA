Ext.define('esapp.store.DateFormatsStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.dateformats',

    requires : [
        'esapp.model.DateFormat'
    ],

    model: 'esapp.model.DateFormat',

    storeId : 'dateformats'

    ,autoLoad: true

    ,proxy: {
        type : 'ajax',
        url : 'dateformats',
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'dateformats'
            //,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('DATE FORMATS STORE - REMOTE EXCEPTION - Reopen window (edit datasource or edit product!');

                //Ext.Msg.show({
                //    title: 'DATE FORMATS STORE- REMOTE EXCEPTION',
                //    msg: operation.getError(),
                //    icon: Ext.Msg.ERROR,
                //    buttons: Ext.Msg.OK
                //});
            }
        }
    }
});
