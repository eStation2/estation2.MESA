Ext.define('esapp.view.acquisition.editEumetcastSourceController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-editeumetcastsource'

    ,onSaveClick: function () {
        // Save the changes pending in the dialog's child session back to the parent session.
        var me = this.getView(),
            form = this.lookupReference('eumetcastsourceform');

        if (form.isValid()) {

            if (Ext.data.StoreManager.lookup('EumetcastSourceStore').getUpdatedRecords() !== []){
                Ext.data.StoreManager.lookup('EumetcastSourceStore').sync();
                //Ext.toast({html: esapp.Utils.getTranslation('saved'), title: esapp.Utils.getTranslation('saved'), width: 200, align: 't'});

            }
            //if (dialog.getSession().getChanges() != null) {
            //    dialog.getSession().getSaveBatch().start();
            //    Ext.toast({html: esapp.Utils.getTranslation('saved'), title: esapp.Utils.getTranslation('saved'), width: 200, align: 't'});
            //    this.onCancelClick();
            //}
        }
    }


    // ,onCancelClick: function () {
    //     Ext.data.StoreManager.lookup('EumetcastSourceStore').rejectChanges();
    //     Ext.destroy(this.getView());
    // }

    //,getEumetcastSource: function(win) {
    //    var me = this.getView();
    //    if (me.data_source_id != null){
    //        //console.info(me.data_source_id);
    //    }
        //console.info(this.getStore('eumetcastsources'));
        //console.info(this.getStore('theEumetcastSource'));
        //this.getStore('theEumetcastSource').setFilters({
        //    property: 'eumetcast_id'
        //    ,value: me.data_source_id
        //    ,anyMatch: false
        //});
        //var eumetcaststore  = Ext.data.StoreManager.lookup('EumetcastSourceStore');
        //var eumetcastrecordid = eumetcaststore.find('eumetcast_id', me.data_source_id, 0, true, false, true);
        //var eumetcastrecord = eumetcaststore.getModel().load(eumetcastrecordid, {
        //    scope: me,
        //    failure: function(record, operation) {
        //        //console.info('failure');
        //    },
        //    success: function(record, operation) {
        //
        //    }
        //});
        //
        //this.getStore('eumetcastsources').load();
        //
        //console.info(this.getStore('eumetcastsources').findRecord('eumetcast_id', me.data_source_id, 0, true, false, false));
        //
        //console.info(this.getViewModel());
        //
        //var record = this.getStore('eumetcastsources').findRecord('eumetcast_id', me.data_source_id, 0, true, false, true);
        //var newstore = Ext.create('Ext.data.JsonStore', {
        //    name: 'theEumetcastSource',
        //    model: 'esapp.model.EumetcastSource',
        //    data: record.getData()
        //});
        //this.getViewModel().addStore(newstore);
        //
        //
        ////this.getViewModel().linkData = {theEumetcastSource: record };
        //this.getViewModel().setLinks( {theEumetcastSource: record.getData() } );
    //}
});
