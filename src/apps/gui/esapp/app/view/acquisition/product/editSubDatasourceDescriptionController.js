Ext.define('esapp.view.acquisition.product.editSubDatasourceDescriptionController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-product-editsubdatasourcedescription'

    ,saveSubDatasourceDescriptionInfo: function(widget, event){
        var me = this.getView();
        // var user = esapp.getUser();
        // var subDatasourcesDescrStore = me.getViewModel().get('subdatasourcedescriptions');

        var url = 'subdatasourcedescription/create';
        if (me.params.edit){
            url = 'subdatasourcedescription/update';
        }
        var params = {
            pads_productcode: me.params.subdatasourcedescrrecord.get('pads_productcode'),
            pads_version: me.params.subdatasourcedescrrecord.get('pads_version'),
            pads_data_source_id: me.params.subdatasourcedescrrecord.get('pads_data_source_id'),
            pads_type: me.params.subdatasourcedescrrecord.get('pads_type'),
            datasource_descriptivename: me.params.subdatasourcedescrrecord.get('datasource_descriptivename'),

            productcode: me.params.subdatasourcedescrrecord.get('pads_productcode'),
            version: me.params.subdatasourcedescrrecord.get('pads_version'),
            subproductcode: me.params.subdatasourcedescrrecord.get('subproductcode'),
            datasource_descr_id: me.params.subdatasourcedescrrecord.get('datasource_descr_id'),
            scale_factor: me.params.subdatasourcedescrrecord.get('scale_factor'),
            scale_offset: me.params.subdatasourcedescrrecord.get('scale_offset'),
            no_data: me.params.subdatasourcedescrrecord.get('no_data'),
            data_type_id: me.params.subdatasourcedescrrecord.get('data_type_id'),
            mask_min: me.params.subdatasourcedescrrecord.get('mask_min'),
            mask_max: me.params.subdatasourcedescrrecord.get('mask_max'),
            re_process: me.params.subdatasourcedescrrecord.get('re_process'),
            re_extract: me.params.subdatasourcedescrrecord.get('re_extract'),
            scale_type: me.params.subdatasourcedescrrecord.get('scale_type'),

            preproc_type: me.params.subdatasourcedescrrecord.get('preproc_type'),
            native_mapset: me.params.subdatasourcedescrrecord.get('native_mapset')
        };

        Ext.Ajax.request({
            method: 'POST',
            url: url,
            params: params,
            success: function(response, opts){
                var result = Ext.JSON.decode(response.responseText);
                // console.info(result);
                if (result.success){

                    if (!me.params.edit){
                        me.params.edit = true;
                        Ext.toast({ html: esapp.Utils.getTranslation('subdatasourcedescrcreated'), title: esapp.Utils.getTranslation('subdatasourcedescrcreated'), width: 200, align: 't' });

                        me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editsubdatasourcedescr') + '</span>');
                    }
                    else {
                        Ext.toast({ html: esapp.Utils.getTranslation('subdatasourcedescrupdated'), title: esapp.Utils.getTranslation('subdatasourcedescrupdated'), width: 200, align: 't' });
                    }

                    // Ext.data.StoreManager.lookup('IngestSubProductsStore').load();
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }

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
