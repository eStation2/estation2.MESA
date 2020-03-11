Ext.define('esapp.view.acquisition.product.selectProductController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-product-selectproduct',

    loadInactiveProductsGrid: function(grid){
        var me = this.getView();
        me.down('grid').getStore().load();
    },

    editProduct: function(grid, rowIndex, colIndex){
        var record = grid.getStore().getAt(rowIndex);
        // if (record.get('defined_by') != 'JRC') {
            var editProductWin = new esapp.view.acquisition.product.editProduct({
                params: {
                    edit: true,
                    product: record,
                    orig_productcode: record.get('productcode'),
                    orig_version: record.get('version')
                }
            });
            editProductWin.show();
        // }
    }
});
