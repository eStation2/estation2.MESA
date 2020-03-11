Ext.define('esapp.view.system.ThemaAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.system-themaadmin'

    ,setupThemas: function() {
        var me = this.getView();

        this.getStore('themas').load({
            callback: function(records, options, success){
                records.forEach(function(record) {
                    var themaradio = {},
                        thema_id = record.get('thema_id'),
                        thema_description = record.get('thema_description'),
                        themasradiogroup = Ext.getCmp('themasradiogroup'),
                        fieldlabel = '           ',
                        checked = false;

                    if (thema_id == me.params.currentthema){
                        fieldlabel = esapp.Utils.getTranslation('activethema');    // 'Active thema';
                        checked = true;
                    }
                    themaradio = {
                            fieldLabel: fieldlabel,
                            boxLabel: '<b>'+thema_description+'</b>',
                            name: 'thema',
                            inputValue: thema_id,
                            checked: checked
                        }
                    themasradiogroup.add(themaradio);
                });
            }
        });
    }

    ,changeThema: function() {
        var me = this,
            newthema = Ext.getCmp('themasradiogroup').getValue();

        Ext.Ajax.request({
            method: 'GET',
            url: 'systemsettings/changethema',
            params: {
                thema: newthema.thema
            },
            success: function(response, opts){
                var result = Ext.JSON.decode(response.responseText);
                if (result.success){
                    if (esapp.globals['typeinstallation'] === 'windows'){
                        Ext.toast({ html: esapp.Utils.getTranslation('systemthemasetto') + " " + newthema.thema,
                                    title: esapp.Utils.getTranslation('themachanged'),
                                    width: 300, align: 't' });
                    }
                    else {
                        Ext.toast({ html: esapp.Utils.getTranslation('systemthemasetto') + " " + newthema.thema + "</BR>" + result.message,
                                    title: esapp.Utils.getTranslation('themachanged'),
                                    width: 300, align: 't' });
                    }
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

                        // IN WINDOWS VERSION THE THEMA MUST BE CHANGEABLE!
                        if (esapp.globals['typeinstallation'] === 'windows'){
                            Ext.getCmp('modify-thema-btn').show();
                        }
                        else {

                            if (record.data.thema != ''){
                                Ext.getCmp('modify-thema-btn').hide();
                            }
                            else {
                                Ext.getCmp('modify-thema-btn').show();
                            }
                        }
                        me.closeView();
                    }
                });
            },
            failure: function(response, opts) {
                console.info(response.status);
                Ext.toast({ html: result.error,
                            title: 'Error',
                            width: 300, align: 't' });
                }
        });
    }
    
});
