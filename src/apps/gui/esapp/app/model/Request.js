
Ext.define('esapp.model.Request', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'requestid', mapping: 'requestid'},
        {name: 'level', mapping: 'level'},
        {name: 'prod_descriptive_name', mapping: 'prod_descriptive_name'},
        {name: 'productcode', mapping: 'productcode'},
        {name: 'version', mapping: 'version'},
        {name: 'subproductcode', mapping: 'subproductcode'},
        {name: 'mapsetcode', mapping: 'mapsetcode'},
        {name: 'status', mapping: 'status'},
        {name: 'totfiles', mapping: 'totfiles'},
        {name: 'downloadedfiles', mapping: 'downloadedfiles'},
        {name: 'message', mapping: 'message'}
    ]
});