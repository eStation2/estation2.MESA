Ext.define('esapp.store.DefinedByStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.definedby',

    requires : [
        'esapp.model.DefinedByType'
    ],

    model: 'esapp.model.DefinedByType',

    storeId : 'DefinedByStore',

    data: [
        { defined_by: 'USER', defined_by_descr: 'USER'},
        { defined_by: 'JRC', defined_by_descr: 'JRC'},
        { defined_by: 'JRC-Test', defined_by_descr: 'JRC-Test'}
    ]
});