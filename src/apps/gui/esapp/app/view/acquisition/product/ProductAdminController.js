Ext.define('esapp.view.acquisition.product.ProductAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-product-productadmin',

    reloadProductsStore: function(grid){
        // var me = this.getView();
        // me.down('grid').getStore().load();
        Ext.data.StoreManager.lookup('ProductsStore').load();
    },

    editProduct: function(grid, rowIndex, colIndex, refElement, event){
        // var record = grid.getStore().getAt(rowIndex);    // for an to me unknown reason rowIndex is the index within the group category
        var record = event.record;
        var user = esapp.getUser();

        var edit = false;
        var view = true;
        if (!record.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)){
            edit = true;
            view = false;
        }

        // console.info(record);
        // console.info(grid.getStore());
        // console.info(grid);
        // console.info(rowIndex);
        // console.info(colIndex);
        // console.info(refElement);
        // console.info(event);

        var editProductWin = new esapp.view.acquisition.product.editProduct({
            params: {
                new: false,
                edit: edit,
                view: view,
                product: record,
                orig_productcode: record.get('productcode'),
                orig_version: record.get('version')
            }
        });
        editProductWin.show();
    },

    deleteProduct: function(grid, rowIndex, row){
        var record = grid.getStore().getAt(rowIndex);
        var messageText = esapp.Utils.getTranslation('delete_product-and-its-subproducts-question') + ': <BR>' +
                 '<b>'+ record.get('prod_descriptive_name')+'</b>';

        if (record.get('version') != ''){
           messageText += '<span class="smalltext"><b> - ' + record.get('version') + '</b></span>' ;
        }

        messageText += '<span class="smalltext">' + '<b style="color:darkgrey;"> - ' + record.get('productcode') + '</b></span>';

        // if (record.get('deletable')){
            Ext.Msg.show({
                title: esapp.Utils.getTranslation('deleteproductquestion'),     // 'Delete product definition?',
                message: messageText,
                buttons: Ext.Msg.OKCANCEL,
                icon: Ext.Msg.QUESTION,
                fn: function(btn) {
                    if (btn === 'ok') {
                        grid.getStore().remove(record);
                    }
                }
            });
        // }
    }
});
