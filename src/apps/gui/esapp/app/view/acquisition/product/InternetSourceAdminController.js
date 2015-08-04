Ext.define('esapp.view.acquisition.product.InternetSourceAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-product-internetsourceadmin',

    requires: [
        'Ext.window.Window',
        'esapp.view.acquisition.product.editInternetSource'
    ],

    onAssignInternetSourceClick: function(button) {
        var me = this.getView();
        var internetSourceGrid = this.lookupReference('internetSourceGrid'),
            selection = internetSourceGrid.getSelectionModel().getSelection()[0];

        var params = {
            productcode: me.params.product.productcode,
            subproductcode: me.params.product.subproductcode,
            version: me.params.product.version,
            data_source_id: selection.get('internet_id')
        }

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

    createDialog: function(record) {
        var view = this.getView();

        this.isEdit = !!record;
        this.dialog = view.add({
            xtype: 'editinternetsource',
            viewModel: {
                data: {
                    title: record ? 'Edit: ' + record.get('descriptive_name') : 'Add Internet Source'
                },
                // If we are passed a record, a copy of it will be created in the newly spawned session.
                // Otherwise, create a new phantom customer in the child.
                links: {
                    theInternetSource: record || {
                        //type: 'InternetSource',
                        reference: 'esapp.model.InternetSource',
                        create: true
                    }
                }
            }
            // Creates a child session that will spawn from the current session of this view.
            ,session: true
        });

        this.dialog.show();
    },

    onAddInternetSourceClick: function() {
        this.createDialog(null);
    },

    onEditInternetSourceClick: function (grid, record, colIndex) {
        var rec;
        if (!isNaN(record)) // record is rowIndex (from actioncolumn icon click)
            rec = grid.getStore().getAt(record);
        else rec = record;  // record is the row from itemdblclick event

        //console.info(rec);
        this.createDialog(rec);
        //this.createDialog(button.getWidgetRecord());
    },

    onRemoveInternetSourceClick: function(button) {
        var internetSourceGrid = this.lookupReference('internetSourceGrid'),
            selection = internetSourceGrid.getSelectionModel().getSelection()[0];

        selection.drop();
        //this.getStore('internetsources').remove(selection);
        //console.info(this.getSession().getChanges());

    },

    onSaveClick: function () {
        // Save the changes pending in the dialog's child session back to the parent session.
        var dialog = this.dialog,
            form = this.lookupReference('internetsourceform'),
            isEdit = this.isEdit;

        if (form.isValid()) {

            if (dialog.getSession().getChanges() != null) {
                dialog.getSession().getSaveBatch().start();
                Ext.toast({html: 'Saved!', title: 'Saved', width: 200, align: 't'});
                this.onCancelClick();
            }

            //if (!isEdit) {
            //    // Since we're not editing, we have a newly inserted record. Grab the id of
            //    // that record that exists in the child session
            //    id = dialog.getViewModel().get('theInternetSource').internet_id;
            //}
            ////dialog.getSession().save();
            ////this.getSession().save();
            //if (!isEdit) {
            //    //console.info(dialog.getViewModel().get('theInternetSource'));
            //    // Use the id of that child record to find the phantom in the parent session,
            //    // we can then use it to insert the record into our store
            //    //this.getStore('internetsources').add(this.getSession().getRecord('InternetSource', id));
            //    //this.getStore('internetsources').add(dialog.getViewModel().get('theInternetSource'));
            //    //this.getStore('internetsources').insert(0, dialog.getViewModel().get('theInternetSource'));
            //    //this.getStore('internetsources').insert(0, form.getValues());
            //    //this.getStore('internetsources').sync();
            //    //dialog.fireEvent('create', dialog, form.getValues());
            //}
            //console.info(this.getStore('internetsources'));
            //this.onCancelClick();
        }
    },

    onCancelClick: function () {
        this.dialog = Ext.destroy(this.dialog);
    }
});
