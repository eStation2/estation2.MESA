
Ext.define("esapp.view.analysis.legendAdmin",{
    extend: "Ext.window.Window",
 
    requires: [
        "esapp.view.analysis.legendAdminController",
        "esapp.view.analysis.legendAdminModel",

        'esapp.view.analysis.addEditLegend',

        'Ext.grid.column.Action'
    ],
    
    controller: "analysis-legendadmin",
    viewModel: {
        type: "analysis-legendadmin"
    },

    id: 'legendsadministration',
    title: '<div class="panel-title-style-16">' + esapp.Utils.getTranslation('legendsadministration') + '</div>',
    header: {
        titlePosition: 0,
        titleAlign: 'center',
        iconCls: 'legends'
    },
    constrainHeader: Ext.getBody(),

    modal: true,
    closable: true,
    closeAction: 'destroy', // 'destroy',
    maximizable: false,
    resizable: true,
    //resizeHandles: 'n,s',
    autoScroll: true,
    height: Ext.getBody().getViewSize().height < 830 ? Ext.getBody().getViewSize().height-130 : 830,  // 600,
    minHeight: 500,
    maxHeight: 830,
    width: 935,

    border:false,
    frame: false,
    bodyBorder: false,
    layout: {
        type  : 'fit',
        padding: 1
    },

    listeners: {
        close: 'onClose'
        // ,show: 'onShow'
    },
    // session:true,

    initComponent: function () {
        var me = this;
        var user = esapp.getUser();

        me.title = '<div class="panel-title-style-16">' + esapp.Utils.getTranslation('legendsadministration') + '</div>';
        me.height = Ext.getBody().getViewSize().height < 830 ? Ext.getBody().getViewSize().height-130 : 830;  // 600,

        me.tools = [
        {
            type: 'refresh',
            align: 'c-c',
            tooltip: esapp.Utils.getTranslation('refreshlegendslist'),    // 'Refresh legend list',
            callback: 'loadLegendsStore'
        }];

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            padding: 3,
            items: [{
                xtype: 'button',
                text: esapp.Utils.getTranslation('newlegend'),    // 'New legend',
                name: 'newlegend',
                iconCls: 'fa fa-plus-circle fa-2x',
                style: {color: 'green'},
                hidden: false,
                // glyph: 'xf055@FontAwesome',
                scale: 'medium',
                handler: 'newLegend'
            },{
                xtype: 'button',
                text: esapp.Utils.getTranslation('copylegend'),    // 'Copy legend',
                name: 'copylegend',
                iconCls: 'fa fa-files-o fa-2x',
                style: {color: 'black'},
                hidden: false,
                // glyph: 'xf055@FontAwesome',
                scale: 'medium',
                handler: 'copyLegend'
            // },{
            //     xtype: 'button',
            //     text: esapp.Utils.getTranslation('exportlegend'),    // 'Export legend',
            //     name: 'exportlegend',
            //     iconCls: 'fa fa-download fa-2x',
            //     style: {color: 'black'},
            //     hidden: false,
            //     // glyph: 'xf055@FontAwesome',
            //     scale: 'medium',
            //     handler: 'exportLegend'
            // },{
            //     xtype: 'button',
            //     text: esapp.Utils.getTranslation('importlegend'),    // 'Import legend',
            //     name: 'importlegend',
            //     iconCls: 'fa fa-upload fa-2x',
            //     style: {color: 'blue'},
            //     hidden: false,
            //     // glyph: 'xf055@FontAwesome',
            //     scale: 'medium',
            //     handler: 'importLegend'
            }]
        });

        me.items = [{
            xtype : 'grid',
            reference: 'legendsGrid',
            bind: '{legends}',
            bufferedRenderer: false,
            viewConfig: {
                stripeRows: false,
                enableTextSelection: true,
                draggable: false,
                markDirty: false,
                // resizable: true,
                // disableSelection: false,
                // trackOver: true,
                preserveScrollOnRefresh: true,
                forceFit:true
            },

            selModel : {
                allowDeselect : false,
                mode:'SINGLE'
                ,listeners: {
                    doubleclick: 'editLegend'
                }
            },

            //cls: 'grid-color-yellow',
            hideHeaders: false,
            collapsible: false,
            enableColumnMove:false,
            enableColumnResize:true,
            sortableColumns:true,
            multiColumnSort: false,
            columnLines: true,
            rowLines: true,
            frame: false,
            border: false,
            bodyBorder: false,

            listeners: {
                // bodyscroll: function(scrollLeft, scrollTop){
                //      console.log('scrolling grid ... ');
                // },
                // scope: 'controller',
                // afterrender: 'loadLegendsStore',
                rowdblclick : 'editLegend'
            },

            columns: [{
                xtype: 'actioncolumn',
                // header: esapp.Utils.getTranslation('actions'),   // 'Actions',
                menuDisabled: true,
                sortable: true,
                variableRowHeight : true,
                draggable:false,
                groupable:false,
                hideable: false,
                width: 50,
                align: 'center',
                stopSelection: false,

                items: [{
                    // scope: me,
                    width:'35',
                    disabled: false,
                    getClass: function (v, meta, rec) {
                        if (rec.get('defined_by')!='JRC' || (esapp.Utils.objectExists(user) && user.userlevel == 1)){   // JRC user has userlevel 1 and can always edit legends.
                            return 'edit';
                        }
                        else return 'vieweye';
                    },
                    getTip: function (v, meta, rec) {
                        if (rec.get('defined_by')!='JRC' || (esapp.Utils.objectExists(user) && user.userlevel == 1)){   // JRC user has userlevel 1 and can always edit legends.
                            return esapp.Utils.getTranslation('editlegendproperties') + ' "' + rec.get('legend_descriptive_name') + '"';
                        }
                    },
                    handler: 'editLegend'
                }]
            }, {
                text: esapp.Utils.getTranslation('legend_descriptive_name'),  // 'Sub menu',
                width: 300,
                dataIndex: 'legend_descriptive_name',
                cellWrap:true,
                menuDisabled: true,
                sortable: true,
                variableRowHeight : true,
                draggable:false,
                groupable:false,
                hideable: false
            }, {
                text: esapp.Utils.getTranslation('colourscheme'),  // 'Colour Scheme',
                width: 300,
                dataIndex: 'colourscheme',
                cellWrap:true,
                menuDisabled: true,
                sortable: true,
                variableRowHeight : true,
                draggable:false,
                groupable:false,
                hideable: false
            // }, {
            //     text: esapp.Utils.getTranslation('legendname'),  // 'Legend name',
            //     width: 200,
            //     dataIndex: 'legendname',
            //     cellWrap:true,
            //     menuDisabled: true,
            //     sortable: true,
            //     variableRowHeight : true,
            //     draggable:false,
            //     groupable:false,
            //     hideable: false
            }, {
                text: esapp.Utils.getTranslation('minvalue'),  // 'Min value',
                width: 90,
                dataIndex: 'minvalue',
                menuDisabled: true,
                sortable: true,
                variableRowHeight : true,
                draggable:false,
                groupable:false,
                hideable: false
            }, {
                text: esapp.Utils.getTranslation('maxvalue'),  // 'Max value',
                width: 90,
                dataIndex: 'maxvalue',
                menuDisabled: true,
                sortable: true,
                variableRowHeight: true,
                draggable: false,
                groupable: false,
                hideable: false
            },{
                xtype: 'actioncolumn',
                // header: esapp.Utils.getTranslation('delete'),   // 'Actions',
                menuDisabled: true,
                sortable: true,
                variableRowHeight : true,
                draggable:false,
                groupable:false,
                hideable: false,
                width: 75,
                align: 'center',
                stopSelection: false,

                items: [{
                    // scope: me,
                    width: '35',
                    disabled: false,
                    getClass: function (v, meta, rec) {
                        if (rec.get('defined_by') != 'JRC' || (esapp.Utils.objectExists(user) && user.userlevel == 1)) {
                            return 'delete';
                        }
                    },
                    getTip: function (v, meta, rec) {
                        return esapp.Utils.getTranslation('deletelegend') + ' "' + rec.get('legend_descriptive_name') + '"';
                    },
                    handler: 'deleteLegend'
                },{
                    width:'35',
                    disabled: false,
                    getClass: function(v, meta, rec) {
                        if ((esapp.Utils.objectExists(user) && user.userlevel == 1)){
                            return 'download';
                        }
                    },
                    getTip: function(v, meta, rec) {
                        if ((esapp.Utils.objectExists(user) && user.userlevel == 1)){
                            return esapp.Utils.getTranslation('downloadlegend') + ' "' + rec.get('export_in_qgis_format') + '"';
                        }
                    },
                    handler: 'exportLegend'
                }]
            }]
        }];

        me.callParent();
    }
});
