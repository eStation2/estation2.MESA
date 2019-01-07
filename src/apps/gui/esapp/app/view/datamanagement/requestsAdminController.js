Ext.define('esapp.view.datamanagement.requestsAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.datamanagement-requestsadmin'


    ,runPauseRequest: function(grid, rowIndex, row){
        var record = grid.getStore().getAt(rowIndex);
        var params = {};
        var status = record.get('status');

        if (record.get('status')=='running'){
            params = {
                'requestid': record.get('requestid'),
                'task': 'pause'
            };
            status = 'paused';
        }
        else if (record.get('status')=='paused'){
            params = {
                'requestid': record.get('requestid'),
                'task': 'run'
            };
            status = 'running';
        }

        Ext.Ajax.request({
            method: 'GET',
            url:'datamanagement/runpauserequest',
            params: params,
            loadMask: esapp.Utils.getTranslation('loading'),    // 'Loading...',
            callback:function(callinfo,responseOK,response ){
                var request = Ext.JSON.decode(response.responseText.trim());
                request = request.request;
                // ToDO: error handling when success is false
                record.set('status', status);
            },
            success: function ( result, request ) {},
            failure: function ( result, request) {}
        });
    }

    ,deleteRequest: function(grid, rowIndex, row){
        var record = grid.getStore().getAt(rowIndex);
        var params = {
                'requestid': record.get('requestid')
            };

        Ext.Ajax.request({
            method: 'GET',
            url:'datamanagement/deleterequestjob',
            params: params,
            loadMask: esapp.Utils.getTranslation('loading'),    // 'Loading...',
            callback:function(callinfo,responseOK,response ){
                var request = Ext.JSON.decode(response.responseText.trim());
                request = request.request;
                // ToDO: error handling when success is false
                grid.getStore().remove(record);
            },
            success: function ( result, request ) {},
            failure: function ( result, request) {}
        });
    }
});
