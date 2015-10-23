
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

    title: esapp.Utils.getTranslation('getrequestfile'),     // 'Send request',
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
    autoScroll:false,
    maximizable: false,
    width:500,
    height: 350,
    bodyStyle: 'padding:5px 5px 5px 5px',
    defaultAlign: 'b-c',

    border:true,
    frame:true,
    layout: 'fit',

    params: {
       level: null,
       record: null
    },

    listeners: {
        beforerender: 'getRequest'
    },

    initComponent: function () {
        var me = this;

        me.bbar = ['->', {
            text: esapp.Utils.getTranslation('cancel'),    // 'Cancel',
            scale: 'medium',
            handler: 'onCancelClick'
        },{
            text: esapp.Utils.getTranslation('saverequestfile'),    // 'Save Request file',
            iconCls: 'fa fa-floppy-o fa-2x',
            style: { color: 'lightblue' },
            scale: 'medium',
            disabled: false,
            handler: 'onSaveClick'
        }];

        me.items = [{
            xtype:'container',
            id: 'requestcontent',
            layout: 'fit',
            autoScroll:true,
            html:''
        }];

        me.callParent();

    }
});
