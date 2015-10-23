Ext.define('esapp.model.Base', {
    extend: 'Ext.data.Model',
    identifier: 'negative',

    requires:[
        'Ext.data.identifier.Negative'
    ],
    schema: {
        namespace: 'esapp.model'
    }
});