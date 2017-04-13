Ext.define('esapp.view.analysis.ProductNavigatorController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-productnavigator',

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

        this.getStore('products').load({
            callback:function(){
                myLoadMask.hide();
            }
        });

    },

    productsGridRowClick: function(gridview, record){

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

        var colorschemesgrid = this.lookupReference('colorschemesGrid');
        colorschemesgrid.columns[1].setText('<div class="grid-header-style">'+esapp.Utils.getTranslation('colorschemes')+'</div>');
        colorschemesgrid.show();

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
            date_format:record.get('date_format')
        };

        colorschemesgrid.columns[1].setText('<div class="grid-header-style">' + esapp.Utils.getTranslation('colorschemes') +
            ' <b class="smalltext">' + esapp.Utils.getTranslation('formapset') + ' ' + record.get('descriptive_name') +
            ' - ' + record.get('subproductcode') + '</b></div>');

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
                        if (records[i].get('default_legend') || records[i].get('default_legend') == 'true') {
                            defaultcount += 1;
                            nodefault = false;
                        }
                    }
                    if (defaultcount > 1) {
                        for (var ii = 0; ii < records.length; ii++) {
                            records[ii].set('default_legend', false);
                            records[ii].set('defaulticon', 'x-grid3-radio-col');
                        }
                        nodefault = true;
                    }
                    if (nodefault) {
                        records[0].set('default_legend', true);
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
        //console.info(record);
        switch(record.get('defaulticon')) {
            case 'x-grid3-radio-col':
                    view.getStore('colorschemes').each(function(rec){
                        if (view.getStore().indexOf(rec) != rowIndex) {
                            rec.set('default_legend', false);
                            rec.set('defaulticon', 'x-grid3-radio-col');
                        }
                    },this);

                    record.set('default_legend', true);
                    record.set('defaulticon', 'x-grid3-radio-col-on');
                break;
            default:
        }
    }
});
