Ext.define('esapp.view.system.PCLogLevelAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.system-pclogleveladmin'

    ,setupLogLevels: function() {
        var me = this.getView();

        this.getStore('loglevels').load({
            callback: function(records, options, success){
                records.forEach(function(record) {
                    var loglevelradio = {},
                        loglevel = record.get('loglevel'),
                        loglevelsradiogroup = Ext.getCmp('loglevelsradiogroup'),
                        fieldlabel = '           ',
                        checked = false;

                    if (loglevel == me.params.currentloglevel){
                        fieldlabel =  esapp.Utils.getTranslation('activeloglevel'); // 'Active log level';
                        checked = true;
                    }
                    loglevelradio = {
                            fieldLabel: fieldlabel,
                            boxLabel: '<b>'+loglevel+'</b>',
                            name: 'loglevel',
                            inputValue: loglevel,
                            checked: checked
                        }
                    loglevelsradiogroup.add(loglevelradio);
                });
            }
        });
    }

    ,changeLogLevel: function() {
        var me = this,
            newloglevel = Ext.getCmp('loglevelsradiogroup').getValue();

        Ext.Ajax.request({
            method: 'GET',
            url: 'systemsettings/changeloglevel',
            params: {
                loglevel: newloglevel.loglevel
            },
            success: function(response, opts){
                var result = Ext.JSON.decode(response.responseText);
                if (result.success){
                    Ext.toast({ html: esapp.Utils.getTranslation('systemloglevelsetto') + " " + newloglevel.loglevel,
                                title: esapp.Utils.getTranslation('loglevelchanged'),
                                width: 200, align: 't' });
                }
                var systemsettingsstore  = Ext.data.StoreManager.lookup('SystemSettingsStore');
                var systemsettingsrecord = systemsettingsstore.getModel().load(0, {
                    scope: me,
                    failure: function(record, operation) {
                        //console.info('failure');
                    },
                    success: function(record, operation) {
                        var systemsettingview = Ext.getCmp('systemsettingsview');

                        systemsettingview.loadRecord(systemsettingsrecord);
                        systemsettingview.updateRecord();
                        me.closeView();
                    }
                });
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }
});
