Ext.define('esapp.view.system.IPAddressAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.system-ipaddressadmin',

    links: {
        ip_settings: {
            reference: 'esapp.model.IPSetting',
            id: 0
            ,listeners: {
                update: function () {
                    //Ext.Msg.alert('Message', 'IP settings updated!');
                }
            }
        }
    }

});
