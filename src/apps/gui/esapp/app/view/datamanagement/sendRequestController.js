Ext.define('esapp.view.datamanagement.sendRequestController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.datamanagement-sendrequest',

    getRequest: function() {
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

        var myMask = Ext.create('Ext.LoadMask', {
            msg    : esapp.Utils.getTranslation('loading'),
            target : me.lookupReference('requestcontent'),
            alwaysOnTop: true,
            maxHeight: 300
            // constrain: true,
            // autoRender: true,
            // autoShow: true
            // border : false,
            // frame : false,
            // shadow : false
        });

        // me.alignTo(Ext.getCmp('datamanagementmain'), 'c');
        myMask.show();

        Ext.Ajax.request({
            method: 'GET',
            url:'datamanagement/getrequest',
            params: params,
            // loadMask: esapp.Utils.getTranslation('loading'),    // 'Loading...',
            callback:function(callinfo,responseOK,response ){

            },
            success: function ( result, request ) {
                var request = Ext.JSON.decode(result.responseText.trim());
                // console.info(request.request);
                request = request.request;

                var requestHTML = '<h3><b style="word-wrap: break-word;">' + esapp.Utils.getTranslation('missingdatafor') + ':</b></h3>';     // generate_request_text
                requestHTML = requestHTML + '<table><tr><td><b>' + esapp.Utils.getTranslation('productcode') + ': </b></td><td><b>' + request.product + '</b></td></tr><tr><td><b>' + esapp.Utils.getTranslation('version') + ': </b></td><td><b>' + request.version + '</b></td></tr></table>';
                requestHTML = requestHTML + '<table id="gradient-style" width="100%"><thead><tr><th scope="col">' + esapp.Utils.getTranslation('mapset') + '</th><th scope="col">' + esapp.Utils.getTranslation('subproduct') + '</th></tr></thead><tbody>';
                for (var mapsetrec in request.productmapsets) {
                    requestHTML = requestHTML + '<tr><td style="vertical-align:top">' + request.productmapsets[mapsetrec].mapset.mapsetcode + '</td><td><table>';
                    for (var dataset in request.productmapsets[mapsetrec].mapsetdatasets) {
                        var missingfiles = esapp.Utils.getTranslation('missingfiles') + ': ' + request.productmapsets[mapsetrec].mapsetdatasets[dataset].missingfiles.length;
                        requestHTML = requestHTML + '<tr><td>' + request.productmapsets[mapsetrec].mapsetdatasets[dataset].subproductcode + '</td><td>' + missingfiles + '</td></tr>';
                    }
                    requestHTML += '</table></td></tr>';
                }
                requestHTML += '</tbody></table>';

                me.lookupReference('requestcontent').setHtml(requestHTML);

                me.lookupReference('getmissingfiles-btn').enable();
                myMask.hide();
            },
            failure: function ( result, request) {
                myMask.hide();
            }
        });
    } // eo getFile


    ,createRequestJob: function () {
        var me = this.getView();
        var thiscontroller = this;

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

        var myMask = new Ext.LoadMask({
            msg    : esapp.Utils.getTranslation('creating_requestjob'),
            target : me,    // me.lookupReference('requestcontent'),
            alwaysOnTop: true,
            maxHeight: 300
            // constrain: true
            // border : false,
            // frame : false,
            // shadow : false
        });

        myMask.show();
        me.lookupReference('getmissingfiles-btn').disable();

        Ext.Ajax.request({
            method: 'GET',
            url:'datamanagement/createrequestjob',
            params: params,
            // loadMask: esapp.Utils.getTranslation('loading'),    // 'Loading...',
            callback:function(callinfo,responseOK,response ){
                var request = Ext.JSON.decode(response.responseText.trim());
                if (request.success){
                    // Job created and running. Show and refresh requests admin tool
                    var requestsbtn = Ext.getCmp('datamanagement-requests-btn');
                    requestsbtn.requestsAdminPanel.setDirtyStore(true);
                    requestsbtn.requestsAdminPanel.show();
                    myMask.hide();
                    thiscontroller.onCancelClick();
                }
                else{
                    myMask.hide();
                    me.lookupReference('getmissingfiles-btn').enable();
                    Ext.Msg.show({
                        title: esapp.Utils.getTranslation('internet_proxy_error_title'),
                        message: esapp.Utils.getTranslation('internet_proxy_error_msg'),
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.WARNING,
                        fn: function(btn) {
                            if (btn === 'ok') {
                                // todo: go to system tab?
                            }
                        }
                    });
                }
            }
        });

    }

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
        this.getView().close();
        // Ext.destroy(this.getView());
    }
});


