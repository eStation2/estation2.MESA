Ext.define('esapp.view.analysis.ProductNavigatorController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-productnavigator',

    assignLegend: function(){
        var me = this.getView();
        var productname = me.selectedproduct['productname'];
        var productcode = me.selectedproduct['productcode'];
        var productversion = me.selectedproduct['productversion'];
        var subproductcode = me.selectedproduct['subproductcode'];
        var legendsstore  = Ext.data.StoreManager.lookup('LegendsStore');
        var productlegendsstore = me.lookupReference('colorschemesGrid').getStore('colorschemes');
        var productlegendids = [];
        productlegendsstore.each( function (record){
            productlegendids.push(record.data.legend_id);
        });
        // filter legend store where legendid not in productlegends
        var filters = legendsstore.getFilters(); // an Ext.util.FilterCollection
        function excludeProductLegends (record) {
            return !(Ext.Array.contains(productlegendids, record.data.legendid));
        }
        filters.add(excludeProductLegends);


        var newAssignLegendWin = new esapp.view.analysis.legendAdmin({
            assign: true,
            productname: productname,
            productcode: productcode,
            productversion: productversion,
            subproductcode: subproductcode,
            productNavigatorObj: me
        });
        // this.getView().add(newLegendAdminWin);
        newAssignLegendWin.show();


        // var assignLegendWin = Ext.getCmp('assignLegendWin');
        // if (assignLegendWin==null || assignLegendWin=='undefined' ) {
        //
        //     assignLegendWin = Ext.create('Ext.window.Window', {
        //          id: 'assignLegendWin'
        //         // ,reference:'assignLegendWin'
        //         ,referenceHolder: true
        //         ,layout: 'fit'
        //         ,hidden: true
        //         ,autoHeight: false
        //         ,maxHeight: 600
        //         ,width: 640
        //         ,resizable: false
        //         ,plain: true
        //         ,stateful :false
        //         ,closable: true
        //         ,loadMask: true
        //         ,title: esapp.Utils.getTranslation('assign_legends_to') + ' ' + productname + '<b class="smalltext"> - ' + productversion + '</b>'  // 'Assign legends to <productname>'
        //         ,closeAction:'destroy'
        //         ,modal: true
        //         ,deferredRender: false
        //         ,frame: false
        //         ,border: true
        //         ,collapsible: false
        //         // ,bodyStyle: 'padding: 15px 3px 0 3px;'
        //         ,defaults: {autoScroll:true}
        //         ,listeners: {
        //              close: function(){
        //                  filters.remove(excludeProductLegends);
        //                  var selecteddataset = me.lookupReference('mapset-dataset-grid').getSelectionModel().getSelected().items[0];
        //                  me.getController().mapsetDataSetGridRowClick(this, selecteddataset);
        //              }
        //         }
        //         ,bbar: [{
        //             xtype: 'box',
        //             html: '<b style="color:orangered">' + 'Hold the [Ctrl] key for multiple selections!' + '</b>'
        //         },
        //         '->',{
        //             reference: 'assignLegendsBtn',
        //             text: esapp.Utils.getTranslation('assign_selected_legends'), // 'Assign selected legends'
        //             iconCls:'fa fa-plus-circle fa-1x',
        //             style: {color:'green'},
        //             handler: function(){
        //                 var selrec = assignLegendWin.lookupReference('assignLegendsGrid').getSelectionModel().getSelected();
        //                 var selected_legendids = [];
        //                 for ( var i=0, len=selrec.items.length; i<len; ++i ){
        //                   selected_legendids.push(selrec.items[i].data.legendid);
        //                 }
        //
        //                 Ext.Ajax.request({
        //                    url:'legends/assignlegends',
        //                    params:{
        //                        productcode: productcode,
        //                        productversion: productversion,
        //                        subproductcode: subproductcode,
        //                        legendids:Ext.util.JSON.encode(selected_legendids)
        //                    },
        //                    method: 'POST',
        //                    waitMsg: esapp.Utils.getTranslation('assigning_legends'), // 'Assigning legends...',
        //                    scope:this,
        //                    success: function(result, request) {
        //                        // The success handler is called if the XHR request actually
        //                        // made it to the server and a response of some kind occurs.
        //                        var returnData = Ext.util.JSON.decode(result.responseText);
        //                        if (returnData.success){
        //                            var selecteddataset = me.lookupReference('mapset-dataset-grid').getSelectionModel().getSelected().items[0];
        //                            me.getController().mapsetDataSetGridRowClick(this, selecteddataset);
        //
        //                            filters.remove(excludeProductLegends);
        //                            Ext.toast({html: esapp.Utils.getTranslation('legends_assiged'), title: esapp.Utils.getTranslation('legends_assiged'), width: 200, align: 't'});
        //                            assignLegendWin.close();
        //                        } else if(!returnData.success){
        //                            esapp.Utils.showError(returnData.message || result.responseText);
        //                        }
        //                    }, // eo function onSuccess
        //                    failure: function(result, request) {
        //                        // The failure handler is called if there's some sort of network error,
        //                        // like you've unplugged your ethernet cable, the server is down, etc.
        //                        var returnData = Ext.util.JSON.decode(result.responseText);
        //                        esapp.Utils.showError(returnData.message || result.responseText);
        //                    } // eo function onFailure
        //                 });
        //             }
        //         }]
        //         ,items: [{
        //             xtype : 'grid',
        //             reference: 'assignLegendsGrid',
        //             // bind: '{legends}',
        //             store: legendsstore,
        //             bufferedRenderer: false,
        //             viewConfig: {
        //                 stripeRows: false,
        //                 enableTextSelection: true,
        //                 draggable: false,
        //                 markDirty: false,
        //                 preserveScrollOnRefresh: true,
        //                 forceFit:true
        //             },
        //
        //             selModel : {
        //                 allowDeselect : false,
        //                 mode:'MULTI'
        //             },
        //
        //             hideHeaders: false,
        //             collapsible: false,
        //             enableColumnMove:false,
        //             enableColumnResize:true,
        //             sortableColumns:true,
        //             multiColumnSort: false,
        //             columnLines: true,
        //             rowLines: true,
        //             frame: false,
        //             border: false,
        //             bodyBorder: false,
        //
        //             columns: [{
        //                 text: esapp.Utils.getTranslation('legend_descriptive_name'),  // 'Sub menu',
        //                 width: 300,
        //                 dataIndex: 'legend_descriptive_name',
        //                 cellWrap:true,
        //                 menuDisabled: true,
        //                 sortable: true,
        //                 variableRowHeight : true,
        //                 draggable:false,
        //                 groupable:false,
        //                 hideable: false
        //             }, {
        //                 text: esapp.Utils.getTranslation('colourscheme'),  // 'Colour Scheme',
        //                 width: 300,
        //                 dataIndex: 'colourscheme',
        //                 cellWrap:true,
        //                 menuDisabled: true,
        //                 sortable: true,
        //                 variableRowHeight : true,
        //                 draggable:false,
        //                 groupable:false,
        //                 hideable: false
        //             }]
        //         }]
        //     });
        // }
        // assignLegendWin.show();

    },

    unassignLegend: function(view, rowIndex, colIndex, item, e, record){
        var me = this.getView();
        var legendid = record.get('legend_id');
        var productcode = me.selectedproduct['productcode'];
        var productversion = me.selectedproduct['productversion'];
        var subproductcode = me.selectedproduct['subproductcode'];

        Ext.Ajax.request({
           url:'legends/unassignlegend',
           params:{
               productcode: productcode,
               productversion: productversion,
               subproductcode: subproductcode,
               legendid: legendid
           },
           method: 'POST',
           scope:this,
           success: function(result, request) {
               // The success handler is called if the XHR request actually
               // made it to the server and a response of some kind occurs.
               var returnData = Ext.util.JSON.decode(result.responseText);
               if (returnData.success){
                   var selecteddataset = me.lookupReference('mapset-dataset-grid').getSelectionModel().getSelected().items[0];
                   me.getController().mapsetDataSetGridRowClick(this, selecteddataset);
               }
               else if(!returnData.success){
                   esapp.Utils.showError(returnData.message || result.responseText);
               }
           }, // eo function onSuccess
           failure: function(result, request) {
               // The failure handler is called if there's some sort of network error,
               // like you've unplugged your ethernet cable, the server is down, etc.
               var returnData = Ext.util.JSON.decode(result.responseText);
               esapp.Utils.showError(returnData.message || result.responseText);
           } // eo function onFailure
        });

    },

    editLegend: function(grid, record, element, rowIndex, e, eOpts){
        if(!isNaN(record)) {    // record is the rowIndex so get the record from the store through the rowIndex
            record = grid.getStore().getAt(record);
        }

        var defaultData = {
            legendid: record.get('legend_id'),
            colourscheme: record.get('colorschemeHTML'),
            legendname: record.get('legend_name'),
            minvalue: null, // record.get('minvalue'),
            maxvalue: null, // record.get('maxvalue'),
            legend_descriptive_name: record.get('colorbar')
        };
        var newrecord = new esapp.model.Legend(defaultData);

        var editLegendWin = new esapp.view.analysis.addEditLegend({
            params: {
                edit: true,
                legendrecord: newrecord
            }
        });
        editLegendWin.show();
    },

    loadProductsGrid: function() {

        var productinfopanel = this.getView().lookupReference('product-datasets-info');
        productinfopanel.setTitle('<div class="panel-title-style-16">'+esapp.Utils.getTranslation('productinfo')+'</div>');
        productinfopanel.collapse();

        var mapsetdatasetgrid = this.getView().lookupReference('mapset-dataset-grid');
        if (mapsetdatasetgrid){
            mapsetdatasetgrid.hide();
        }
        var colorschemesgrid = this.getView().lookupReference('colorschemesGrid');
        if (colorschemesgrid){
            colorschemesgrid.hide();
        }

        this.getStore('colorschemes').removeAll();
        this.getStore('mapsetdatasets').removeAll();
        this.getStore('productmapsets').removeAll();

        var prodgrid = this.getView().lookupReference('productsGrid');
        var myLoadMask = new Ext.LoadMask({
            msg    : esapp.Utils.getTranslation('loading'), // 'Loading...',
            target : prodgrid
        });
        myLoadMask.show();

        Ext.data.StoreManager.lookup('ProductNavigatorStore').load({
            params: {
                force: true
            },
            callback:function(){
                myLoadMask.hide();
            }
        });
        // this.getStore('products').load({
        //     params: {
        //         force: true
        //     },
        //     callback:function(){
        //         myLoadMask.hide();
        //     }
        // });
    },

    productsGridRowClick: function(gridview, record){
        var me = this.getView();

        this.lookupReference('addtomapbtn_'+this.getView().mapviewid.replace(/-/g,'_')).disable();
        this.lookupReference('mapset-dataset-grid').hide();
        this.lookupReference('colorschemesGrid').hide();
        this.getStore('colorschemes').removeAll();
        this.getStore('mapsetdatasets').removeAll();
        this.getStore('productmapsets').removeAll();

        var productinfopanel = this.lookupReference('product-datasets-info');
        if (record.get('version') != 'undefined')
            productinfopanel.setTitle('<div class="panel-title-style-16">' + record.get('prod_descriptive_name') + '<b class="smalltext"> ' + record.get('version') + '</b>' + '</div>');
        else
            productinfopanel.setTitle('<div class="panel-title-style-16">' + record.get('prod_descriptive_name') + '</div>');

        productinfopanel.expand(true);
        this.getStore('productmapsets').setData(record.get('productmapsets'));
        me.productsensor = record.get('prod_descriptive_name');
    },

    mapsetItemClick: function(dataview, record ){
        this.lookupReference('addtomapbtn_'+this.getView().mapviewid.replace(/-/g,'_')).disable();
        this.getStore('colorschemes').removeAll();
        this.getStore('mapsetdatasets').removeAll();
        // nodes contain all selected records when dataview has multiSelect to true!
        // here we do not use multiSelect so nodes is the record of the selected mapset!
        this.getStore('mapsetdatasets').setData(record.get('mapsetdatasets'));
        var sorters = [{
        //     property: 'prod_descriptive_name',
        //     direction: 'ASC'
        // },{
            property: 'display_index',
            direction: 'ASC'
        }];

        // var colorschemesgrid = this.lookupReference('colorschemesGrid');
        // colorschemesgrid.columns[1].setText('<div class="grid-header-style">'+esapp.Utils.getTranslation('colorschemes')+'</div>');
        // colorschemesgrid.show();

        this.getStore('mapsetdatasets').setSorters(sorters);
        this.getStore('mapsetdatasets').sort(sorters);
        var mapsetdatasetgrid = this.lookupReference('mapset-dataset-grid');
        mapsetdatasetgrid.columns[0].setText('<div class="grid-header-style">' + esapp.Utils.getTranslation('datasets') + ' <b class="smalltext">' + esapp.Utils.getTranslation('formapset') + ' ' + record.get('descriptive_name') + '</b></div>');
        mapsetdatasetgrid.show();

    },

    mapsetDataSetGridRowClick: function(gridview, record, tr, rowIndex, e, eOpts) { // for rowclick
        var me = this.getView();
        var addToMapBtn = this.getView().lookupReference('addtomapbtn_'+this.getView().mapviewid.replace(/-/g,'_'));
        var colorschemesgrid = me.lookupReference('colorschemesGrid');
        var mapsetdatasetgrid = this.lookupReference('mapset-dataset-grid');

        me.selectedproduct = {
            productcode:record.get('productcode'),
            productversion:record.get('version'),
            mapsetcode:record.get('mapsetcode'),
            subproductcode:record.get('subproductcode'),
            productname:record.get('descriptive_name'),
            date_format:record.get('date_format'),
            frequency_id:record.get('frequency_id'),
            productsensor: me.productsensor
        };

        // colorschemesgrid.columns[1].setText('<div class="grid-header-style">' + esapp.Utils.getTranslation('colorschemes') +
        //     ' <b class="smalltext">' + esapp.Utils.getTranslation('for') + ' ' + record.get('descriptive_name') +
        //     ' ' + record.get('version') + ' - ' + record.get('subproductcode') + '</b></div>');
        colorschemesgrid.columns[1].setText('<div>' +
            ' <b class="smalltext">' + esapp.Utils.getTranslation('for') + ' ' + record.get('descriptive_name') +
            ' ' + record.get('version') + ' <BR> ' + record.get('subproductcode') + '</b></div>');

        if (colorschemesgrid.hidden) {
            // console.info('colorschemesgrid hidden, so show');
            colorschemesgrid.show();
        }

        this.getStore('colorschemes').removeAll();

        this.getStore('colorschemes').load({
            params:this.getView().selectedproduct,
            callback:function(records, options, success){
                if (records != null && records.length>0){
                    var nodefault = true,
                        defaultcount = 0;
                    for (var i = 0; i < records.length; i++) {
                        if (records[i].get('default_legend') || records[i].get('default_legend') === 'true') {
                            defaultcount += 1;
                            nodefault = false;
                        }
                    }
                    if (defaultcount > 1) {
                        for (var ii = 0; ii < records.length; ii++) {
                            // records[ii].data.default_legend = false;
                            // records[ii].data.defaulticon = 'x-grid3-radio-col';
                            // records[ii].dirty = false;
                            records[ii].set('default_legend', 'false');
                            records[ii].set('defaulticon', 'x-grid3-radio-col');
                        }
                        nodefault = true;
                    }
                    if (nodefault) {
                        // records[0].data.default_legend = true;
                        // records[0].data.defaulticon = 'x-grid3-radio-col-on';
                        // records[0].dirty = false;
                        records[0].set('default_legend', 'true');
                        records[0].set('defaulticon', 'x-grid3-radio-col-on');
                    }
                    addToMapBtn.enable();
                }
            }
        });


        var task = new Ext.util.DelayedTask(function() {
            mapsetdatasetgrid.fireEvent('scrolltoselection');
        });
        task.delay(250);

    },

    onRadioColumnAction:function(view, rowIndex, colIndex, item, e, record ) {
        switch(record.get('defaulticon')) {
            case 'x-grid3-radio-col':
                    view.getStore('colorschemes').each(function(rec){
                        if (view.getStore().indexOf(rec) != rowIndex) {
                            // rec.data.default_legend = 'false';
                            // rec.data.defaulticon = 'x-grid3-radio-col';
                            // rec.dirty = false;
                            rec.set('default_legend', false);
                            rec.set('defaulticon', 'x-grid3-radio-col');
                        }
                    },this);

                    // record.data.default_legend = 'true';
                    // record.data.defaulticon = 'x-grid3-radio-col-on';
                    // record.dirty = false;
                    record.set('default_legend', true);
                    record.set('defaulticon', 'x-grid3-radio-col-on');
                break;
            default:
        }
    }
});
