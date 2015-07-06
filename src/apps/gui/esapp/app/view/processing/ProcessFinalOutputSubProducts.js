
Ext.define("esapp.view.processing.ProcessFinalOutputSubProducts",{
    "extend": "Ext.grid.Panel",
    "controller": "processing-finaloutputsubproducts",
    "viewModel": {
        "type": "processing-finaloutputsubproducts"
    },

    "xtype"  : 'process-finaloutputsubproducts-grid',

    requires: [
        'esapp.view.processing.ProcessFinalOutputSubProductsModel',
        'esapp.view.processing.ProcessFinalOutputSubProductsController',

        'Ext.grid.column.Action',
        'Ext.grid.column.Widget'
    ],

    store: null,

    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable: false,
        markDirty: false,
        resizable: false,
        disableSelection: true,
        trackOver: false
    },

    hideHeaders: true,
    columnLines: false,
    rowLines:false,

    initComponent: function () {
        var me = this;

        me.defaults = {
            menuDisabled: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false
        };

        me.columns = [{
            xtype:'templatecolumn',
            header: '', // 'Productcode',
            tpl: new Ext.XTemplate(
                    '<b>{productcode}</b>' +
                    '<tpl if="version != \'undefined\'">',
                        '<b> - {version}</b>',
                    '</tpl>',
                    '</br>' +
                    '<b class="smalltext" style="color:darkgrey">{prod_descriptive_name}</b>' +
                    '</br>'
                ),
            width: 250,
            cellWrap:true
        }, {
            header: '', // 'Mapsetcode',
            dataIndex: 'mapsetcode',
            width: 200
        }, {

            header: '', // 'Subproductcode',
            dataIndex: 'subproductcode',
            width: 150
            },{
                xtype: 'actioncolumn',
                header: 'Active',
                hideable: false,
                hidden: false,
                width: 65,
                align: 'center',
                shrinkWrap: 0,
                items: [{
                    // scope: me,
                    // handler: me.onToggleActivation
                    getClass: function(v, meta, rec) {
                        if (rec.get('subactivated')) {
                            return 'activated';
                        } else {
                            return 'deactivated';
                        }
                    },
                    getTip: function(v, meta, rec) {
                        if (rec.get('subactivated')) {
                            return 'Deactivate SubProduct';
                        } else {
                            return 'Activate SubProduct';
                        }
                    },
                    handler: function(grid, rowIndex, colIndex) {
                        var rec = grid.getStore().getAt(rowIndex),
                            action = (rec.get('subactivated') ? 'deactivated' : 'activated');
                        //Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                        rec.get('subactivated') ? rec.set('subactivated', false) : rec.set('subactivated', true);
                    }
                }]
//        },{
//            xtype: 'checkcolumn',
//            header: '', // Active
//            width: 65,
//            dataIndex: 'activated',
//            stopSelection: false,
//            hideable: true,
//            hidden: false,
//            disabled: false,
//            listeners: {
//              checkchange: function(chkBox, rowIndex, checked, eOpts){
//                  var myTitle = ""
//                  if (checked)  myTitle = "Activate Processing of Final SubProduct";
//                  else myTitle = "De-activate Processing of Final SubProduct";
//                  Ext.toast({ html: 'Checkbox clicked!', title: myTitle, width: 200, align: 't' });
//              }
//            }
        }];

        me.callParent();
    }

});
