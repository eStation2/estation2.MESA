Ext.define('esapp.view.analysis.ProductNavigatorController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-productnavigator',

    loadProductsGrid: function() {

        var productinfopanel = this.getView().lookupReference('product-datasets-info');
        productinfopanel.setTitle('<div class="panel-title-style-16">Product Info</div>');
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
            msg    : 'Loading...',
            target : prodgrid
        });
        myLoadMask.show();

        this.getStore('products').load({
            callback:function(){
                myLoadMask.hide();
            }
        });
        //    var productsgridstore  = Ext.data.StoreManager.lookup('ProductNavigatorStore');
        //    var productsgridstore = productnavwin.lookupReference('productsGrid').getStore('products');
        //    if (productsgridstore.isStore) {
        //        productsgridstore.load({loadMask:true});
        //    }
    },

    productsGridRowClick: function(gridview, record){

        this.lookupReference('addtomapbtn').disable();
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

        //var mapsets = record.data.productmapsets;
        //var itemsInGroup = [];
        //
        //for (var i = 0, l = mapsets.length; i < l; i++) {
        //    var mapset = mapsets[i];
        //
        //    itemsInGroup.push( {
        //        boxLabel: mapset.descriptive_name,
        //        name: mapset.mapsetcode,
        //        inputValue: mapset.mapsetcode
        //    });
        //}
        //
        //var myGroup = {
        //  xtype: 'radiogroup',
        //  fieldLabel: '',
        //  items: itemsInGroup
        //};
        //
        //var productinfopanel = Ext.ComponentQuery.query('panel[id=product-datasets-info]')[0];
        //var productinfopanel = gridview.up().up().down('panel[reference=product-datasets-info]');
        //productinfopanel.down('fieldset').removeAll();
        //productinfopanel.down('fieldset').add(myGroup);
    },

    mapsetItemClick: function(dataview, record ){

        this.lookupReference('addtomapbtn').disable();
        this.lookupReference('colorschemesGrid').hide();
        this.getStore('colorschemes').removeAll();
        this.getStore('mapsetdatasets').removeAll();
        // nodes contain all selected records when dataview has multiSelect to true!
        // here we do not use multiSelect so nodes is the record of the selected mapset!
        this.getStore('mapsetdatasets').setData(record.get('mapsetdatasets'));
        var mapsetdatasetgrid = this.lookupReference('mapset-dataset-grid');
        mapsetdatasetgrid.columns[0].setText('<div class="grid-header-style">Data sets' + '<b class="smalltext"> for mapset ' + record.get('descriptive_name') + '</b></div>');
        mapsetdatasetgrid.show();
    },

    mapsetDataSetGridRowClick: function(gridview, record) {

        this.getView().selectedproduct = {
            productcode:record.get('productcode'),
            productversion:record.get('version'),
            mapsetcode:record.get('mapsetcode'),
            subproductcode:record.get('subproductcode'),
            productname:record.get('descriptive_name')
        };

        //var params = {
        //       productcode:record.get('productcode'),
        //       version:record.get('version'),
        //       mapsetcode:record.get('mapsetcode'),
        //       subproductcode:record.get('subproductcode')
        //};

        var colorschemesgrid = this.getView().lookupReference('colorschemesGrid');
        colorschemesgrid.hide();
        this.getStore('colorschemes').removeAll();

        var myLoadMask = new Ext.LoadMask({
            msg    : 'Loading...',
            target : colorschemesgrid
        });
        myLoadMask.show();

        var addToMapBtn = this.getView().lookupReference('addtomapbtn');

        this.getStore('colorschemes').load({
            params:this.getView().selectedproduct,
            callback:function(records, options, success){
                myLoadMask.hide();
                if (records.length>0){
                    var nodefault = true;
                    for (var i = 0; i < records.length; i++) {
                        if (records[i].get('default_legend') == 'true') {
                            nodefault = false;
                        }
                    }
                    if (nodefault) {
                        records[0].set('default_legend', true);
                        records[0].set('defaulticon', 'x-grid3-radio-col-on');
                    }
                    addToMapBtn.enable();
                    colorschemesgrid.show();
                }
            }
        });
    },

    onRadioColumnAction:function(view, rowIndex, colIndex, item, e, record ) {
        switch(record.get('defaulticon')) {
            case 'x-grid3-radio-col':
                    view.getStore().each(function(rec){
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
