Ext.define('esapp.view.acquisition.product.editIngestSubProductController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-product-editingestsubproduct',

    setup: function() {
        var me = this.getView();
        var user = esapp.getUser();

        var subDatasourceDescriptionStore = me.getViewModel().get('subdatasourcedescriptions');

        subDatasourceDescriptionStore.setFilters([{
            property: 'pads_productcode'
            ,value: this.getView().params.ingestsubproductrecord.get('productcode')
            ,anyMatch: true
        },{
            property: 'pads_version'
            ,value: this.getView().params.ingestsubproductrecord.get('version')
            ,anyMatch: true
        }]);

        me.lookupReference('description').setValue(me.params.ingestsubproductrecord.get('description'));
        me.lookupReference('masked').setValue(!me.params.ingestsubproductrecord.get('masked'));
        me.lookupReference('defined_by_field').setValue(me.params.ingestsubproductrecord.get('defined_by'));

        if (me.params.edit){
            me.height = 825;
            Ext.getCmp('ingestsubproductdatasourcesfieldset').show();
            me.center();
        }
        else {
            if (esapp.Utils.objectExists(user) && user.userlevel == 1){
                Ext.getCmp('defined_by_field').setValue('JRC');
            }
            else {
                Ext.getCmp('defined_by_field').setValue('USER');
            }
        }
    }

    ,saveIngestSubProductInfo: function(widget, event){
        var me = this.getView();
        // var user = esapp.getUser();
        // var subDatasourcesDescrStore = me.getViewModel().get('subdatasourcedescriptions');

        var url = 'ingestsubproduct/create';
        if (me.params.edit){
            url = 'ingestsubproduct/update';
        }
        var params = {
            category_id: me.params.ingestsubproductrecord.get('category_id'),
            productcode: me.params.ingestsubproductrecord.get('productcode'),
            version: me.params.ingestsubproductrecord.get('version'),
            orig_subproductcode: me.params.ingestsubproductrecord.get('orig_subproductcode'),
            subproductcode: me.params.ingestsubproductrecord.get('subproductcode'),
            product_type: me.params.ingestsubproductrecord.get('product_type'),
            provider: me.params.ingestsubproductrecord.get('provider'),
            descriptive_name: me.params.ingestsubproductrecord.get('descriptive_name'),
            description: me.lookupReference('description').getValue().trim(),
            defined_by:  me.lookupReference('defined_by_field').getValue(),      //  me.params.ingestsubproductrecord.get('defined_by'),

            frequency_id: me.params.ingestsubproductrecord.get('frequency_id'),
            date_format: me.params.ingestsubproductrecord.get('date_format'),
            scale_factor: me.params.ingestsubproductrecord.get('scale_factor'),
            scale_offset: me.params.ingestsubproductrecord.get('scale_offset'),
            nodata: me.params.ingestsubproductrecord.get('nodata'),
            mask_min: me.params.ingestsubproductrecord.get('mask_min'),
            mask_max: me.params.ingestsubproductrecord.get('mask_max'),
            unit: me.params.ingestsubproductrecord.get('unit'),
            data_type_id: me.params.ingestsubproductrecord.get('data_type_id'),
            masked: !me.lookupReference('masked').getValue(),
            timeseries_role: me.lookupReference('enable_in_timeseries').getValue() ? 'Initial': null,
            enable_in_timeseries: me.params.ingestsubproductrecord.get('enable_in_timeseries'),
            display_index: me.params.ingestsubproductrecord.get('display_index')
        };

        // params = Ext.util.JSON.encode(params);

        Ext.Ajax.request({
            method: 'POST',
            url: url,
            params: params,
            success: function(response, opts){
                var result = Ext.JSON.decode(response.responseText);
                // console.info(result);
                if (result.success){
                    Ext.toast({ html: esapp.Utils.getTranslation('productinfoupdated'), title: esapp.Utils.getTranslation('productinfoupdated'), width: 200, align: 't' });

                    if (!me.params.edit){
                        me.params.edit = true;
                        me.height = 825;

                        Ext.getCmp('ingestsubproductdatasourcesfieldset').show();
                        me.center();

                        me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editingestsubproduct') + '</span>');
                        me.params.orig_subproductcode = me.params.ingestsubproductrecord.get('subproductcode');

                        // subDatasourcesDescrStore.setFilters({
                        //      property:'productid'
                        //     ,value:me.params.orig_productcode + '_' + me.params.orig_version
                        //     ,anyMatch:true
                        // });
                    }

                    Ext.data.StoreManager.lookup('IngestSubProductsStore').load();
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }

    ,addEditIngestParameters: function(grid, rowIndex, colIndex, colCmp){
        var me = this.getView();
        var subDatasourceDescriptionRecord = grid.getStore().getAt(rowIndex);
        // console.info(subDatasourceDescriptionRecord);
        var edit = false;
        var create = true;  // By default open Sub Datasource Description editor in create mode.
        if (subDatasourceDescriptionRecord.get('productcode') != '' ){  // open Sub Datasource Description editor in edit mode.
            edit = true;
            create = false;
        }
        else {
            subDatasourceDescriptionRecord.set('subproductcode', me.params.ingestsubproductrecord.get('subproductcode'));
            subDatasourceDescriptionRecord.set('datasource_descr_id', subDatasourceDescriptionRecord.get('pads_data_source_id'));
        }

        var editSubDatasourceDescriptionWin = new esapp.view.acquisition.product.editSubDatasourceDescription({
            params: {
                create: create,
                edit: edit,
                subdatasourcedescrrecord: subDatasourceDescriptionRecord
            }
        });
        editSubDatasourceDescriptionWin.show();
    }

    // ,deleteIngestParameters: function(){
    //
    // }
    //
    //
    // ,onSaveClick: function () {
    //     var me = this.getView(),
    //         form = me.lookupReference('ingestsubproductform');
    //
    //     if (form.isValid()) {
    //         // console.info(Ext.data.StoreManager.lookup('InternetSourceStore').getUpdatedRecords());
    //
    //         if (Ext.data.StoreManager.lookup('IngestSubProductsStore').getUpdatedRecords() !== []){
    //             Ext.data.StoreManager.lookup('IngestSubProductsStore').sync();
    //             //Ext.toast({html: esapp.Utils.getTranslation('saved'), title: esapp.Utils.getTranslation('saved'), width: 200, align: 't'});
    //         }
    //     }
    // }

});
