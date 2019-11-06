
Ext.define("esapp.view.acquisition.product.InternetSourceAdmin",{
    "extend": "Ext.window.Window",
    "controller": "acquisition-product-internetsourceadmin",
    "viewModel": {
        "type": "acquisition-product-internetsourceadmin"
    },

    requires: [
        'esapp.view.acquisition.product.InternetSourceAdminModel',
        'esapp.view.acquisition.product.InternetSourceAdminController',
        'esapp.view.acquisition.editInternetSource',

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

    width: 1200,
    height: Ext.getBody().getViewSize().height < 625 ? Ext.getBody().getViewSize().height-10 : 800,  // 600,
    maxHeight: 800,

    frame: true,
    layout: {
        type: 'fit'
    },

    params: {},

    // Create a session for this view
    session: true,

    initComponent: function () {
        var me = this;
        var user = esapp.getUser();

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

        var refreshButton = {
            xtype: 'button',
            iconCls: 'fa fa-refresh fa-2x',
            style: { color: 'gray' },
            enableToggle: false,
            scale: 'medium',
            handler: 'reloadStore'
        };
        // var deleteButton = {
        //     text: esapp.Utils.getTranslation('delete'),  // 'Delete',
        //     iconCls: 'fa fa-minus-circle fa-2x',
        //     style: {color: 'red'},
        //     scale: 'medium',
        //     disabled: true,
        //     handler: 'onRemoveInternetSourceClick',
        //     bind: {
        //         disabled: '{!internetSourceGrid.selection}'
        //     }
        // };


        me.tbar = [addButton, '->', refreshButton];

        if (me.params.assigntoproduct){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('assigninternetsource')
                + ': ' + me.params.product.productcode + ' ' + me.params.product.version + '</span>');

            me.bbar = ['->', assignButton];
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('internetsources') + '</span>');
        }

        me.items = [{
            xtype: 'grid',
            reference: 'internetSourceGrid',
            bind: '{internetsources}',
            listeners: {
                itemdblclick: 'onEditInternetSourceClick'
            },
            selModel: {
                allowDeselect: true
            },
            layout: 'fit',

            viewConfig: {
                stripeRows: false,
                enableTextSelection: true,
                draggable: false,
                markDirty: false,
                resizable: false,
                disableSelection: false,
                trackOver: true
            },

            bufferedRenderer: false,
            scrollable: 'y',    // vertical scrolling only
            collapsible: false,
            enableColumnMove: false,
            enableColumnResize: true,
            multiColumnSort: false,
            columnLines: false,
            rowLines: true,
            frame: false,
            border: false,

            cls: 'grid-column-header-multiline',

            columns: [{
                xtype: 'actioncolumn',
                hidden: false,
                width: 40,
                align: 'center',
                sortable: false,
                menuDisabled: true,
                shrinkWrap: 0,
                items: [{
                    // icon: 'resources/img/icons/edit.png',
                    // tooltip: esapp.Utils.getTranslation('editinternetsource') // 'Edit Internet Source'
                    width:'35',
                    disabled: false,
                    getClass: function (v, meta, rec) {
                       if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)) {
                           return 'edit';
                       }
                       else {
                           // return 'x-hide-display';
                           return 'vieweye';
                       }
                    },
                    getTip: function (v, meta, rec) {
                       if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)) {
                           return esapp.Utils.getTranslation('editinternetsource');    // 'Edit Internet datasource',
                       }
                    },
                    handler: 'onEditInternetSourceClick'
                }]
            }, {
                dataIndex: 'internet_id',
                header: esapp.Utils.getTranslation('id'), // 'ID'
                width: 280,
                minWidth: 150,
                align: 'left',
                menuDisabled: true,
                sortable: true,
                cellWrap: true
            }, {
                dataIndex: 'descriptive_name',
                header: esapp.Utils.getTranslation('name'), // 'Name'
                width: 250,
                minWidth: 150,
                align: 'left',
                menuDisabled: true,
                sortable: false,
                cellWrap: true
            }, {
                dataIndex: 'url',
                header: esapp.Utils.getTranslation('url'), // 'URL'
                width: 320,
                minWidth: 200,
                align: 'left',
                menuDisabled: true,
                sortable: false,
                cellWrap: true
            }, {
                dataIndex: 'type',
                header: esapp.Utils.getTranslation('type'), // 'Type'
                width: 110,
                minWidth: 80,
                align: 'center',
                menuDisabled: true,
                sortable: true,
                cellWrap: true
            }, {
                dataIndex: 'update_datetime',
                header: esapp.Utils.getTranslation('lastupdated'), // 'Last updated'
                width: 130,
                minWidth: 120,
                align: 'center',
                menuDisabled: true,
                sortable: false,
                cellWrap: true
            },{
               xtype: 'actioncolumn',
               hidden: false,
               width: 35,
               align: 'center',
               sortable: false,
               menuDisabled: true,
               shrinkWrap: 0,
               items: [{
                   width:'35',
                   // disabled: false,
                   isDisabled: function(view, rowIndex, colIndex, item, record){
                        if (!record.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                            return false;
                        }
                        else {
                            return true;
                        }
                   },
                   getClass: function(cell, meta, rec) {
                       if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                           return 'delete';
                       }
                       else {
                           // cell.setDisabled(true);
                           return 'x-hide-display';
                       }
                   },
                   getTip: function(cell, meta, rec) {
                       if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                           return esapp.Utils.getTranslation('deleteinternetsource');    // 'Delete Internet datasource',
                       }
                   },
                   handler: 'onRemoveInternetSourceClick'
               }]
            }]
        }];


        me.callParent();
    }
});
