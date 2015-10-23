Ext.define('esapp.view.datamanagement.sendRequestController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.datamanagement-sendrequest',

    getRequest: function(win) {
        var me = this.getView();

        //var params = Ext.JSON.encode(win.params);
        var params = {}
        if (me.params.level == 'product') {
            params = {
                level: me.params.level,
                productcode: me.params.record.get('productcode'),
                version: me.params.record.get('version')
            };
        }
        else if (me.params.level == 'mapset') {
            //var inputproducts = me.params.record.get('inputproducts');
            //productcode: inputproducts[0].productcode,
            params = {
                level: me.params.level,
                productcode: me.params.record.get('productcode'),
                version: me.params.record.get('version'),
                mapsetcode: me.params.record.get('mapsetcode')
            };
        }
        else {
            params = {
                level: me.params.level,
                productcode: me.params.record.get('productcode'),
                version: me.params.record.get('version'),
                mapsetcode: me.params.record.get('mapsetcode'),
                subproductcode: me.params.record.get('subproductcode')
            };
        }

        Ext.Ajax.request({
            method: 'GET',
            url:'datamanagement/getrequest',
            params: params,
            loadMask: esapp.Utils.getTranslation('loading'),    // 'Loading...',
            callback:function(callinfo,responseOK,response ){
                var request = Ext.JSON.decode(response.responseText.trim());
                console.info(request.request);
                request = request.request;
                var requestHTML = '<h3><b style="word-wrap: break-word;">' + esapp.Utils.getTranslation('generate_request_text') + '</b></h3>';
                requestHTML = requestHTML + '<table><tr><td><b>' + esapp.Utils.getTranslation('productcode') + ': </b></td><td><b>' + request.product + '</b></td></tr><tr><td><b>' + esapp.Utils.getTranslation('version') + ': </b></td><td><b>' + request.version + '</b></td></tr></table>';
                requestHTML = requestHTML + '<table id="gradient-style" width="100%"><thead><tr><th scope="col">' + esapp.Utils.getTranslation('mapset') + '</th><th scope="col">' + esapp.Utils.getTranslation('subproduct') + '</th></tr></thead><tbody>';
                for (var mapset in request.productmapsets) {
                    requestHTML = requestHTML + '<tr><td>' + request.productmapsets[mapset].mapsetcode + '</td><td><table>';
                    for (var dataset in request.productmapsets[mapset].mapsetdatasets) {
                        var missingfiles = esapp.Utils.getTranslation('missingfiles') + ': ' + request.productmapsets[mapset].mapsetdatasets[dataset].missing[0].info.missingfiles;
                        var totfiles = esapp.Utils.getTranslation('totalfiles') + ': ' + request.productmapsets[mapset].mapsetdatasets[dataset].missing[0].info.totfiles;
                        requestHTML = requestHTML + '<tr><td>' + request.productmapsets[mapset].mapsetdatasets[dataset].subproductcode + '</td><td>' + missingfiles + ' - ' + totfiles + '</td></tr>';
                    };
                    requestHTML = requestHTML + '</table></td></tr>';
                };
                requestHTML = requestHTML + '</tbody></table>';

                Ext.getCmp('requestcontent').setHtml(requestHTML);
            },
            success: function ( result, request ) {},
            failure: function ( result, request) {}
        });
    } // eo getFile

    ,onSaveClick: function () {
        var me = this.getView();

        //var params = Ext.JSON.encode(win.params);
        var params = {}
        if (me.params.level == 'product') {
            params = {
                level: me.params.level,
                productcode: me.params.record.get('productcode'),
                version: me.params.record.get('version')
            };
        }
        else if (me.params.level == 'mapset') {
            //var inputproducts = me.params.record.get('inputproducts');
            //productcode: inputproducts[0].productcode,
            params = {
                level: me.params.level,
                productcode: me.params.record.get('productcode'),
                version: me.params.record.get('version'),
                mapsetcode: me.params.record.get('mapsetcode')
            };
        }
        else {
            params = {
                level: me.params.level,
                productcode: me.params.record.get('productcode'),
                version: me.params.record.get('version'),
                mapsetcode: me.params.record.get('mapsetcode'),
                subproductcode: me.params.record.get('subproductcode')
            };
        }

        esapp.Utils.download({
            method: 'GET',
            url: 'datamanagement/saverequest',
            params: params
        });

        this.onCancelClick();

        //if (!Ext.fly('frmExportDummy')) {
        //    var frm = document.createElement('form');
        //    frm.id = 'frmExportDummy';
        //    frm.name = id;
        //    frm.className = 'x-hidden';
        //    document.body.appendChild(frm);
        //}
        //
        //Ext.Ajax.request({
        //    method: 'GET',
        //    url:'datamanagement/saverequest',
        //    params: params,
        //    //disableCaching: false,
        //    isUpload: true,
        //    form: Ext.fly('frmExportDummy'),
        //    callback:function (callinfo,responseOK,response ){},
        //    success: function ( result, request ) {},
        //    failure: function ( result, request) {}
        //});
    }
    ,onCancelClick: function () {
        Ext.destroy(this.getView());
    }
});


