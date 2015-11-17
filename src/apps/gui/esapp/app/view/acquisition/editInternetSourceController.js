Ext.define('esapp.view.acquisition.editInternetSourceController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-editinternetsource'

    ,onSaveClick: function () {
        // Save the changes pending in the dialog's child session back to the parent session.
        var dialog = this.getView(),
            form = this.lookupReference('internetsourceform');

        //console.info(this.getStore('internetsources'));
        //console.info(Ext.data.StoreManager.lookup('InternetSourceStore').getUpdatedRecords());
        if (form.isValid()) {

            if (Ext.data.StoreManager.lookup('InternetSourceStore').getUpdatedRecords() != []){
                Ext.data.StoreManager.lookup('InternetSourceStore').sync();
                //Ext.toast({html: esapp.Utils.getTranslation('saved'), title: esapp.Utils.getTranslation('saved'), width: 200, align: 't'});
                this.onCancelClick();
            }
            //if (dialog.getSession().getChanges() != null) {
            //    dialog.getSession().getSaveBatch().start();
            //    Ext.toast({html: esapp.Utils.getTranslation('saved'), title: esapp.Utils.getTranslation('saved'), width: 200, align: 't'});
            //    this.onCancelClick();
            //}
        }
    }

    ,onCancelClick: function () {
        Ext.destroy(this.getView());
    }
});
