Ext.define('esapp.view.widgets.ServiceMenuButtonController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.widgets-servicemenubutton',

    execServiceTask: function(menuitem, ev){
        var me = this;

        // AJAX call to run/start a specified service (specified through the menuitem name).
        // Ext.Ajax.extraParams = {task: menuitem.name};
        Ext.Ajax.request({
            method: 'POST',
            url: 'services/execservicetask',
            // extraParams: {task: menuitem.name},
            params: {
                service: menuitem.service,
                task: menuitem.task
            },
            success: function(response, opts){
                var runresult = Ext.JSON.decode(response.responseText);
                if (runresult.success){
                    if (menuitem.task=='restart') {
                        var message = esapp.Utils.getTranslation(menuitem.service) + ' ' + esapp.Utils.getTranslation('restarted');
                        Ext.toast({
                            html: message,
                            title: message,
                            width: 200,
                            align: 't'
                        });
                    }
                    // menuitem.up().up().fireEvent('click', this);
                    menuitem.up().up().up().up().getController().checkStatusServices(menuitem.up().up());
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    },

    viewLogFile: function (menuitem) {
        var logViewWin = new esapp.view.acquisition.logviewer.LogView({
            params: {
                logtype: 'service',
                record: menuitem.service
            }
        });
        logViewWin.show();
    }

});
