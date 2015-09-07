
Ext.define("esapp.view.acquisition.product.InternetSourceAdmin",{
    "extend": "Ext.window.Window",
    "controller": "acquisition-product-internetsourceadmin",
    "viewModel": {
        "type": "acquisition-product-internetsourceadmin"
    },

    requires: [
        'esapp.view.acquisition.product.InternetSourceAdminModel',
        'esapp.view.acquisition.product.InternetSourceAdminController',
        'esapp.view.acquisition.product.editInternetSource',

        'Ext.layout.container.Center',
        'Ext.grid.plugin.CellEditing',
        'Ext.grid.column.Action'
    ],

    title: '',
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

    width: 1000,
    height: Ext.getBody().getViewSize().height < 625 ? Ext.getBody().getViewSize().height-10 : 800,  // 600,
    maxHeight: 800,

    frame: true,
    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    params: {},

    // Create a session for this view
    session: true,

    initComponent: function () {
        var me = this;

        var assignButton = {
            text: esapp.Utils.getTranslation('assign'),  // 'Assign',
            iconCls: 'fa fa-link fa-2x',
            style: {color: 'green'},
            scale: 'medium',
            disabled: false,
            handler: 'onAssignInternetSourceClick'
        };
        var addButton = {
            text: esapp.Utils.getTranslation('add'),  // 'Add',
            iconCls: 'fa fa-plus-circle fa-2x',
            style: {color: 'green'},
            scale: 'medium',
            disabled: false,
            handler: 'onAddInternetSourceClick'
        };
        var deleteButton = {
            text: esapp.Utils.getTranslation('delete'),  // 'Delete',
            iconCls: 'fa fa-minus-circle fa-2x',
            style: {color: 'red'},
            scale: 'medium',
            disabled: true,
            handler: 'onRemoveInternetSourceClick',
            bind: {
                disabled: '{!internetSourceGrid.selection}'
            }
        };

        if (me.params.assigntoproduct){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('assigninternetsource')
                + ': ' + me.params.product.productcode + ' ' + me.params.product.version + '</span>');

            me.bbar = ['->', assignButton, addButton, deleteButton];
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('internetsources') + '</span>');

            me.bbar = ['->', addButton, deleteButton];
        }

        me.items = [{
            flex: 1,
            xtype: 'grid',
            reference: 'internetSourceGrid',
            bind: '{internetsources}',
            listeners: {
                itemdblclick: 'onEditInternetSourceClick'
            },
            selModel: {
                allowDeselect: true
            },
            columns: [{
                xtype: 'actioncolumn',
                width: 30,
                //flex: 0.5,
                align: 'center',
                shrinkWrap: 0,
                items: [{
                    icon: 'resources/img/icons/edit.png',
                    tooltip: esapp.Utils.getTranslation('editinternetsource') // 'Edit Internet Source'
                    , handler: 'onEditInternetSourceClick'
                }]
            }, {
                dataIndex: 'internet_id',
                flex: 1.5,
                text: esapp.Utils.getTranslation('id') // 'ID'
            }, {
                dataIndex: 'descriptive_name',
                flex: 2,
                text: esapp.Utils.getTranslation('name') // 'Name'
            }, {
                dataIndex: 'url',
                flex: 2,
                text: esapp.Utils.getTranslation('url') // 'URL'
            }, {
                dataIndex: 'update_datetime',
                flex: 1,
                text: esapp.Utils.getTranslation('lastupdated') // 'Last updated'
            }, {
                dataIndex: 'type',
                flex: 0.5,
                text: esapp.Utils.getTranslation('type') // 'Type'
            }, {
                dataIndex: 'status',
                flex: 0.5,
                text: esapp.Utils.getTranslation('status') // 'Status'
            }]
        }]


        me.callParent();
    }
});
