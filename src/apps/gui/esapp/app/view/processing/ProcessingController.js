Ext.define('esapp.view.processing.ProcessingController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.processing-processing',

    checkStatusServices: function(splitbtn, ev){
        // AJAX call to check the status of all 3 services
        Ext.Ajax.request({
            method: 'POST',
            url: 'services/checkstatusall',
            success: function(response, opts){
                var services = Ext.JSON.decode(response.responseText);
                if (services.processing){
                    splitbtn.up().down('button[name=processingbtn]').setStyle('color','green');
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=runprocessing]').setDisabled(true);
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=stopprocessing]').setDisabled(false);
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=restartprocessing]').setDisabled(false);
                } else {
                    splitbtn.up().down('button[name=processingbtn]').setStyle('color','red');
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=runprocessing]').setDisabled(false);
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=stopprocessing]').setDisabled(true);
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=restartprocessing]').setDisabled(true);
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }
    
});
