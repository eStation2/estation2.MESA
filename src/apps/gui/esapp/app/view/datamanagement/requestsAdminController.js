Ext.define('esapp.view.datamanagement.requestsAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.datamanagement-requestsadmin'


    ,runPauseRequest: function(grid, rowIndex, row){
        var me = this.getView();
        var record = grid.getStore().getAt(rowIndex);
        var params = {};
        var msg = '';
        var origstatus = record.get('status').toLowerCase();

        if (origstatus=='running'){
            params = {
                'requestid': record.get('requestid'),
                'task': 'pause'
            };

            msg = esapp.Utils.getTranslation('pausing_request') + ' ' + record.get('requestid');
        }
        else if (origstatus=='paused'){
            params = {
                'requestid': record.get('requestid'),
                'task': 'run'
            };
            msg = esapp.Utils.getTranslation('restarting_request') + ' ' + record.get('requestid');
        }
        else if (origstatus=='error'){  // Give the user the possibility to restart a job that is in error!
            params = {
                'requestid': record.get('requestid'),
                'task': 'run'
            };
            msg = esapp.Utils.getTranslation('restarting_request') + ' ' + record.get('requestid');
        }

        me.myMask = new Ext.LoadMask({
            msg    : msg,
            target : grid,
            border : false,
            frame : false,
            shadow : false,
            shim : true
        });

        me.myMask.show();

        Ext.Ajax.request({
            method: 'GET',
            url:'datamanagement/runpauserequest',
            params: params,
            loadMask: esapp.Utils.getTranslation('loading'),    // 'Loading...',
            callback:function(callinfo,responseOK,response ){
                var request = Ext.JSON.decode(response.responseText);
                // request = request.request;
                me.myMask.hide();
                if (Ext.isObject(request)) {
                    if (request.success) {
                        record.set('status', request.status);
                    }
                    else {
                        if (origstatus == 'running') {
                            // Error pausing the request job.
                            if (request.status.toLowerCase() == 'error') {
                                Ext.Msg.show({
                                    title: esapp.Utils.getTranslation('internet_proxy_error_title'),
                                    message: esapp.Utils.getTranslation('internet_proxy_error_msg'),
                                    buttons: Ext.Msg.OK,
                                    icon: Ext.Msg.WARNING,
                                    fn: function (btn) {
                                        if (btn === 'ok') {
                                            // todo: go to system tab?
                                        }
                                    }
                                });
                            }
                            else {
                                Ext.Msg.show({
                                    title: esapp.Utils.getTranslation('error_pausing_request'),
                                    message: request.message,
                                    buttons: Ext.Msg.OK,
                                    icon: Ext.Msg.WARNING,
                                    fn: function (btn) {
                                        if (btn === 'ok') {
                                        }
                                    }
                                });
                            }
                        }
                        else {
                            // Error restarting the request job.
                            if (request.status.toLowerCase() == 'error') {
                                Ext.Msg.show({
                                    title: esapp.Utils.getTranslation('internet_proxy_error_title'),
                                    message: esapp.Utils.getTranslation('internet_proxy_error_msg'),
                                    buttons: Ext.Msg.OK,
                                    icon: Ext.Msg.WARNING,
                                    fn: function (btn) {
                                        if (btn === 'ok') {
                                            // todo: go to system tab?
                                        }
                                    }
                                });
                            }
                            else {
                                Ext.Msg.show({
                                    title: esapp.Utils.getTranslation('error_restarting_request'),
                                    message: request.message,
                                    buttons: Ext.Msg.OK,
                                    icon: Ext.Msg.WARNING,
                                    fn: function (btn) {
                                        if (btn === 'ok') {
                                        }
                                    }
                                });
                            }
                        }
                    }
                }
            },
            success: function ( result, request ) {},
            failure: function ( result, request) {}
        });
    }

    ,deleteRequest: function(grid, rowIndex, row){
        var me = this.getView();
        var record = grid.getStore().getAt(rowIndex);
        var params = {
                'requestid': record.get('requestid')
            };
        var msg = esapp.Utils.getTranslation('deleting_request') + ' ' + record.get('requestid');

        me.myMask = new Ext.LoadMask({
            msg    : msg,
            target : grid,
            border : false,
            frame : false,
            shadow : false,
            shim : true
        });

        me.myMask.show();

        Ext.Ajax.request({
            method: 'GET',
            url:'datamanagement/deleterequestjob',
            params: params,
            loadMask: esapp.Utils.getTranslation('loading'),    // 'Loading...',
            callback:function(callinfo,responseOK,response ){
                var request = Ext.JSON.decode(response.responseText);
                // request = request.request;
                // console.info(me);
                me.myMask.hide();

                if (Ext.isObject(request)) {
                    if (request.success) {
                        me.dirtyStore = true;
                        me.fireEvent('loadstore');
                        // grid.getStore().remove(record);
                    }
                    else {
                        Ext.Msg.show({
                            title: esapp.Utils.getTranslation('error_deleting_request'),
                            message: request.message,
                            buttons: Ext.Msg.OK,
                            icon: Ext.Msg.WARNING,
                            fn: function (btn) {
                                if (btn === 'ok') {
                                }
                            }
                        });
                    }
                }
            },
            success: function ( result, request ) {},
            failure: function ( result, request) {}
        });
    }
});
