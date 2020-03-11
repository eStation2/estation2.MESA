Ext.define('esapp.view.analysis.addEditLayerModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-addeditlayer',
    stores: {
        layertypes:{
            fields: ['layertype', 'layertypename'],
            sorters: {property: 'layertype', direction: 'DESC'},
            data: [
                {layertype: 'polygon', layertypename: 'Polygon'},
                {layertype: 'line', layertypename: 'Line'},
                {layertype: 'point', layertypename: 'Point'}
            ]
        },
        layermenu:{
            fields: ['menu', 'menuname'],
            sorters: {property: 'menu', direction: 'DESC'},
            data: [
                {menu: 'border', menuname: esapp.Utils.getTranslation('borderlayers')},
                {menu: 'marine', menuname: esapp.Utils.getTranslation('marinelayers')},
                {menu: 'other', menuname: esapp.Utils.getTranslation('otherlayers')}
            ]
        },
        serverlayerfiles:{
            fields: ['layerfilename', 'filesize'],
            sorters: {property: 'layerfilename', direction: 'ASC'}

            ,autoLoad: true

            ,proxy: {
                type : 'ajax',
                url : 'layers/serverlayerfiles',
                reader: {
                     type: 'json'
                    ,successProperty: 'success'
                    ,rootProperty: 'layerfiles'
                    ,messageProperty: 'message'
                },
                listeners: {
                    exception: function(proxy, response, operation){
                        console.info('ADD EDIT LAYER VIEW MODEL - REMOTE EXCEPTION!');
                    }
                }
            }

        }
        // chained store for grid
        //,serverlayerfilesChained:{
        //    source:'{serverlayerfiles}'
        //}
    }

    //initConfig: function () {
    //    var me = this;
    //    console.info('InitConfig of addEditLayerModel');
    //    console.info(me);
    //
    //    me.stores = {
    //        layertypes:{
    //            fields: ['layertype', 'layertypename'],
    //            sorters: {property: 'layertype', direction: 'DESC'},
    //            data: [
    //                {layertype: 'polygon', layertypename: 'Polygon'},
    //                {layertype: 'line', layertypename: 'Line'},
    //                {layertype: 'point', layertypename: 'Point'}
    //            ]
    //        },
    //        layermenu:{
    //            fields: ['menu', 'menuname'],
    //            sorters: {property: 'menu', direction: 'DESC'},
    //            data: [
    //                {menu: 'border', menuname: "'" + esapp.Utils.getTranslation('borderlayers') + "'"},
    //                {menu: 'marine', menuname: "'" + esapp.Utils.getTranslation('marinelayers') + "'"},
    //                {menu: 'other', menuname: "'" + esapp.Utils.getTranslation('otherlayers') + "'"}
    //            ]
    //        },
    //        serverlayerfiles:{
    //            fields: ['layerfilename', 'filesize'],
    //            sorters: {property: 'layerfilename', direction: 'ASC'}
    //
    //            ,autoLoad: true
    //
    //            ,proxy: {
    //                type : 'ajax',
    //                url : 'layers/serverlayerfiles',
    //                reader: {
    //                     type: 'json'
    //                    ,successProperty: 'success'
    //                    ,rootProperty: 'layerfiles'
    //                    ,messageProperty: 'message'
    //                },
    //                listeners: {
    //                    exception: function(proxy, response, operation){
    //                        console.info('ADD EDIT LAYER VIEW MODEL - REMOTE EXCEPTION!');
    //                    }
    //                }
    //            }
    //
    //        }
    //        // chained store for grid
    //        //,serverlayerfilesChained:{
    //        //    source:'{serverlayerfiles}'
    //        //}
    //    };
    //
    //    me.callParent();
    //}

});
