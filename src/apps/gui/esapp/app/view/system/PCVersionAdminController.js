Ext.define('esapp.view.system.PCVersionAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.system-pcversionadmin'

    ,setupVersions: function() {
        var me = this.getView();

        this.getStore('versions').load({
            callback: function(records, options, success){
                records.forEach(function(record) {
                    var versionradio = {},
                        version = record.get('version'),
                        versionsradiogroup = Ext.getCmp('versionsradiogroup'),
                        fieldlabel = '           ',
                        checked = false;

                    if (version == me.params.currentversion){
                        fieldlabel = esapp.Utils.getTranslation('activeversion'),    // 'Active version';
                        checked = true;
                    }
                    versionradio = {
                            fieldLabel: fieldlabel,
                            boxLabel: '<b>'+version+'</b>',
                            name: 'version',
                            inputValue: version,
                            checked: checked
                        }
                    versionsradiogroup.add(versionradio);
                });
            }
        });
    }

    ,changeVersion: function() {
        var me = this,
            newversion = Ext.getCmp('versionsradiogroup').getValue();

        Ext.Ajax.request({
            method: 'GET',
            url: 'systemsettings/changeversion',
            params: {
                version: newversion.version
            },
            success: function(response, opts){
                // ToDo: reload window!
                // window.location = '?versionchanged=true';
                window.location.reload(true);
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }
});
