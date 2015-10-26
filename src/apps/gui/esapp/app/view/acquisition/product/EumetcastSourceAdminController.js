Ext.define('esapp.view.acquisition.product.EumetcastSourceAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-product-eumetcastsourceadmin',

    requires: [
        'Ext.window.Window',
        'esapp.view.acquisition.product.editEumetcastSource'
    ],

    onAssignEumetcastSourceClick: function(button) {
        var me = this.getView();
        var eumetcastSourceGrid = this.lookupReference('eumetcastSourceGrid'),
            selection = eumetcastSourceGrid.getSelectionModel().getSelection()[0];

        var params = {
            productcode: me.params.product.productcode,
            subproductcode: me.params.product.subproductcode,
            version: me.params.product.version,
            data_source_id: selection.get('eumetcast_id')
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

    createDialog: function(record) {
        var view = this.getView();

        this.isEdit = !!record;
        this.dialog = view.add({
            xtype: 'editeumetcastsource',
            viewModel: {
                data: {
                    title: record ? esapp.Utils.getTranslation('edit') + ': ' + record.get('collection_name') : esapp.Utils.getTranslation('addeumetcastsource')  // 'Add Eumetcast Source'
                },
                // If we are passed a record, a copy of it will be created in the newly spawned session.
                // Otherwise, create a new phantom customer in the child.
                links: {
                    theEumetcastSource: record || {
                        //type: 'EumetcastSource',
                        reference: 'esapp.model.EumetcastSource',
                        create: true
                    }
                }
            }
            // Creates a child session that will spawn from the current session of this view.
            ,session: true
        });

        this.dialog.show();
    },

    onAddEumetcastSourceClick: function() {
        this.createDialog(null);
    },

    onEditEumetcastSourceClick: function (grid, record, colIndex) {
        var rec;
        if (!isNaN(record)) // record is rowIndex (from actioncolumn icon click)
            rec = grid.getStore().getAt(record);
        else rec = record;  // record is the row from itemdblclick event

        //console.info(rec);
        this.createDialog(rec);
        //this.createDialog(button.getWidgetRecord());
    },

    onRemoveEumetcastSourceClick: function(button) {
        var eumetcastSourceGrid = this.lookupReference('eumetcastSourceGrid'),
            selection = eumetcastSourceGrid.getSelectionModel().getSelection()[0];

        selection.drop();
        //this.getStore('eumetcastsources').remove(selection);
        //console.info(this.getSession().getChanges());

    },

    onSaveClick: function () {
        // Save the changes pending in the dialog's child session back to the parent session.
        var dialog = this.dialog,
            form = this.lookupReference('eumetcastsourceform'),
            isEdit = this.isEdit;

        if (form.isValid()) {

            if (dialog.getSession().getChanges() != null) {
                dialog.getSession().getSaveBatch().start();
                Ext.toast({html: esapp.Utils.getTranslation('saved'), title: esapp.Utils.getTranslation('saved'), width: 200, align: 't'});
                this.onCancelClick();
            }
        }
    },

    onCancelClick: function () {
        this.dialog = Ext.destroy(this.dialog);
    }
});
