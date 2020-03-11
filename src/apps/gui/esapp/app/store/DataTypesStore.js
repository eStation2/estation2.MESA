Ext.define('esapp.store.DataTypesStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.datatypes',

    requires : [
        'esapp.model.DataType'
    ],

    model: 'esapp.model.DataType',

    storeId : 'datatypes'

    ,autoLoad: true

    ,proxy: {
        type : 'ajax',
        url : 'datatypes',
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'datatypes'
            //,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('DATA TYPES STORE - REMOTE EXCEPTION - Reopen window (edit datasource or edit product!');

                //Ext.Msg.show({
                //    title: 'DATA TYPES STORE- REMOTE EXCEPTION',
                //    msg: operation.getError(),
                //    icon: Ext.Msg.ERROR,
                //    buttons: Ext.Msg.OK
                //});
            }
        }
    }
});
