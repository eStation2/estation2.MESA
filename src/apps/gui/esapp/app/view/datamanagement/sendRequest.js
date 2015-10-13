
Ext.define("esapp.view.datamanagement.sendRequest",{
    "extend": "Ext.window.Window",
    "controller": "datamanagement-sendrequest",
    "viewModel": {
        "type": "datamanagement-sendrequest"
    },
    xtype: "sendrequest",

    requires: [
        'esapp.view.datamanagement.sendRequestController',
        'esapp.view.datamanagement.sendRequestModel',

        'Ext.layout.container.Center',
        'Ext.XTemplate'
    ],

    title: esapp.Utils.getTranslation('sendrequest'),     // 'Send request',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },

    constrainHeader: true,
    //constrain: true,
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable: true,
    autoScroll:true,
    maximizable: false,
    width:300,
    height: 300,

    border:true,
    frame:true,
    layout: {
        type  : 'fit',
        padding: 5
    },

    params: {
       level: null,
       record: null
    },

    initComponent: function () {
        var me = this;

        me.bbar = ['->', {
            text: esapp.Utils.getTranslation('cancel'),    // 'Cancel',
            scale: 'medium',
            handler: 'onCancelClick'
        },{
            text: esapp.Utils.getTranslation('send'),    // 'Send',
            iconCls: 'fa fa-paper-plane-o fa-2x',
            style: { color: 'lightblue' },
            scale: 'medium',
            disabled: false,
            formBind: true,
            handler: 'onSendClick'
        }];

        me.items = [{
            html: "Send a request to receive an archive of all missing data for:<BR><BR>" +
            "List of product - mapsets - subproducts"
        }];

        me.callParent();

    }
});
