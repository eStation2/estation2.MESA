Ext.define('esapp.view.acquisition.product.editProductController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-product-editproduct',

    setup: function() {
        var me = this.getView();
        var user = esapp.getUser();

        var productDatasourcesStore = me.getViewModel().get('productdatasources');
        var ingestsubproductsStore = me.getViewModel().get('ingestsubproducts');

        if (me.params.edit){
            Ext.getCmp('category').setValue(me.params.product.get('category_id'));
            Ext.getCmp('productcode').setValue(me.params.product.get('productcode'));
            Ext.getCmp('version').setValue(me.params.product.get('version'));
            Ext.getCmp('provider').setValue(me.params.product.get('provider'));
            Ext.getCmp('product_name').setValue(me.params.product.get('prod_descriptive_name'));
            Ext.getCmp('productdescription').setValue(me.params.product.get('description'));
            Ext.getCmp('defined_by_field').setValue(me.params.product.get('defined_by'));
            Ext.getCmp('activate_product_field').setValue(me.params.product.get('activated'));

            productDatasourcesStore.setFilters({
                 property:'productid'
                ,value:me.params.product.get('productid')
                ,anyMatch: true
            });

            ingestsubproductsStore.setFilters({
                 property: 'productid'
                ,value: me.params.product.get('productid')
                ,anyMatch: true

            //     property: 'productcode'
            //     ,value: me.params.product.get('productcode')
            //     ,anyMatch: true
            // },{
            //     property: 'version'
            //     ,value: me.params.product.get('version')
            //     ,anyMatch: true
            });

            Ext.getCmp('datasourcesfieldset').show();
            Ext.getCmp('ingestionsfieldset').show();

            // console.info(ingestsubproductsStore);
            // console.info(me.params.product.get('productid'));
        }
        else {
            if (esapp.Utils.objectExists(user) && user.userlevel == 1){
                Ext.getCmp('defined_by_field').setValue('JRC');
            }
            else {
                Ext.getCmp('defined_by_field').setValue('USER');
            }

            productDatasourcesStore.setFilters({
                 property:'productid'
                ,value:' '
                //,anyMatch:true
            });

            ingestsubproductsStore.setFilters({
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

    unassignDataSource: function(grid, rowIndex, colIndex) {
        var me = this.getView(),
            rec = grid.getStore().getAt(rowIndex);
            // grid = me.lookupReference('productDataSourcesGrid'),
            // rec = grid.getSelectionModel().getSelection()[0];

        if (esapp.Utils.objectExists(rec)) {
            //rec.remove();

            var params = {
                productcode: rec.get('productcode'),
                subproductcode: rec.get('subproductcode'),
                version: rec.get('version'),
                data_source_id: rec.get('data_source_id')
            };

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
        var data_source_id = record.get('data_source_id');
        var user = esapp.getUser();

        // console.info(record.get('defined_by'));
        // console.info(record);
        // console.info(data_source_id);

        var edit = false;
        var view = true;
        if (!record.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)){
            edit = true;
            view = false;
        }

        if (record.get('type') == 'INTERNET') {
            // data_source_id = record.get('internet_id');
            var editInternetDataSourceWin = new esapp.view.acquisition.editInternetSource({
                params: {
                    create: false,
                    edit: edit,
                    view: view,
                    internetsourcerecord: record,
                    data_source_id: data_source_id
                }
            });
            editInternetDataSourceWin.show();
        }
        else {
            var editEumetcastDataSourceWin = new esapp.view.acquisition.editEumetcastSource({
                params: {
                    create: false,
                    edit: edit,
                    view: view,
                    eumetcastsourcerecord: record,
                    data_source_id: data_source_id
                }
            });
            editEumetcastDataSourceWin.show();
        }
    },

    saveProductInfo: function(widget, event){
        var me = this.getView();
        var productDatasourcesStore = me.getViewModel().get('productdatasources');
        var ingestsubproductsStore = me.getViewModel().get('ingestsubproducts');

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
            description: Ext.getCmp('productdescription').getValue().trim(),
            defined_by: Ext.getCmp('defined_by_field').getValue(),
            activated: Ext.getCmp('activate_product_field').getValue()
        };
        // params = Ext.util.JSON.encode(params);

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
                    me.height = 830;

                    Ext.getCmp('datasourcesfieldset').show();
                    Ext.getCmp('ingestionsfieldset').show();
                    me.center();

                    me.params.orig_productcode = Ext.getCmp('productcode').getValue();
                    me.params.orig_version = Ext.getCmp('version').getValue();
                    //
                    // var daStore = Ext.data.StoreManager.lookup('DataAcquisitionsStore');
                    // Ext.data.StoreManager.lookup('DataAcquisitionsStore').load();

                    productDatasourcesStore.setFilters({
                         property:'productid'
                        ,value:me.params.orig_productcode + '_' + me.params.orig_version
                        ,exactMatch:true
                    });

                    ingestsubproductsStore.setFilters({
                         property:'productid'
                        ,value:me.params.orig_productcode + '_' + me.params.orig_version
                        ,exactMatch:true
                    });

                    me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editproduct') + '</span>');
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    },

    addIngestSubProduct: function(grid){
        var me = this.getView();
        var ingestsubproductstore  = Ext.data.StoreManager.lookup('IngestSubProductsStore');
        var user = esapp.getUser();

        var newIngestSubProductRecord = new esapp.model.IngestSubProduct({
            'productid': 'new-ingest-subproduct',
            'productcode': Ext.getCmp('productcode').getValue(),    // me.params.product.get('productcode'),
            'orig_subproductcode': '',
            'subproductcode': '',
            'version':  Ext.getCmp('version').getValue(),   // me.params.product.get('version'),
            'defined_by': (esapp.Utils.objectExists(user) && user.userlevel == 1) ? 'JRC' : 'USER',
            'activated': false,
            'category_id': Ext.getCmp('category').getValue(),   // me.params.product.get('category_id'),
            'product_type': 'Ingest',
            'descriptive_name': '',
            'description': '',
            'provider': Ext.getCmp('provider').getValue(),  // me.params.product.get('provider'),
            'frequency_id': '',
            'date_format': '',
            'scale_factor': null,
            'scale_offset': null,
            'nodata': null,
            'mask_min': null,
            'mask_max': null,
            'unit': '',
            'data_type_id': '',
            'masked': true,
            'enable_in_timeseries': false,
            'timeseries_role': null,
            'display_index': null
        });

        ingestsubproductstore.add(newIngestSubProductRecord);

        var newIngestionWin = new esapp.view.acquisition.product.editIngestSubProduct({
            params: {
                create: true,
                edit: false,
                view: false,
                ingestsubproductrecord: newIngestSubProductRecord,
                productid: 'new-ingest-subproduct'
            }
        });
        newIngestionWin.show();
    },

    editIngestSubProduct: function(grid, rowIndex, row){
        var me = this.getView();
        var record = grid.getStore().getAt(rowIndex);
        var user = esapp.getUser();

        var edit = false;
        var view = true;
        if (!record.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)){
            edit = true;
            view = false;
        }

        var editIngestionWin = new esapp.view.acquisition.product.editIngestSubProduct({
            params: {
                create: false,
                edit: edit,
                view: view,
                ingestsubproductrecord: record,
                productid: me.params.orig_productcode + '_' + me.params.orig_version
            }
        });
        editIngestionWin.show();
    },

    deleteIngestSubProduct: function(grid, rowIndex, row){
        var record = grid.getStore().getAt(rowIndex);

        var messageText = esapp.Utils.getTranslation('deleteingestsubproductquestion2') + ': <BR>' +
                 '<b>'+ record.get('descriptive_name')+'</b>';

        messageText += '<span class="smalltext">' +
                  '<b style="color:darkgrey;"> - '+record.get('subproductcode')+'</b></span>';

        Ext.Msg.show({
            title: esapp.Utils.getTranslation('deleteingestsubproductquestion'),     // 'Delete Internet source definition?',
            message: messageText,
            buttons: Ext.Msg.OKCANCEL,
            icon: Ext.Msg.QUESTION,
            fn: function(btn) {
                if (btn === 'ok') {
                    var ingestsubproductStore = Ext.data.StoreManager.lookup('IngestSubProductsStore');
                    grid.getStore().remove(record);

                    ingestsubproductStore.sync({
                        success: function (proxy, operations) {
                            // pop success message
                            Ext.toast({ html: esapp.Utils.getTranslation('ingestsubproductdeleted'), title: esapp.Utils.getTranslation('ingestsubproductdeleted'), width: 200, align: 't' });
                        },
                        failure: function (proxy, operations) {
                            // console.info(proxy);
                            // console.info(operations);
                            Ext.Msg.show({
                               title: esapp.Utils.getTranslation('errordeleting_ingestsubproduct'),         // 'REMOTE EXCEPTION - Error deleting Ingest Sub Product',
                               msg: proxy.operations[0].getError().response.responseText,
                               icon: Ext.Msg.ERROR,
                               buttons: Ext.Msg.OK
                            });

                            // gridStore.add(gridStore.getRemovedRecords());
                            // resume records
                            ingestsubproductStore.rejectChanges();
                        }
                    });
                    // grid.getStore().sync(); // Chained store does not have sync() method!
                }
            }
        });
    }
});
