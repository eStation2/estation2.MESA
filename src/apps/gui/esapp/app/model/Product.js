Ext.define('esapp.model.Product', {
    extend : 'esapp.model.Base',

    idProperty : 'productid',

    fields: [
        {name: 'productid'},
        {name: 'productcode'},
        {name: 'subproductcode'},
        {name: 'version'},
        {name: 'defined_by'},
        {name: 'product_type'},
        {name: 'activated', type: 'boolean'},
        {name: 'prod_descriptive_name'},
        {name: 'description'},
        {name: 'provider'},
        {name: 'category_id'},
        {name: 'cat_descr_name'},
        {name: 'order_index'},
        {name: 'subprods_productcode'},
        {name: 'subprods_version'},
        {name: 'subproductcode'},
        {name: 'totsubprods'}
    ]
});