Ext.define('esapp.view.processing.ProcessingController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.processing-processing',

    checkStatusServices: function(splitbtn, ev){
        var me = this;
        // AJAX call to check the status of all 3 services
        Ext.Ajax.request({
            method: 'POST',
            url: 'services/checkstatusall',
            success: function(response, opts){
                var services = Ext.JSON.decode(response.responseText);
                if (services.processing){
                    me.getView().down('button[name=processingbtn]').setStyle('color','green');
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=runprocessing]').setDisabled(true);
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=stopprocessing]').setDisabled(false);
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=restartprocessing]').setDisabled(false);
                } else {
                    me.getView().down('button[name=processingbtn]').setStyle('color','red');
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=runprocessing]').setDisabled(false);
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=stopprocessing]').setDisabled(true);
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=restartprocessing]').setDisabled(true);
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }
    
});
