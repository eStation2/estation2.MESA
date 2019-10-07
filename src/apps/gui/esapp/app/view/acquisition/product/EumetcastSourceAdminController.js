Ext.define('esapp.view.acquisition.product.EumetcastSourceAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-product-eumetcastsourceadmin',

    requires: [
        'Ext.window.Window',
        'esapp.view.acquisition.editEumetcastSource'
    ],

    onAssignEumetcastSourceClick: function(button) {
        var me = this.getView();
        var user = esapp.getUser();
        var eumetcastSourceGrid = this.lookupReference('eumetcastSourceGrid'),
            selection = eumetcastSourceGrid.getSelectionModel().getSelection()[0];

        var params = {
            productcode: me.params.product.productcode,
            subproductcode: me.params.product.subproductcode,
            version: me.params.product.version,
            data_source_id: selection.get('eumetcast_id'),
            defined_by: (esapp.Utils.objectExists(user) && user.userlevel == 1) ? 'JRC' : 'USER'
        }

        Ext.Ajax.request({
            method: 'POST',
            url: 'eumetcastsource/assigntoproduct',
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

    onAddEumetcastSourceClick: function() {
        // Create a new eumetcast source record and pass it. With the bind the store will automaticaly saved (through CRUD) on the server!
        var eumetcastsourcestore  = Ext.data.StoreManager.lookup('EumetcastSourceStore');
        var user = esapp.getUser();

        var newEumetcastSourceRecord = new esapp.model.EumetcastSource({
                'eumetcast_id': 'new-eumetcast-source',
                'orig_eumetcast_id': '',
                'collection_name': '',
                'filter_expression_jrc': '',
                'description': '',
                'typical_file_name': '',
                'keywords_theme': '',
                'keywords_societal_benefit_area': '',
                'defined_by': (esapp.Utils.objectExists(user) && user.userlevel == 1) ? 'JRC' : 'USER',
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

            eumetcastsourcestore.add(newEumetcastSourceRecord);

            var editEumetcastDataSourceWin = new esapp.view.acquisition.editEumetcastSource({
                params: {
                    create: true,
                    edit: false,
                    view: false,
                    internetsourcerecord: newEumetcastSourceRecord,
                    data_source_id: 'new-eumetcast-source'
                }
            });
            editEumetcastDataSourceWin.show();
    },

    // onEditEumetcastSourceClick: function (grid, record, colIndex) {
    //     var rec;
    //     if (!isNaN(record)) // record is rowIndex (from actioncolumn icon click)
    //         rec = grid.getStore().getAt(record);
    //     else rec = record;  // record is the row from itemdblclick event
    //
    //     //console.info(rec);
    //     this.createDialog(rec);
    //     //this.createDialog(button.getWidgetRecord());
    // },

    onEditEumetcastSourceClick: function(grid, rowIndex, colIndex) {
        var record = grid.getStore().getAt(rowIndex);
        var data_source_id = record.get('eumetcast_id');
        var user = esapp.getUser();
        // console.info(record);
        // console.info(data_source_id);

        var edit = false;
        var view = true;
        if (!record.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)){
            edit = true;
            view = false;
        }

        var editEumetcastDataSourceWin = new esapp.view.acquisition.editEumetcastSource({
            params: {
                create: false,
                edit: edit,
                view: view,
                internetsourcerecord: record,
                data_source_id: data_source_id
            }
        });
        editEumetcastDataSourceWin.show();
    },

    onRemoveEumetcastSourceClick: function(grid, rowIndex, row) {
        var record = grid.getStore().getAt(rowIndex);

        var messageText = esapp.Utils.getTranslation('delete_eumetcastsource-question') + ': <BR>' +
                 '<b>'+ record.get('eumetcast_id')+'</b>';

        messageText += '<span class="smalltext">' +
                  '<b style="color:darkgrey;"> - '+record.get('collection_name')+'</b></span>';

        Ext.Msg.show({
            title: esapp.Utils.getTranslation('deleteeumetcastsourcequestion'),     // 'Delete Internet source definition?',
            message: messageText,
            buttons: Ext.Msg.OKCANCEL,
            icon: Ext.Msg.QUESTION,
            fn: function(btn) {
                if (btn === 'ok') {
                    grid.getStore().remove(record);
                    Ext.data.StoreManager.lookup('EumetcastSourceStore').sync();
                    // grid.getStore().sync(); // Chained store does not have sync() method!
                }
            }
        });

        // var eumetcastSourceGrid = this.lookupReference('eumetcastSourceGrid'),
        //     selection = eumetcastSourceGrid.getSelectionModel().getSelection()[0];
        // selection.drop();
        //this.getStore('eumetcastsources').remove(selection);
        //console.info(this.getSession().getChanges());

    },

    reloadStore: function(btn){
        // var me = this.getView();
        // console.info(btn.up().up().down('grid').getStore());
        // btn.up().up().down('grid').getStore().load();
        // me.down('grid').getStore().load();
        Ext.data.StoreManager.lookup('EumetcastSourceStore').load();
    }

    // onSaveClick: function () {
    //     // Save the changes pending in the dialog's child session back to the parent session.
    //     var dialog = this.dialog,
    //         form = this.lookupReference('eumetcastsourceform'),
    //         isEdit = this.isEdit;
    //
    //     if (form.isValid()) {
    //
    //         if (dialog.getSession().getChanges() != null) {
    //             dialog.getSession().getSaveBatch().start();
    //             Ext.toast({html: esapp.Utils.getTranslation('saved'), title: esapp.Utils.getTranslation('saved'), width: 200, align: 't'});
    //             this.onCancelClick();
    //         }
    //     }
    // }

    // createDialog: function(record) {
    //     var view = this.getView();
    //
    //     this.isEdit = !!record;
    //     this.dialog = view.add({
    //         xtype: 'editeumetcastsource',
    //         viewModel: {
    //             data: {
    //                 title: record ? esapp.Utils.getTranslation('edit') + ': ' + record.get('collection_name') : esapp.Utils.getTranslation('addeumetcastsource')  // 'Add Eumetcast Source'
    //             },
    //             // If we are passed a record, a copy of it will be created in the newly spawned session.
    //             // Otherwise, create a new phantom record in the child.
    //             links: {
    //                 theEumetcastSource: record || {
    //                     //type: 'EumetcastSource',
    //                     reference: 'esapp.model.EumetcastSource',
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
    //
    // onCancelClick: function () {
    //     this.dialog = Ext.destroy(this.dialog);
    // }
});
