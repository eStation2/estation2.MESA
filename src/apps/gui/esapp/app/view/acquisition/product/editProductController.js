Ext.define('esapp.view.acquisition.product.editProductController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-product-editproduct',

    setup: function() {
        var me = this.getView();

        var productDatasourcesStore = me.getViewModel().get('productdatasources');
        var productIngestionsStore = me.getViewModel().get('productingestions');
        if (me.params.product){
            Ext.getCmp('category').setValue(me.params.product.get('category_id'));
            Ext.getCmp('productcode').setValue(me.params.product.get('productcode'));
            Ext.getCmp('version').setValue(me.params.product.get('version'));
            Ext.getCmp('provider').setValue(me.params.product.get('provider'));
            Ext.getCmp('product_name').setValue(me.params.product.get('prod_descriptive_name'));
            Ext.getCmp('productdescription').setValue(me.params.product.get('description'));

            productDatasourcesStore.setFilters({
                 property:'productid'
                ,value:me.params.product.get('productid')
                ,anyMatch:true
            });

            productIngestionsStore.setFilters({
                 property:'productid'
                ,value:me.params.product.get('productid')
                ,anyMatch:true
            });

            Ext.getCmp('datasourcesfieldset').show();
            Ext.getCmp('ingestionsfieldset').show();
        }
        else {
            productDatasourcesStore.setFilters({
                 property:'productid'
                ,value:' '
                //,anyMatch:true
            });

            productIngestionsStore.setFilters({
                 property:'productid'
                ,value:' '
                //,anyMatch:true
            });
        }
    },

    addDataSource: function(widget, event) {
        var me = this.getView();

        var selectdatasourcetypeWin = Ext.create('Ext.window.Window', {
            title: esapp.Utils.getTranslation('datasourcetype'),   // 'Data Source Type',
            id: 'selectdatasourcetypeWin',
            titleAlign: 'center',
            modal: true,
            closable: true,
            closeAction: 'destroy', // 'hide',
            border:true,
            frame:true,
            width:165,
            autoScroll:false,
            bodyPadding:'10 5 0 5',
            viewConfig:{forceFit:true},
            bbar: ['->',{
                xtype: 'button',
                id: 'selectdatasourcebtn',
                text: esapp.Utils.getTranslation('choose'),   // 'Choose',
                iconCls: 'fa fa-thumbs-o-up fa-2x',
                style: { color: 'green' },
                scale: 'medium',
                scope:me,
                handler: function(){
                    var eumetcastradio = Ext.getCmp('eumetcastradio'),
                        internetradio = Ext.getCmp('internetradio');

                    if (eumetcastradio.getValue()) {
                        // open EUMETCAST datasource administration window
                        var EumetcastSourceAdminWin = new esapp.view.acquisition.product.EumetcastSourceAdmin({
                            params: {
                                assigntoproduct: true,
                                product: {
                                    productcode: me.params.orig_productcode,
                                    subproductcode: me.params.orig_productcode+'_native',
                                    version: me.params.orig_version
                                }
                            }
                        });

                        EumetcastSourceAdminWin.show();
                        selectdatasourcetypeWin.close();
                    }
                    else if (internetradio.getValue()) {
                        // open INTERNET datasource administration window
                        var InternetSourceAdminWin = new esapp.view.acquisition.product.InternetSourceAdmin({
                            params: {
                                assigntoproduct: true,
                                product: {
                                    productcode: me.params.orig_productcode,
                                    subproductcode: me.params.orig_productcode+'_native',
                                    version: me.params.orig_version
                                }
                            }
                        });

                        InternetSourceAdminWin.show();
                        selectdatasourcetypeWin.close();
                    }
                }
            }],
            items:[{
                xtype: 'fieldset',
                reference:'choosedatasourcetype',
                width: 145,
                hidden:false,
                defaultType: 'radio',
                //padding: 5,
                layout: 'anchor',
                defaults: {
                    anchor: '100%',
                    labelWidth: 100
                },

                items: [{
                    xtype: 'radiogroup',
                    id: 'datasourceradiogroup',
                    columns: 1,
                    vertical: true,
                    items: [{
                        boxLabel: '<b>EUMETCAST</b>',
                        id: 'eumetcastradio',
                        name: 'datasourcetype',
                        inputValue: 'eumetcast',
                        checked: true
                    }, {
                        boxLabel: '<b>INTERNET</b>',
                        id: 'internetradio',
                        name: 'datasourcetype',
                        inputValue: 'internet',
                        checked: false
                    }]
                }]
            }]
        });
        selectdatasourcetypeWin.show();
        //me.lookupReference('choosedatasourcetype').show();
    },

    deleteDataSource: function(widget, event) {
        var me = this.getView(),
            grid = me.lookupReference('productDataSourcesGrid'),
            rec = grid.getSelectionModel().getSelection()[0];

        if (rec) {
            //rec.remove();

            var params = {
                productcode: rec.get('productcode'),
                subproductcode: rec.get('subproductcode'),
                version: rec.get('version'),
                data_source_id: rec.get('data_source_id')
            }

            Ext.Ajax.request({
                method: 'POST',
                url: 'product/unassigndatasource',
                params: params,
                success: function(response, opts){
                    var result = Ext.JSON.decode(response.responseText);
                    if (result.success){
                        Ext.toast({ html: esapp.Utils.getTranslation('productdatasourceunassigned'), title: esapp.Utils.getTranslation('productdatasourceunassigned'), width: 200, align: 't' });
                    }

                    Ext.data.StoreManager.lookup('DataAcquisitionsStore').load();

                },
                failure: function(response, opts) {
                    console.info(response.status);
                }
            });
        }
    },

    editDataSource: function(grid, rowIndex, colIndex){
        var record = grid.getStore().getAt(rowIndex);

        if (record.get('type') == 'INTERNET') {
            var editInternetDataSourceWin = new esapp.view.acquisition.product.editInternetSource({
                params: {
                    edit: true,
                    product: record,
                    orig_productcode: record.get('productcode'),
                    orig_version: record.get('version')
                }
            });
            editInternetDataSourceWin.show();
        }
        else {

        }
    },

    saveProductInfo: function(widget, event){
        var me = this.getView();

        var url = 'product/createproduct';
            //orig_productcode = '',
            //orig_version = '';
        if (me.params.edit){
            url = 'product/updateproductinfo';
            //orig_productcode = me.params.product.get('productcode');
            //orig_version = me.params.product.get('version');
        }
        var params = {
            category_id: Ext.getCmp('category').getValue(),
            orig_productcode: me.params.orig_productcode,
            orig_version: me.params.orig_version,
            productcode: Ext.getCmp('productcode').getValue(),
            version: Ext.getCmp('version').getValue(),
            provider: Ext.getCmp('provider').getValue(),
            prod_descriptive_name: Ext.getCmp('product_name').getValue(),
            description: Ext.getCmp('productdescription').getValue()
        }

        Ext.Ajax.request({
            method: 'POST',
            url: url,
            params: params,
            success: function(response, opts){
                var result = Ext.JSON.decode(response.responseText);
                if (result.success){
                    Ext.toast({ html: esapp.Utils.getTranslation('productinfoupdated'), title: esapp.Utils.getTranslation('productinfoupdated'), width: 200, align: 't' });
                }
                if (!me.params.edit){
                    me.params.edit = true;
                    Ext.getCmp('datasourcesfieldset').show();
                }
                me.params.orig_productcode = Ext.getCmp('productcode').getValue();
                me.params.orig_version = Ext.getCmp('version').getValue();

                Ext.data.StoreManager.lookup('ProductsInactiveStore').load();
                Ext.data.StoreManager.lookup('DataAcquisitionsStore').load();

                var daStore = me.getViewModel().get('productdatasources');

                daStore.setFilters({
                     property:'productid'
                    ,value:me.params.orig_productcode + '_' + me.params.orig_version
                    ,anyMatch:true
                });

            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }

});
