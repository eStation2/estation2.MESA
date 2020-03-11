Ext.define('esapp.view.analysis.addEditLayerController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-addeditlayer'

    ,setup: function() {
        var me = this.getView();

        //if (me.params.edit){
            Ext.getCmp('layername').setValue(me.params.layerrecord.get('layername'));
            Ext.getCmp('layerdescription').setValue(me.params.layerrecord.get('description'));
            Ext.getCmp('layer_filename').setValue(me.params.layerrecord.get('filename'));
            Ext.getCmp('feature_display_column').setValue(me.params.layerrecord.get('feature_display_column'));

            Ext.getCmp('provider').setValue(me.params.layerrecord.get('provider'));
            Ext.getCmp('layertype').setValue(me.params.layerrecord.get('layertype'));
            Ext.getCmp('layerorderidx').setValue(me.params.layerrecord.get('layerorderidx'));
            Ext.getCmp('layermenu').setValue(me.params.layerrecord.get('menu'));
            Ext.getCmp('layersubmenu').setValue(me.params.layerrecord.get('submenu'));
            Ext.getCmp('layerenabled').setValue(me.params.layerrecord.get('enabled'));
            Ext.getCmp('open_in_mapview').setValue(me.params.layerrecord.get('open_in_mapview'));
        //}
    }

    ,saveLayerInfo: function(){

        var me = this.getView(),
            form = this.lookupReference('layersform'),
            layerstore = Ext.data.StoreManager.lookup('LayersStore');

        if (form.isValid()) {
            layerstore.suspendAutoSync();
            me.params.layerrecord.set('layername', Ext.getCmp('layername').getValue());
            me.params.layerrecord.set('description', Ext.getCmp('layerdescription').getValue());
            me.params.layerrecord.set('filename',  Ext.getCmp('layer_filename').getValue());
            me.params.layerrecord.set('feature_display_column',  Ext.getCmp('feature_display_column').getValue());

            me.params.layerrecord.set('provider',  Ext.getCmp('provider').getValue());
            me.params.layerrecord.set('layertype',  Ext.getCmp('layertype').getValue());
            me.params.layerrecord.set('layerorderidx',  Ext.getCmp('layerorderidx').getValue());
            me.params.layerrecord.set('menu',  Ext.getCmp('layermenu').getValue());
            me.params.layerrecord.set('submenu',  Ext.getCmp('layersubmenu').getValue());
            me.params.layerrecord.set('enabled',  Ext.getCmp('layerenabled').getValue());
            me.params.layerrecord.set('open_in_mapview',  Ext.getCmp('open_in_mapview').getValue());

            if (!me.edit){
                layerstore.insert(0, me.params.layerrecord);
            }
            layerstore.resumeAutoSync(true);

            //if (!me.params.edit){
            //    Ext.getCmp('layeradministration').toFront();
                Ext.toast({html: esapp.Utils.getTranslation('layer_settings_saved'), title: esapp.Utils.getTranslation('saved'), width: 200, align: 't'});
                // Ext.getCmp('layeradministration').getController().loadLayersStore();
                Ext.destroy(me);
            //}
        }
    }

    ,selectLayer: function(){

        var layerfilesStore = this.getStore('serverlayerfiles');

        var gp = new Ext.grid.Panel({
            xtype : 'grid',
            reference: 'selectlayerGrid',
            width: 650,
            height:700,
            store: layerfilesStore,

            viewConfig: {
                stripeRows: false,
                enableTextSelection: true,
                draggable:false,
                markDirty: false,
                resizable:false,
                disableSelection: false,
                trackOver:true
            },

            selModel : {
                allowDeselect : false,
                mode:'SINGLE'
            },

            collapsible: false,
            enableColumnMove:false,
            enableColumnResize:false,
            multiColumnSort: false,
            columnLines: false,
            rowLines: true,
            frame: false,
            border: false,
            bodyBorder: false,

            listeners: {
                rowdblclick: function(gridview, record){
                    Ext.getCmp('layer_filename').setValue(record.get('layerfilename'));
                    selectLayerFileWin.close();
                }
            },
            columns: [{
                text: esapp.Utils.getTranslation('layerfile'),   // "Layer file name",
                width: 400,
                sortable: false,
                hideable: false,
                variableRowHeight: true,
                menuDisabled: true,
                //bind: '{serverlayerfilesChained.layerfilename}'
                dataIndex: 'layerfilename'
            },{
                text: esapp.Utils.getTranslation('filesize'),   // "File size",
                width: 200,
                sortable: false,
                hideable: false,
                variableRowHeight: true,
                menuDisabled: true,
                //bind: '{serverlayerfilesChained.filesize}'
                dataIndex: 'filesize'
            }],
            buttons: [{
                text: esapp.Utils.getTranslation('selectlayer'), // 'Select',
                handler: function(){
                    if (gp.getSelectionModel().selected.items.length == 1){
                        Ext.getCmp('layer_filename').setValue(gp.getSelectionModel().selected.items[0].get('layerfilename'));
                        selectLayerFileWin.close();
                    }
                    else {
                        Ext.toast({html: esapp.Utils.getTranslation('pleaseselectlayerfile'), title: esapp.Utils.getTranslation('warning'), width: 200, align: 't'});
                    }
                }
            },{
                text: esapp.Utils.getTranslation('close'), // 'Close',
                handler: function(){
                    selectLayerFileWin.close();
                }
            }]
        });

        var selectLayerFileWin = new Ext.Window({
             id:'selectlayerfile-win'
            ,layout:'fit'
            ,autoWidth: true
            ,plain: true
            ,modal:true
            ,stateful :false
            ,closable:true
            ,loadMask:true
            ,title:esapp.Utils.getTranslation('selectlayerfile') // 'Select a layer file present on the server.'
            ,items:gp
        });

        selectLayerFileWin.show();
    }

    ,importLayer:function() {

        var fileUploadWin = new Ext.Window({
             id:'fileupload-win'
            ,layout:'fit'
            ,autoWidth: true
            ,plain: true
            ,modal:true
            ,stateful :false
            ,closable:true
            ,loadMask:true
            ,title:esapp.Utils.getTranslation('importlayer') // 'Import layer'
            ,items:[{
                xtype: 'form',
                fileUpload: true,
                width: 400,
                frame: false,
                title: '',
                autoHeight: true,
                bodyStyle: 'padding: 10px 10px 10px 10px;',
                defaults: {
                    anchor: '90%',
                    allowBlank: false,
                    msgTarget: 'side'
                },
                columnCount:1,
                labelAlign :'top',
                items: [{
                     xtype: 'hidden'
                    ,name:'layerfilename'
                    ,id:'layerfilename'
                    ,value: ''
                },{
                    xtype: 'filefield'
                    ,id: 'layerfile'
                    ,name: 'layerfile'
                    ,emptyText: esapp.Utils.getTranslation('select_geojson file') // 'Select a .geojson file'
                    //,fieldLabel: esapp.Utils.getTranslation('import_layer_geojson_file') // 'Layer .geojson file'
                    ,width: 200
                    ,vtype:'GeoJSON'
                    //,labelWidth: 150
                    ,msgTarget: 'side'
                    ,allowBlank: false
                    ,anchor: '100%'
                    ,buttonText: ''
                    ,buttonConfig: {
                        iconCls: 'fa fa-folder-open-o'
                    }
                }],
                buttons: [{
                    text: esapp.Utils.getTranslation('btn_import'), // 'Import',
                    handler: function(){
                        if(this.up().up().getForm().isValid()){
                            Ext.getCmp('layerfilename').setValue(Ext.getCmp('layerfile').lastValue);
                            this.up().up().getForm().submit({
                                url:'layers/import',
                                //scope:this,
                                waitMsg: esapp.Utils.getTranslation('msg_wait_importing_layer'), // 'Importing layer...',
                                success: function(fp, o, x){
                                    var tpl = new Ext.XTemplate(
                                        esapp.Utils.getTranslation('layer_file_saved_on_the_server')+'<br />',
                                        esapp.Utils.getTranslation('name') + ': {filename}<br />'
                                    );
                                    Ext.Msg.alert('Success', tpl.apply(o.result));

                                    Ext.getCmp('layer_filename').setValue(o.result.filename);

                                    fileUploadWin.close();
                                }
                            });
                        }
                        else {
                            Ext.Msg.alert(esapp.Utils.getTranslation('warning'), esapp.Utils.getTranslation('vtype_geojson'));
                        }
                    }
                },{
                    text: esapp.Utils.getTranslation('btn_txt_reset'), // 'Reset',
                    handler: function(){
                        this.up().up().getForm().reset();
                    }
                },{
                    text: esapp.Utils.getTranslation('close'), // 'Close',
                    handler: function(){
                        fileUploadWin.close();
                    }
                }
                ]
            }]
        });

        fileUploadWin.show();
    }

    ,createTooltip: function (view) {
    //    console.info(view);

        if (!esapp.Utils.objectExists(view.tip)){
            view.tip = new Ext.ToolTip({
                // The overall target element.
                target: view.el,
                // Each grid row causes its own seperate show and hide.
                delegate: view.rowSelector, // view.itemSelector, //
                // Moving within the row should not hide the tip.
                trackMouse: true,
                // Render immediately so that tip.body can be referenced prior to the first show.
                renderTo: Ext.getBody(),
                listeners: {
                    // Change content dynamically depending on which element triggered the show.
                    beforeshow: function (tip) {
                        var tooltip = view.grid.getStore().getAt(view.findRowIndex(tip.triggerElement)).get('tooltip');
                        if(tooltip){
                            tip.update(tooltip);
                        } else {
                             tip.on('show', function(){
                                 Ext.defer(tip.hide, 10, tip);
                             }, tip, {single: true});
                        }
                    }
                }
            });
        }
    }

//     ,awesomeUploadLayer:function() {
//
//         var statusIconRenderer = function(value){
//        		switch(value){
//        			default:
//        				return value;
//        			case 'Pending':
//        				return '<img src="resources/img/hourglass.png" width=16 height=16>';
//        			case 'Sending':
//        				return '<img src="resources/img/loading.gif" width=16 height=16>';
//        			case 'Error':
//        				return '<img src="resources/img/cross.png" width=16 height=16>';
//        			case 'Cancelled':
//        			case 'Aborted':
//        				return '<img src="resources/img/cancel.png" width=16 height=16>';
//        			case 'Uploaded':
//        				return '<img src="resources/img/tick.png" width=16 height=16>';
//        		}
//        	},
//
//        	progressBarColumnTemplate = new Ext.XTemplate(
//        		'<div class="ux-progress-cell-inner ux-progress-cell-inner-center ux-progress-cell-foreground">',
//        			'<div>{value} %</div>',
//        		'</div>',
//        		'<div class="ux-progress-cell-inner ux-progress-cell-inner-center ux-progress-cell-background" style="left:{value}%">',
//        			'<div style="left:-{value}%">{value} %</div>',
//        		'</div>'
//            ),
//
//        	progressBarColumnRenderer = function(value, meta, record, rowIndex, colIndex, store){
//             meta.css += ' x-grid3-td-progress-cell';
//        		return progressBarColumnTemplate.apply({
//        			value: value
//        		});
//        	},
//
//        	updateFileUploadRecord = function(id, column, value){
//        		var rec = fileUploadPanel.awesomeUploaderGrid.store.getById(id);
//        		rec.set(column, value);
//        		rec.commit();
//        	};
//
//
//         function getFileExtension(filename){
//             var result = null;
//             var parts = filename.split('.');
//             if (parts.length > 1) {
//                 result = parts.pop();
//             }
//             return result;
//         }
//
//         function isPermittedFileType(filename){
//             var result = true;
//             if (this.permitted_extensions.length > 0) {
//                 result = this.permitted_extensions.indexOf(this.getFileExtension(filename)) != -1;
//             }
//             return result;
//         }
//
//
//        	var fileUploadPanel = new Ext.Panel({
//        		title:''
//             ,id:'fileUploadPanel'
//        		,frame:true
//        		,width:520
//        		,autoHeight:true
//        		,items:[{
//        			xtype:'grid'
//        			,ref:'awesomeUploaderGrid'
//                 ,id:'awesomeUploaderGrid'
//                 ,layout:'fit'
//        			,height:230
//        			,enableHdMenu:false
//        			,tbar:[
//                     AwesomeUploaderInstance,
//                     "->",
//                     {
//                         text:esapp.Utils.getTranslation('btn_txt_start_upload') // 'Start Upload'
//                         ,id:'btn-startupload'
//                         ,disabled:true
//                         ,icon:'resources/img/tick.png'
//                         ,scope:this
//                         ,handler:function(){
//                             AwesomeUploaderInstance.startUpload();
//                         }
//                     },{
//                         text:esapp.Utils.getTranslation('btn_txt_abort') // 'Abort'
//                         ,id:'btn-abort'
//                         ,disabled:true
//                         ,icon:'resources/img/cancel.png'
//                         ,scope:this
//                         ,handler:function(){
//                             var selModel = fileUploadPanel.awesomeUploaderGrid.getSelectionModel();
//                             if(!selModel.hasSelection()){
//                                 Ext.Msg.alert('',esapp.Utils.getTranslation('Msg_txt_select_upload_to_cancel')); // 'Please select an upload to cancel'
//                                 return true;
//                             }
//                             var rec = selModel.getSelected();
//                             AwesomeUploaderInstance.abortUpload(rec.data.id);
//                         }
//                     },{
//                         text:esapp.Utils.getTranslation('btn_txt_abort_all') // 'Abort All'
//                         ,id:'btn-abortall'
//                         ,disabled:true
//                         ,icon:'resources/img/cancel.png'
//                         ,scope:this
//                         ,handler:function(){
//                            AwesomeUploaderInstance.abortAllUploads();
//                         }
//                     },{
//                         text:esapp.Utils.getTranslation('btn_txt_remove') // 'Remove'
//                         ,id:'btn-remove'
//                         ,disabled:true
//                         ,icon:'resources/img/cross.png'
//                         ,scope:this
//                         ,handler:function(){
//                             var selModel = fileUploadPanel.awesomeUploaderGrid.getSelectionModel();
//                             if(!selModel.hasSelection()){
//                                 Ext.Msg.alert('',esapp.Utils.getTranslation('Msg_txt_select_upload_to_cancel')); // 'Please select an upload to cancel'
//                                 return true;
//                             }
//                             var rec = selModel.getSelected();
//                             AwesomeUploaderInstance.removeUpload(rec.data.id);
//                         }
//                     },{
//                         text:esapp.Utils.getTranslation('btn_txt_remove_all') // 'Remove All'
//                         ,id:'btn-removeall'
//                         ,disabled:true
//                         ,icon:'resources/img/cross.png'
//                         ,scope:this
//                         ,handler:function(){
//                            AwesomeUploaderInstance.removeAllUploads();
//                         }
//        			}]
//                 ,bbar: new Ext.ux.StatusBar({
//                            id: 'win-statusbar',
//                            defaultText: '',
//                            items: [{
//                                id:'btn-useforlayer',
//                                text: esapp.Utils.getTranslation('btn_txt_useforlayer'), // 'Use for layer',
//                                disabled:true,
//                                scope:this,
//                                handler:function(){
//                                    Ext.getCmp('filename').setValue(AwesomeUploaderInstance.layerfile);
//                                    AwesomeUploaderWindow.close();
//                                }
//                            }]
//                        })
//        			,store:new Ext.data.JsonStore({
//        				fields: ['id','name','size','status','progress','tooltip']
//            			,idProperty: 'id'
//        			})
//                 ,viewConfig: {
//                     listeners: {
//                         render: this.createTooltip
//                     }
//                 }
//        			,columns:[
//        				 {header:esapp.Utils.getTranslation('gridcolheader_filename'),dataIndex:'name', width:200} // 'File Name'
//        				,{header:esapp.Utils.getTranslation('gridcolheader_size'),dataIndex:'size', width:60, renderer:Ext.util.Format.fileSize} // 'Size'
//        				,{header:'&nbsp;',dataIndex:'status', width:30, renderer:statusIconRenderer}
//        				,{header: esapp.Utils.getTranslation('gridcolheader_status'),dataIndex:'status', width:60} // 'Status'
//        				,{header:esapp.Utils.getTranslation('gridcolheader_progress'),dataIndex:'progress', width:130, renderer:progressBarColumnRenderer} // 'Progress'
//        			]
// //               },{
// //                xtype:'box'
// //                ,id:'SWFUpload_ConsoleBox'
//        		}]
//        	});
//
//
//         var AwesomeUploaderInstance = new Ext.ux.AwesomeUploader({
//             xtype:'awesomeuploader'
//             ,awesomeUploaderRoot:'../lib/Ext.ux/AwesomeUploader/'
//             ,id:'awesomeUploader'
//             ,ref:'awesomeUploader'
//             ,extraPostData:{
//                 'key':'value'
//                 ,'test':'testvalue'
//             }
//             ,method:'swfupload' // 'standard' 'swfupload'
//             ,flashSwfUploadFileTypes:'*.geojson, *.tif;*.shp;*.shx;*.dbf;*.prj;*.sbn;*.sbx;*.fbn;*.fbx;*.ain;*.aih;*.ixs;*.mxs;*.atx;*.shp*.xml;*.cpg'
//             ,allowDragAndDropAnywhere:true
//             ,autoStartUpload:false
//             ,maxFileSizeBytes: 250 * 1024 * 1024 // 250 MiB
//             ,uploadedFiles:0
//             ,layertype:'' // 'vector'  'raster'
//             ,layerfile:''
//             ,listeners:{
//                 scope:this
//                 ,fileselected:function(awesomeUploader, file){
// //                    console.info(file);
//                   /*
//                       file will at minimum be:
//                       file = {
//                           name: fileName
//                           ,method: "swfupload" //(can be "swfupload", "standard", "dnd"
//                           ,id: 1 // a unique identifier to abort or remove an individual file, incrementing int
//                           ,status: "queued" // file status. will always be queued at this point
//                           // if swfupload or dnd or standard upload on a modern browser (supports the FILE API) is used, size property will be set:
//                           ,size: 12345 // file size in bytes
//                       }
//                   */
//                     Ext.getCmp('btn-startupload').enable();
//                     Ext.getCmp('btn-remove').enable();
//                     Ext.getCmp('btn-removeall').enable();
//
//                     // Example of cancelling a file to be selection
//                     if( file.name == 'image.jpg' ){
//                         Ext.Msg.alert('Error','You cannot upload a file named "image.jpg"');
//                         return false;
//                     }
//
//                     fileUploadPanel.awesomeUploaderGrid.store.loadData({
//                         id:file.id
//                         ,name:file.name
//                         ,size:file.size
//                         ,status:'Pending'
//                         ,progress:0
//                         ,tooltip:'Pending'
//                     }, true);
//
//                     this.createTooltip(fileUploadPanel.awesomeUploaderGrid.getView());
//
//                 }
//                 ,uploadstart:function(awesomeUploader, file){
//
//                     updateFileUploadRecord(file.id, 'status', 'Sending');
//                     Ext.getCmp('btn-abort').enable();
//                     Ext.getCmp('btn-abortall').enable();
//
//                     var statusBar = Ext.getCmp('win-statusbar');
//                     statusBar.showBusy();
//                 }
//                 ,uploadprogress:function(awesomeUploader, fileId, bytesComplete, bytesTotal){
//
//                     updateFileUploadRecord(fileId, 'progress', Math.round((bytesComplete / bytesTotal)*100) );
//                 }
//                 ,uploadcomplete:function(awesomeUploader, file, serverData, resultObject){
// //                    Ext.Msg.alert('Data returned from server'+ serverData);
//
//                     try{
//                         var result = Ext.util.JSON.decode(serverData); //throws a SyntaxError.
//                     }catch(e){
//                         resultObject.error = 'Invalid JSON data returned';
//                         //Invalid json data. Return false here and "uploaderror" event will be called for this file. Show error message there.
//                         return false;
//                     }
//                     resultObject = result;
//
//                     if(result.success){
//                         updateFileUploadRecord(file.id, 'progress', 100 );
//                         updateFileUploadRecord(file.id, 'status', 'Uploaded' );
//                         updateFileUploadRecord(file.id, 'tooltip', 'Uploaded' );
//
//                         awesomeUploader.uploadedFiles=awesomeUploader.uploadedFiles+1;
// //                        console.info('uploaded: '+awesomeUploader.uploadedFiles);
// //                        console.info('store size: '+fileUploadPanel.awesomeUploaderGrid.store.getCount());
//
//                         var statusBar = Ext.getCmp('win-statusbar');
//                         var fileExtension = getFileExtension(file.name);
//
//                         if (fileExtension=='shp'){
//                             awesomeUploader.layertype='vector';
//                             awesomeUploader.layerfile='/static_data/uploads/'+file.name
//                         }
//                         else if (fileExtension=='tif'){
//                             awesomeUploader.layertype='raster';
//                             awesomeUploader.layerfile='/static_data/uploads/'+file.name
//                         }
//                         else if (fileExtension=='jpg' || fileExtension=='png' || fileExtension=='gif'){
//                             awesomeUploader.layertype='image';
//                             awesomeUploader.layerfile='/static_data/uploads/'+file.name
//                         }
//                         else{
//                             statusBar.clearStatus({useDefaults:true});
//                         }
//
//                         if (fileUploadPanel.awesomeUploaderGrid.store.getCount()==awesomeUploader.uploadedFiles && awesomeUploader.layertype!=''){
//                             awesomeUploader.uploadedFiles=0;
//                             var statustext='';
//                             if (awesomeUploader.layertype=='vector'){
//                                 statustext = 'Vector layer: '+awesomeUploader.layerfile;
//                             }
//                             else if (awesomeUploader.layertype=='raster'){
//                                 statustext = 'Raster layer: '+awesomeUploader.layerfile;
//                             }
//                             else if (awesomeUploader.layertype=='image'){
//                                 statustext = 'Image layer: '+awesomeUploader.layerfile;
//                             }
//                             statusBar.setStatus({
//                                 text: statustext
//                             });
//                             Ext.getCmp('btn-useforlayer').enable();
//                         }
//
//                     }else{
//                         return false;
//                     }
//
//                 }
//                 ,uploadaborted:function(awesomeUploader, file ){
//                     updateFileUploadRecord(file.id, 'status', 'Aborted' );
//                 }
//                 ,uploadremoved:function(awesomeUploader, file ){
//
//                     fileUploadPanel.awesomeUploaderGrid.store.remove(fileUploadPanel.awesomeUploaderGrid.store.getById(file.id) );
//                     if(fileUploadPanel.awesomeUploaderGrid.store.getCount()==0){
//                         Ext.getCmp('btn-startupload').disable();
//                         Ext.getCmp('btn-abort').disable();
//                         Ext.getCmp('btn-abortall').disable();
//                         Ext.getCmp('btn-remove').disable();
//                         Ext.getCmp('btn-removeall').disable();
//                     }
//                 }
//                 ,uploaderror:function(awesomeUploader, file, serverData, resultObject){
// //                    Ext.Msg.alert('Error data returned from server: '+ serverData);
//                     try{
//                         var result = Ext.util.JSON.decode(serverData); //throws a SyntaxError.
//                     }catch(e){
//                         resultObject.error = 'Invalid JSON data returned';
//                         //Invalid json data. Return false here and "uploaderror" event will be called for this file. Show error message there.
//                         return false;
//                     }
//                     resultObject = resultObject || {};
//
//                     var error = 'Error! ';
//                     if(resultObject.error){
//                         error += resultObject.error;
//                     }
//
//                     updateFileUploadRecord(file.id, 'progress', 0 );
//                     updateFileUploadRecord(file.id, 'status', 'Error');
//                     updateFileUploadRecord(file.id, 'tooltip', 'Error: '+ result.error );
//
//                     var statusBar = Ext.getCmp('win-statusbar');
//                     statusBar.clearStatus({useDefaults:true});
//                 }
//             }
//        	});
//
//
//         var AwesomeUploaderWindow = new Ext.Window({
//        		title:esapp.Utils.getTranslation('title_multiple_file_upload_win') // 'Upload layer file(s)'
//        		,closeAction:'close'
//        		,frame:true
//             ,layout:'fit'
//             ,modal: true
//        		,items:fileUploadPanel
//         });
//
//         AwesomeUploaderWindow.show();
//
//     }
});
