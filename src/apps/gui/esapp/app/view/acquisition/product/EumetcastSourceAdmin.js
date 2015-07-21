
Ext.define("esapp.view.acquisition.product.EumetcastSourceAdmin",{
    "extend": "Ext.window.Window",
    "controller": "acquisition-product-eumetcastsourceadmin",
    "viewModel": {
        "type": "acquisition-product-eumetcastsourceadmin"
    },

    requires: [
        'esapp.view.acquisition.product.EumetcastSourceAdminModel',
        'esapp.view.acquisition.product.EumetcastSourceAdminController',
        'esapp.view.acquisition.product.editEumetcastSource',

        'Ext.layout.container.Center',
        'Ext.grid.plugin.CellEditing',
        'Ext.grid.column.Action'
    ],

    title: '',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },
    modal: true,
    frame: true,
    width: 1200,
    height: 800,
    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    params: {},

    // Create a session for this view
    session: true,

    initComponent: function () {
        var me = this;

        if (me.params.assigntoproduct){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('assigneumetcastsource')
                + ': ' + me.params.product.productcode + ' ' + me.params.product.version + '</span>');

            me.bbar = ['->', {
                text: 'Assign',
                iconCls: 'fa fa-link fa-2x',
                style: {color: 'green'},
                scale: 'medium',
                disabled: false,
                handler: 'onAssignEumetcastSourceClick'
            //}, {
            //    text: 'Add',
            //    iconCls: 'fa fa-plus-circle fa-2x',
            //    style: {color: 'green'},
            //    scale: 'medium',
            //    disabled: false,
            //    handler: 'onAddEumetcastSourceClick'
            //}, {
            //    text: 'Delete',
            //    iconCls: 'fa fa-minus-circle fa-2x',
            //    style: {color: 'red'},
            //    scale: 'medium',
            //    disabled: true,
            //    handler: 'onRemoveEumetcastSourceClick',
            //    bind: {
            //        disabled: '{!eumetcastSourceGrid.selection}'
            //    }
            }];
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('eumetcastsources') + '</span>');
        }

        me.items = [{
            flex: 1,
            xtype: 'grid',
            reference: 'eumetcastSourceGrid',
            bind: '{eumetcastsources}',
            listeners: {
                itemdblclick: 'onEditEumetcastSourceClick'
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
                    tooltip: 'Edit Eumetcast Source'
                    , handler: 'onEditEumetcastSourceClick'
                }]
            }, {
                text: 'ID',
                dataIndex: 'eumetcast_id',
                flex: 1.5
            }, {
                text: 'Collection name',
                dataIndex: 'collection_name',
                flex: 2
            }, {
                text: 'Filter expression',
                flex: 2,
                dataIndex: 'filter_expression_jrc'
            }]
        }]


        me.callParent();
    }
});
