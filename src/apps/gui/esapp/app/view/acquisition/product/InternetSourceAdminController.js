Ext.define('esapp.view.acquisition.product.InternetSourceAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-product-internetsourceadmin',

    requires: [
        'Ext.window.Window',
        'esapp.view.acquisition.editInternetSource'
    ],

    onAssignInternetSourceClick: function(button) {
        var me = this.getView();
        var user = esapp.getUser();
        var internetSourceGrid = this.lookupReference('internetSourceGrid'),
            selection = internetSourceGrid.getSelectionModel().getSelection()[0];

        var params = {
            productcode: me.params.product.productcode,
            subproductcode: me.params.product.subproductcode,
            version: me.params.product.version,
            data_source_id: selection.get('internet_id'),
            defined_by: (esapp.Utils.objectExists(user) && user.userlevel == 1) ? 'JRC' : 'USER'
        };

        Ext.Ajax.request({
            method: 'POST',
            url: 'internetsource/assigntoproduct',
            params: params,
            success: function(response, opts){
                //var result = Ext.JSON.decode(response.responseText);
                Ext.data.StoreManager.lookup('DataAcquisitionsStore').reload();
                //console.info(Ext.data.StoreManager.lookup('DataAcquisitionsStore'));
                me.close();
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });

    },

    onAddInternetSourceClick: function() {
        // Create a new internet source record and pass it. With the bind the store will automaticaly saved (through CRUD) on the server!
        var internetsourcestore  = Ext.data.StoreManager.lookup('InternetSourceStore');
        var user = esapp.getUser();

        var newInternetSourceRecord = new esapp.model.InternetSource({
                'internet_id': 'new-internet-source',
                'orig_internet_id': '',
                'defined_by': (esapp.Utils.objectExists(user) && user.userlevel == 1) ? 'JRC' : 'USER',
                'descriptive_name': '',
                'description': '',
                'modified_by': '',
                'update_datetime': null,
                'url': '',
                'user_name': '',
                'password': '',
                'type': null,
                'include_files_expression': '',
                'files_filter_expression': '',
                'status': false,
                'pull_frequency': null,
                'frequency_id': null,
                'start_date': null,
                'end_date': null,
                'https_params': '',
                'datasource_descr_id': '',
                'format_type': null,
                'file_extension': '',
                'delimiter': '',
                'date_format': null,
                'date_position': null,
                'product_identifier': '',
                'prod_id_position': null,
                'prod_id_length': null,
                'area_type': null,
                'area_position': null,
                'area_length': null,
                'preproc_type': null,
                'product_release': null,
                'release_position': null,
                'release_length': null,
                'native_mapset': null
            });

            internetsourcestore.add(newInternetSourceRecord);
            // console.info(internetsourcestore);

            var editInternetDataSourceWin = new esapp.view.acquisition.editInternetSource({
                params: {
                    create: true,
                    edit: false,
                    view: false,
                    internetsourcerecord: newInternetSourceRecord,
                    data_source_id: 'new-internet-source'
                }
            });
            editInternetDataSourceWin.show();
    },

    // onEditInternetSourceClick: function (grid, record, colIndex) {
    //     var rec;
    //     if (!isNaN(record)) // record is rowIndex (from actioncolumn icon click)
    //         rec = grid.getStore().getAt(record);
    //     else rec = record;  // record is the row from itemdblclick event
    //
    //     //console.info(rec);
    //     this.createDialog(rec);
    //     //this.createDialog(button.getWidgetRecord());
    // },

    onEditInternetSourceClick: function(grid, rowIndex, colIndex){
        var record = grid.getStore().getAt(rowIndex);
        var data_source_id = record.get('internet_id');
        var user = esapp.getUser();
        // console.info(record);
        // console.info(data_source_id);

        var edit = false;
        var view = true;
        if (!record.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)){
            edit = true;
            view = false;
        }

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
    },

    onRemoveInternetSourceClick: function(grid, rowIndex, row) {
        var record = grid.getStore().getAt(rowIndex);

        var messageText = esapp.Utils.getTranslation('delete_internetsource-question') + ': <BR>' +
                 '<b>'+ record.get('internet_id')+'</b>';

        messageText += '<span class="smalltext">' +
                  '<b style="color:darkgrey;"> - '+record.get('descriptive_name')+'</b></span>';

        Ext.Msg.show({
            title: esapp.Utils.getTranslation('deleteinternetsourcequestion'),     // 'Delete Internet source definition?',
            message: messageText,
            buttons: Ext.Msg.OKCANCEL,
            icon: Ext.Msg.QUESTION,
            fn: function(btn) {
                if (btn === 'ok') {
                    grid.getStore().remove(record);
                    Ext.data.StoreManager.lookup('InternetSourceStore').sync();
                    // grid.getStore().sync(); // Chained store does not have sync() method!
                }
            }
        });

        // var internetSourceGrid = this.lookupReference('internetSourceGrid'),
        //     selection = internetSourceGrid.getSelectionModel().getSelection()[0];
        // selection.drop();
        //this.getStore('internetsources').remove(selection);
        //console.info(this.getSession().getChanges());

    },

    reloadStore: function(btn){
        // var me = this.getView();
        // console.info(btn.up().up().down('grid').getStore());
        // btn.up().up().down('grid').getStore().load();
        // me.down('grid').getStore().load();
        Ext.data.StoreManager.lookup('InternetSourceStore').load();
    }


    // createDialog: function(record) {
    //     var view = this.getView();
    //
    //     this.isEdit = !!record;
    //     this.dialog = view.add({
    //         xtype: 'editinternetsource',
    //         viewModel: {
    //             data: {
    //                 title: record ? esapp.Utils.getTranslation('edit') + ': ' + record.get('descriptive_name') : esapp.Utils.getTranslation('addinternetsource')  // 'Add Internet Source'
    //
    //             },
    //             // If we are passed a record, a copy of it will be created in the newly spawned session.
    //             // Otherwise, create a new phantom customer in the child.
    //             links: {
    //                 theInternetSource: record || {
    //                     //type: 'InternetSource',
    //                     reference: 'esapp.model.InternetSource',
    //                     create: true
    //                 }
    //             }
    //         }
    //         // Creates a child session that will spawn from the current session of this view.
    //         ,session: true
    //     });
    //
    //     this.dialog.show();
    // },

    // onSaveClick: function () {
    //     // Save the changes pending in the dialog's child session back to the parent session.
    //     var dialog = this.dialog,
    //         form = this.lookupReference('internetsourceform'),
    //         isEdit = this.isEdit;
    //
    //     if (form.isValid()) {
    //
    //         if (dialog.getSession().getChanges() != null) {
    //             dialog.getSession().getSaveBatch().start();
    //             Ext.toast({html: esapp.Utils.getTranslation('saved'), title: esapp.Utils.getTranslation('saved'), width: 200, align: 't'});
    //             this.onCancelClick();
    //         }
    //
    //         //if (!isEdit) {
    //         //    // Since we're not editing, we have a newly inserted record. Grab the id of
    //         //    // that record that exists in the child session
    //         //    id = dialog.getViewModel().get('theInternetSource').internet_id;
    //         //}
    //         ////dialog.getSession().save();
    //         ////this.getSession().save();
    //         //if (!isEdit) {
    //         //    //console.info(dialog.getViewModel().get('theInternetSource'));
    //         //    // Use the id of that child record to find the phantom in the parent session,
    //         //    // we can then use it to insert the record into our store
    //         //    //this.getStore('internetsources').add(this.getSession().getRecord('InternetSource', id));
    //         //    //this.getStore('internetsources').add(dialog.getViewModel().get('theInternetSource'));
    //         //    //this.getStore('internetsources').insert(0, dialog.getViewModel().get('theInternetSource'));
    //         //    //this.getStore('internetsources').insert(0, form.getValues());
    //         //    //this.getStore('internetsources').sync();
    //         //    //dialog.fireEvent('create', dialog, form.getValues());
    //         //}
    //         //console.info(this.getStore('internetsources'));
    //         //this.onCancelClick();
    //     }
    // },
    //
    // onCancelClick: function () {
    //     this.dialog = Ext.destroy(this.dialog);
    // }
});
