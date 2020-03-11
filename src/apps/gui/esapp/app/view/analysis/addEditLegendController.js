Ext.define('esapp.view.analysis.addEditLegendController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-addeditlegend'

    ,validateClasses: function(){
        var me = this.getView();
        var legendClassesStore = me.getViewModel().getStore('legendClassesStore');

        legendClassesStore.sort('from_step', 'asc');

        var previousFromStep;
        var previousToStep;
        var overlap = false;
        var doubles = false;
        legendClassesStore.each( function (record){
            if (parseFloat(record.data.from_step) < parseFloat(previousToStep)) {
                overlap = true;
            }
            if (parseFloat(record.data.from_step) == parseFloat(previousFromStep) && parseFloat(record.data.to_step) == parseFloat(previousToStep)){
                doubles = true;
            }
            previousFromStep = record.data.from_step;
            previousToStep = record.data.to_step;
        });
        if (!overlap && !doubles){
            return true;
        }
        else return false;
    }

    ,saveLegend: function(){
        var me = this.getView(),
            // legendform = me.lookupReference('legendform'),
            legendid = me.params.legendrecord.get('legendid'),
            legenddescriptivename = me.lookupReference('legenddescriptivename'),
            title_in_legend = me.lookupReference('title_in_legend'),
            legendminvalue = me.lookupReference('legend_minvalue'),
            legendmaxvalue = me.lookupReference('legend_maxvalue'),
            defined_by = me.lookupReference('defined_by_field'),
            legendClassesStore = me.getViewModel().getStore('legendClassesStore');

        if (!legenddescriptivename.validate() || !title_in_legend.validate() || !legendminvalue.validate() || !legendmaxvalue.validate()) {
            return;
        }

        if (this.validateClasses()){

            Ext.Msg.show({
                title: esapp.Utils.getTranslation('savelegendquestion'),     // 'Save legend',
                message: esapp.Utils.getTranslation('savelegendquestion') + ' "' + legenddescriptivename.getValue() + '"?',
                buttons: Ext.Msg.OKCANCEL,
                icon: Ext.Msg.QUESTION,
                fn: function(btn) {
                    if (btn === 'ok') {
                        Ext.Ajax.request({
                           url: 'legends/savelegend',
                           params:{
                               legend_descriptive_name: legenddescriptivename.getValue(),
                               title_in_legend: title_in_legend.getValue(),
                               legendid: legendid,
                               minvalue: legendminvalue.getValue(),
                               maxvalue: legendmaxvalue.getValue(),
                               defined_by: defined_by.getValue(),
                               legend_type: me.legend_type,
                               legendClasses:esapp.Utils.makeGridJSON(legendClassesStore)
                           },
                           method: 'POST',
                           waitMsg:esapp.Utils.getTranslation('savinglegend'), // 'Saving legend...',
                           scope:this,
                           success: function(result, request) {
                               // The success handler is called if the XHR request actually
                               // made it to the server and a response of some kind occurs.
                               var returnData = Ext.util.JSON.decode(result.responseText);
                               // console.info(returnData);
                               if (returnData.success){
                                    me.params.legendrecord.set('legendid', returnData.legendid);
                                    me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editlegend') + '</span>');
                                    // legendclasses.onLoadClick(this.legendid);
                                    // var legendlist = Ext.getCmp('legendslist');
                                    // legendlist.store.load();
                                    Ext.Msg.show({
                                        title:esapp.Utils.getTranslation('legend_saved'), // 'Legend saved',
                                        msg:esapp.Utils.getTranslation('legend_saved'), // 'Legend saved successfully',
                                        modal:true,
                                        icon:Ext.Msg.INFO,
                                        buttons:Ext.Msg.OK
                                    });

                                    me.changedsaved = true;
                               } else{
                                   esapp.Utils.showError(returnData.error || result.responseText);
                               }
                           }, // eo function onSuccess
                           failure: function(result, request) {
                               // The failure handler is called if there's some sort of network error,
                               // like you've unplugged your ethernet cable, the server is down, etc.
                           }, // eo function onFailure
                           callback:function(callinfo,responseOK,response ){
                               //refresh legend list
                           }
                        });
                    }
                }
            });

        }
        else {
            Ext.Msg.show({
                title:esapp.Utils.getTranslation('warning'), // 'Warning!',
                msg:esapp.Utils.getTranslation('check_legend_classes'), // 'Legend not saved! Check classes double values or overlaps!',
                modal:true,
                icon:Ext.Msg.ERROR,
                buttons:Ext.Msg.OK
            });
        }
    }

    ,newClass: function(){
        var me = this.getView();
        var legendClassesStore = me.getViewModel().getStore('legendClassesStore');
        var lastrecordID = -1;

        var defaultData = {
            legend_id: me.params.legendrecord.get('legendid'),
            from_step: null,
            to_step: null,
            color_rgb: '255 255 255',
            color_label:'',
            group_label:''
        };
        var newrecord = new esapp.model.LegendClasses(defaultData);
        newrecord.dirty = false;
        legendClassesStore.add(newrecord);
        // if (legendClassesStore.data.length > 0) {   // Better if a method exists to insert as last
        //     lastrecordID = legendClassesStore.last().id;
        // }
        // newrecord.set('id', lastrecordID-1);
        // legendClassesStore.insert(lastrecordID-1, newrecord);
        // me.lookupReference('legendclassesGrid').startEditing(legendClassesStore.indexOf(newrecord), 1);
    }

    ,deleteAllClasses: function(){
        var me = this.getView();
        var legendClassesStore = me.getViewModel().getStore('legendClassesStore');
        legendClassesStore.removeAll();
    }

    ,openColourPicker: function(record, el){
        var me = this.getView();
        // var colourPickerWin = Ext.getCmp('colourPickerWin');
        // if (colourPickerWin==null || colourPickerWin=='undefined' ) {

        var colourPickerWin = Ext.create('Ext.window.Window', {
             // id:'colourPickerWin'
            // reference:'colourPickerWin'
            // ,referenceHolder: true
             layout:'fit'
            ,hidden:false
            ,autoShow: true
            ,autoHeight: true
            ,autoWidth: true
            ,resizable:false
            ,plain: true
            ,stateful :false
            ,closable:true
            // ,loadMask:true
            // ,title:esapp.Utils.getTranslation('colourpicker') // 'Colour picker'
            ,closeAction:'destroy'
            ,modal:true
            ,deferredRender:false
            ,frame: false
            ,border: false
            ,collapsible:false
            ,bodyStyle: 'padding: 10px 3px 0px 3px;'
            ,bbar: {
                padding: 4,
                defaults: {
                    scale: 'medium',
                    hidden: false
                },
                items: ['->', {
                    xtype: 'button',
                    text: esapp.Utils.getTranslation('ok'),    // 'Ok',
                    handler: function(){
                        // console.info(this.up().up().down('colorselector'));
                        var hexvalue = this.up().up().down('colorselector').getValue();
                        var rgbvalue = esapp.Utils.HexToRGB(hexvalue);
                        rgbvalue = rgbvalue.replace(/,/g, ' ');
                        record.set('color_rgb', rgbvalue);

                        me.getController().setLegendPreview();
                        colourPickerWin.close();
                    }
                }]
            }
            ,items: [{
                xtype: 'colorselector',
                scope:this,
                border: false,
                frame: false,
                format: "#HEX6",
                value: esapp.Utils.convertRGBtoHex(record.get('color_rgb')),
                listeners: {
                    change: function(colorbtn, hexvalue) {
                        // var rgbvalue = esapp.Utils.HexToRGB(hexvalue);
                        // rgbvalue = rgbvalue.replace(/,/g, ' ');
                        // record.set('color_rgb', rgbvalue);
                    }
                }
            }]
        });
        // }
        // colourPickerWin.show();
        colourPickerWin.alignTo(el,"l-r", [-6, 0]);
    }

    ,generateClasses: function(){
        var me = this.getView();
        var legendClassesStore = me.getViewModel().getStore('legendClassesStore');
        // var legendClassesTmp = this;

        function setBackgroundColor (field) {
            var value = field.getValue();
            var arr = [];
            if (esapp.Utils.is_array(value)){
                arr = value;
            }
            else {
                arr = value.split(" "); // toString().replace(/,/g,' ');
            }

            var R = arr[0];
            var G = arr[1];
            var B = arr[2];
            var rgbValue = esapp.Utils.RGBtoHex(R,G,B);
            var Rinverse = (R ^ 128);
            var Ginverse = (G ^ 128);
            var Binverse = (B ^ 128);

            var fontcolor = esapp.Utils.RGBtoHex( Rinverse, Ginverse, Binverse);
            // console.info(field);
            field.setStyle('background-color: '+rgbValue+';'+'color: '+fontcolor+';');
            // var styleSheetID = field.id+"_mystylesheet";
            // Ext.util.CSS.removeStyleSheet(styleSheetID);
            // var className = field.id+"_textfieldColors";
            // var newClass = " ."+className+" {background:"+rgbValue+"; color: "+fontcolor+";}";
            // Ext.util.CSS.createStyleSheet(newClass,styleSheetID);
            // field.addClass(className);

        }

        var generateClassesWin = Ext.getCmp('generateClassesWin');
        if (generateClassesWin==null || generateClassesWin=='undefined' ) {

            generateClassesWin = Ext.create('Ext.window.Window', {
                 id:'generateClassesWin'
                ,reference:'generateClassesWin'
                ,referenceHolder: true
                ,layout:'fit'
                ,hidden:true
                ,autoHeight: true
                ,width: 315
                ,resizable:false
                ,plain: true
                ,stateful :false
                ,closable:true
                ,loadMask:true
                ,title:esapp.Utils.getTranslation('win_title_generate_classes') // 'Generate classes using color interpolation'
                // ,items:generateClassesPanel
                ,closeAction:'hide'
                ,modal:true
                ,deferredRender:false
                ,frame: false
                ,border: true
                ,collapsible:false
                ,bodyStyle: 'padding: 15px 3px 0 3px;'
                ,defaults: {autoScroll:true}
                ,bbar: ['->',{
                    reference: 'GenerateClassesBtn',
                    text: esapp.Utils.getTranslation('generate'), // 'Generate'
                    iconCls:'fa fa-cogs',   // fa fa-cogs fa-2x
                    handler: function(){
                        function interpolateColor(rgbMin, rgbMax, maxDepth, depth){
                            if (depth <= 0){
                                return rgbMin.toString().replace(/,/g,' ');
                            }
                            if (depth >= maxDepth) {
                                return rgbMax.toString().replace(/,/g, ' ');
                            }
                            var rgb=rgbMin;
                           // rgb2=rgbMin;
                           // rgb3=rgbMin;
                            for (var iTriplet=0; iTriplet<3; iTriplet++){
                                var minVal=parseInt(rgbMin[iTriplet]);
                                var maxVal=parseInt(rgbMax[iTriplet]);
                                rgb[iTriplet] = parseInt(minVal + (maxVal-minVal)*(depth/parseFloat(maxDepth)));
                               // rgb2[iTriplet] = parseInt(minVal + (maxVal-minVal)*(depth/maxDepth));
                               // rgb3[iTriplet] = minVal + (maxVal-minVal)*(depth/maxDepth);
                            }
                            return rgb.toString().replace(/,/g,' ');
                        }


                        legendClassesStore.removeAll();

                        var generateClassesWindow = this.up().up();
                        var classes = generateClassesWindow.lookupReference('classes').getValue();
                        var startvalue = generateClassesWindow.lookupReference('startvalue').getValue();
                        var endvalue = generateClassesWindow.lookupReference('endvalue').getValue();
                        var startcolour = generateClassesWindow.lookupReference('startcolour').getValue();
                        var endcolour = generateClassesWindow.lookupReference('endcolour').getValue();
                        var setClasslabel = generateClassesWindow.lookupReference('ckb_apply_class_label').getValue();

                        var i=0;
                        var classlabel = '';
                        var colour = null;
                        var to = null;
                        var from = startvalue;
                        var precision = parseInt(4-Math.log10(endvalue-startvalue));
                        if (precision < 1) precision = 1;

                        var stepwidth = parseFloat((endvalue-startvalue)/classes);
                        while (i<=classes-1){
                            colour = interpolateColor(startcolour.split(" "), endcolour.split(" "), classes, i);
                            to = from+stepwidth

                            classlabel = from.toFixed(precision);
                            if(!setClasslabel){
                                classlabel = '';
                            }
                            var classData = {
                                legend_id: me.params.legendrecord.get('legendid'),
                                from_step: parseFloat(from.toFixed(precision)),
                                to_step: parseFloat(to.toFixed(precision)),
                                color_rgb: colour,
                                color_label: classlabel,
                                group_label:''
                            };

                            var newrecord = new esapp.model.LegendClasses(classData);
                            legendClassesStore.add(newrecord);
                            // var lastrecordID = -1;
                            // if (legendClassesStore.data.length > 0) {   // Better if a method exists to insert as last
                            //     lastrecordID = legendClassesStore.last().id-1;
                            // }
                            // newrecord.set('id', lastrecordID);
                            // legendClassesStore.insert(lastrecordID*-1, newrecord);

                            from=to;
                            i+=1;
                        }
                        me.getController().setLegendPreview();
                        generateClassesWindow.close();
                        // Ext.getCmp('preview').setValue(legendClassesTmp.getLegendPreview());
                    }
                }]
                ,items: [{
                    xtype: 'fieldset',
                    title: '',
                    labelWidth:90,
                    collapseable:false,
                    border:false,
                    margins:{top:15, right:5, bottom:0, left:5},
                    items:[{
                        xtype:'numberfield',
                        reference:'classes',
                        fieldLabel: esapp.Utils.getTranslation('classes'), // 'Classes',
                        width:90+90
                    },{
                        xtype:'numberfield',
                        reference:'startvalue',
                        fieldLabel: esapp.Utils.getTranslation('start_value'), // 'Start value',
                        width:90+90
                    },{
                        xtype:'numberfield',
                        reference:'endvalue',
                        fieldLabel: esapp.Utils.getTranslation('end_value'), // 'End value',
                        width:90+90
                    },{
                        xtype: 'container',
                        layout:'hbox',
                        layoutConfig: {
                            align:'left'
                        },
                        border:false,
                        defaults:{
                            disabled:false,  // items in hbox disabled on start!
                            margin: {
                                top: 0,
                                right: 5,
                                bottom: 5,
                                left: 0
                            },
                            cls:'x-form-item'
                        },
                        items: [{
                            xtype:'textfield',
                            id:'startcolour',
                            reference:'startcolour',
                            // renderer: setBackgroundColor,
                            fieldLabel: esapp.Utils.getTranslation('startcolour'), // 'Start colour',
                            regex: /(\d{1,3}) (\d{1,3}) (\d{1,3})/,
                            maskRe: /[0-9 ]+/,
                            invalidText: 'Not a valid RGB.  Must be 3 numbers between 0 and 255, devided by a space".',
                            listeners:{
                                change:function(field,value) {
                                    // setBackgroundColor(this);
                                    var arr = [];
                                    if (esapp.Utils.is_array(value)){
                                        arr = value;
                                    }
                                    else {
                                        arr = value.split(" "); // toString().replace(/,/g,' ');
                                    }

                                    var R = arr[0];
                                    var G = arr[1];
                                    var B = arr[2];
                                    var hexValue = esapp.Utils.RGBtoHex(R,G,B);

                                    if (esapp.Utils.objectExists(Ext.getCmp('startcolourpicker'))){
                                        Ext.getCmp('startcolourpicker').setValue(hexValue);
                                    }
                                }
                            },
                            width:120+90
                        },{
                            xtype: 'colorbutton',
                            id:'startcolourpicker',
                            reference:'startcolourpicker',
                            // text:'',
                            tooltip:esapp.Utils.getTranslation('opencolourpicker'), // 'Open colour picker',
                            // iconCls:'colorwheel',
                            // cls:'alignright',
                            scope:this,
                            width: 25,
                            height: 24,
                            border: true,
                            frame: false,
                            format: "#HEX6",
                            listeners: {
                                change: function(colorbtn, hexvalue) {
                                    // console.info(colorbtn);
                                    // console.info(hexvalue);
                                    var rgbvalue = esapp.Utils.HexToRGB(hexvalue);
                                    rgbvalue = rgbvalue.replace(/,/g, ' ');
                                    // console.info(rgbvalue);
                                    Ext.getCmp('startcolour').setValue(rgbvalue);
                                }
                            }
                            // handler:function() {
                            //     // showColorPicker(Ext.getCmp('startcolour'));
                            // }
                        }]
                    },{
                        xtype: 'container',
                        layout:'hbox',
                        layoutConfig: {
                            align:'left'
                        },
                        border:false,
                        defaults:{
                            disabled:false,  // items in hbox disabled on start!
                            margin: {
                                top: 0,
                                right: 5,
                                bottom: 5,
                                left: 0
                            },
                            cls:'x-form-item'
                        },
                        items: [{
                            xtype:'textfield',
                            id:'endcolour',
                            reference:'endcolour',
                            // renderer: setBackgroundColor,
                            fieldLabel: esapp.Utils.getTranslation('endcolour'), // 'End colour',
                            regex: /(\d{1,3}) (\d{1,3}) (\d{1,3})/,
                            maskRe: /[0-9 ]+/,
                            invalidText: 'Not a valid RGB.  Must be 3 numbers between 0 and 255, devided by a space".',
                            listeners:{
                                change: function(field,value) {
                                    // setBackgroundColor(this);
                                    var arr = [];
                                    if (esapp.Utils.is_array(value)){
                                        arr = value;
                                    }
                                    else {
                                        arr = value.split(" "); // toString().replace(/,/g,' ');
                                    }

                                    var R = arr[0];
                                    var G = arr[1];
                                    var B = arr[2];
                                    var hexValue = esapp.Utils.RGBtoHex(R,G,B);

                                    if (esapp.Utils.objectExists(Ext.getCmp('endcolourpicker'))){
                                        Ext.getCmp('endcolourpicker').setValue(hexValue);
                                    }
                                }
                            },
                            width:120+90
                        },{
                            xtype: 'colorbutton',
                            id:'endcolourpicker',
                            reference:'endcolourpicker',
                            text:'',
                            tooltip:esapp.Utils.getTranslation('opencolourpicker'), // 'Open colour picker',
                            // iconCls:'colorwheel',
                            // cls:'alignright',
                            scope:this,
                            width: 25,
                            height: 24,
                            border: true,
                            frame: false,
                            format: "#HEX6",
                            listeners: {
                                change: function(colorbtn, hexvalue) {
                                    var rgbvalue = esapp.Utils.HexToRGB(hexvalue);
                                    rgbvalue = rgbvalue.replace(/,/g, ' ');
                                    Ext.getCmp('endcolour').setValue(rgbvalue);
                                }
                            }
                            // handler:function() {
                            //     // showColorPicker(Ext.getCmp('endcolour'));
                            // }
                        }]
                    },{
                        xtype: 'checkbox',
                        reference: 'ckb_apply_class_label',
                        name: 'ckb_apply_class_label',
                        fieldLabel: esapp.Utils.getTranslation('apply_class_label'), // 'Apply class label',
                        labelSeparator: '',
                        value:true
                    }]
                }]
            });
        }
        generateClassesWin.show();
        // generateClassesWin.alignTo(this.getGridEl(),"br-l", [-6, 0]);
    }

    ,showGenerateLogValuesPanel: function(btn){
        btn.generateLogValuesPanel.show();
    }

    ,generateLogValuesPanel: function(btn){
        var me = this.getView();

        var generateLogValuesPanel = new Ext.panel.Panel({
            //  reference:'generateLogValuesWin'
             referenceHolder: true
            ,layout:'fit'
            ,autoShow : false
            ,hidden: true
            ,autoHeight: true
            ,width: 250
            ,collapsible: false
            ,resizable: false
            ,maximizable: false
            ,focusable: true
            ,floating: true
            ,closable: true
            ,closeAction: 'hide'
            ,title: esapp.Utils.getTranslation('win_title_logarithmic_values') // 'Generate logarithmic values for existing classes'
            ,plain: true
            // ,modal:true
            ,frame: false
            ,border: false
            ,bodyBorder: true
            ,cls: 'newpanelstyle'
            ,defaultAlign: 'tl-bc'
            ,header: {
                hidden: false,
                titlePosition: 0,
                focusable: true
            }
            ,bodyStyle: 'padding: 15px 3px 0 3px;'
            ,owner: btn
            ,config: {
                owner: btn
            }
            ,listeners : {
                afterrender: function(){
                    var legendminvalue = me.lookupReference('legend_minvalue');
                    var legendmaxvalue = me.lookupReference('legend_maxvalue');
                    if (legendminvalue.getValue() == 0){
                        this.lookupReference('minvalue').setValue(0.000001)
                    }
                    else {
                        this.lookupReference('minvalue').setValue(legendminvalue.getValue());
                    }
                    this.lookupReference('maxvalue').setValue(legendmaxvalue.getValue());
                    this.alignTarget = this.owner;
                },
                focusleave: function(){
                    this.hide();
                },
                show: function(){
                    this.alignTo(this.owner,'tl-bc');
                    // this.fireEvent('align');
                }
            }
            ,bbar: ['->',{
                // reference: 'GenerateClassesBtn',
                text: esapp.Utils.getTranslation('generate'), // 'Generate'
                iconCls:'fa fa-cogs',   // fa fa-cogs fa-2x
                handler: function(){
                    var precision = 8;
                    var legendClassesStore = me.getViewModel().getStore('legendClassesStore');
                    var generateLogValuesWindow = this.up().up();
                    var minvalue = generateLogValuesWindow.lookupReference('minvalue').getValue();
                    var maxvalue = generateLogValuesWindow.lookupReference('maxvalue').getValue();
                    var legendminvalue = me.lookupReference('legend_minvalue');
                    var legendmaxvalue = me.lookupReference('legend_maxvalue');
                    var logminvalue = parseFloat(Math.log10(minvalue).toFixed(precision));
                    var logmaxvalue = parseFloat(Math.log10(maxvalue).toFixed(precision));
                    var maxmindiff = logmaxvalue-logminvalue;
                    var totsteps = legendClassesStore.getCount();
                    var onestep = maxmindiff/totsteps;

                    var to = null;
                    var from = minvalue;
                    var previouslog = logminvalue;

                    legendClassesStore.suspendEvents();
                    legendClassesStore.each(function(legendclass, id){
                        to = parseFloat(Math.pow(10, previouslog+onestep).toFixed(precision));
                        if (id == 0) from = 0;
                        if (id == totsteps-1) to = maxvalue;
                        legendclass.set('from_step', from);     // parseFloat(from.toFixed(precision))
                        legendclass.set('to_step', to);
                        from=to;
                        previouslog+=onestep;
                    },this);
                    legendClassesStore.resumeEvents();

                    legendminvalue.setValue(0);
                    legendmaxvalue.setValue(maxvalue);
                    me.legend_type = 'logarithmic';
                    // me.params.legendrecord.set('legend_type', 'logarithmic');

                    me.getController().setLegendPreview();
                    generateLogValuesWindow.close();
                }
            }]
            ,items: [{
                xtype: 'fieldset',
                title: '',
                labelWidth:60,
                collapseable:false,
                border:false,
                margins:{top:15, right:5, bottom:0, left:5},
                items:[{
                    xtype:'numberfield',
                    reference:'minvalue',
                    fieldLabel: esapp.Utils.getTranslation('minvalue'), // 'Min value',
                    width:200,
                    minValue: 0.000001,
                    decimalPrecision:6
                },{
                    xtype:'numberfield',
                    reference:'maxvalue',
                    fieldLabel: esapp.Utils.getTranslation('maxvalue'), // 'MAx value',
                    width:200,
                    minValue: 0.000001,
                    decimalPrecision:6
                }]
            }]
        });

        return generateLogValuesPanel;

    }

    ,setLegendPreview: function(){
        var me = this.getView();
        var legendClassesStore = me.getViewModel().getStore('legendClassesStore');
        var TotClasses = parseInt(legendClassesStore.getCount());
        var legendname = me.lookupReference('title_in_legend').getValue();
        var fontSizeLabels = 14;
        var legendHTMLVertical = '';
        var TotColorLabels = 0;
        var TotGroupLabels = 0;

        legendClassesStore.each( function (record){
            var color_label = record.get('color_label');
            var group_label = record.get('group_label');
            if (color_label.trim() != '') {
               TotColorLabels += 1;
            }
            if (group_label.trim() != '') {
               TotGroupLabels += 1;
            }
        });
        legendClassesStore.sort('from_step', 'asc');

        if (TotClasses >= 25){
            var fontSizeTitle = 16;
            var stepWidth = 28;
            var stepHeight = 1;
            var rowspan = 15;
            var lineheight = 14;
            var classlegendstyle = "legend-style";

            if (TotClasses <= 35) {
                stepHeight = 10;
                rowspan = 1;
                classlegendstyle = "";
            }
            else if (TotClasses <= 65){
                stepHeight = 5;
                rowspan = 2;
                classlegendstyle = "";
            }
            else if (TotClasses <= 130){
                stepHeight = 2;
                rowspan = 5;
                classlegendstyle = "";
            }


            var mainTableBegin = '<table style="border-spacing:0px; background:white; padding:0;"> ';
            var mainTableEnd = '</table>';
            var legendHeaderRow = '<tr><td style="font-weight: bold; background:white; padding: 5px; font-size:' + fontSizeTitle.toString() + 'px;">' + legendname + '</td></tr>';
            var legendTableBegin = '<table style="border-spacing:0px; background:white; padding: 5px 5px 15px 10px;"> ';
            var legendTableEnd = '</table>';

            var ColumnSpan = 1;
            if (TotColorLabels > 0)
                ColumnSpan = Math.ceil(TotClasses / parseFloat(TotColorLabels));

            var Counter = 0;
            legendClassesStore.each( function (record) {
                // Add color column
                // convert row['color_rgb'] from RGB to html color
                var color_rgb = record.get('color_rgb').split(' ');
                var r = color_rgb[0];
                var g = color_rgb[1];
                var b = color_rgb[2];
                var color_html = 'rgb(' + r + ',' + g + ',' + b + ')';

                var border = "";
                if (TotClasses <= 24)
                    border = "border:1px solid black; ";

                // var legendColorColumn = '<td width=' + stepWidth.toString() + 'px; height=' + stepHeight.toString() + 'px; style="' + border + ' background-color: ' + color_html + '"></td>';
                var legendColorColumn = '<td width=' + stepWidth.toString() + 'px; class="'+classlegendstyle+'" style="' + border + ' background-color: ' + color_html + '"></td>';

                // Add label column
                Counter += 1;
                // var legendColorLabelColumn = '<td height="1px;"></td>';
                var legendColorLabelColumn = '<td class="'+classlegendstyle+'"></td>';
                if (ColumnSpan > 1) {
                    if (record.get('color_label') != null && record.get('color_label').trim() != '') {
                        legendColorLabelColumn = '<td rowspan="'+rowspan+'px;" style="font-weight: bold; font-size:' + fontSizeLabels.toString() + 'px; line-height:'+lineheight+'px; " valign="top" align="left">' + record.get('color_label') + '</td>'
                    }
                }
                else if (record.get('color_label') != null && record.get('color_label').trim() != '') {
                    legendColorLabelColumn = '<td rowspan="' + ColumnSpan.toString() + '" style="font-weight: bold; font-size:' + fontSizeLabels.toString() + 'px; line-height:'+lineheight+'px; " align="left">' + record.get('color_label') + '</td>';
                }
                legendHTMLVertical += '<tr style="height:'+stepHeight+'px;">' + legendColorColumn + legendColorLabelColumn + '</tr>';

                // Add an empty row for the label on last class to have the lable shown at the bottom of the table
                if (TotClasses == Counter && record.get('color_label') != null && record.get('color_label').trim() != ''){
                    legendHTMLVertical += '<tr style="height:1px;"></tr>';
                }
            });
            legendHTMLVertical = mainTableBegin + legendHeaderRow + '<tr><td>' + legendTableBegin + legendHTMLVertical + legendTableEnd + '</td></tr>' + mainTableEnd;

        }
        else {

            var mainTableBackgroundColor = 'transparent',
                fontSizeHeader = 16,
                firstColumnWidth = 35,
                legendColorTableBackgroundColor = 'white',
                legendLabelTableBackgroundColor = 'white',
                extraFirstRowHeight = 14,
                absoluteMaxRowColorTableHeight = 10,
                colorColumnWidth = 35,
                colorColumnHeight = 18,
                tickColumnWidth = 8,
                tickColumnHeight = 18,
                labelColumnHeight = 18,
                bordertop = ' ';

            var mainTableBegin = '<table style="background: ' + mainTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px; ">';
            var legendHeaderRow = '<tr><td colspan=2 style="background: white; padding:3px;"><span style="font-weight: bold; font-size:' + fontSizeHeader.toString() + 'px;">' + legendname + '</span></td></tr>';     // line-height: 24px;
            var legendRowBegin = '<tr>'
            var firstColumnBegin = '<td width=' + firstColumnWidth.toString() + 'px; style="border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px;">';
            var secondColumnBegin = '<td valign="top" align="left" style="border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 0px;" >';

            var legendColorTable = '<table style="background: ' + legendColorTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding-left: 3px;">';
            legendColorTable += '<tr><td colspan=2 height=' + extraFirstRowHeight.toString() + 'px; style=""></td></tr>';

            var legendLabelTable = '<table style="background: ' + legendLabelTableBackgroundColor + '; border:0px solid black; border-spacing:0px; border-padding:0px; cellspacing=0px; cellpadding=0px; margin: 0px; padding: 3px; ">';

            var row_counter = 0;
            // for row in legend_steps:
            legendClassesStore.each(function (record) {
                row_counter += 1;
                if (row_counter == 1)
                    bordertop = ' border-top:1px solid black; ';

                var borderbottom = ' ';
                var borderbottomtick = ' ';
                var absoluteMaxRowColorTable = '';
                var absoluteMaxRowLegendLabelTable = '';
                if (row_counter == TotClasses) {
                    borderbottom = ' border-bottom:1px solid black; ';
                    if (record.get('group_label') != null && record.get('group_label').trim() != '') {
                        borderbottomtick = ' border-bottom:1px solid black; ';
                        absoluteMaxRowColorTable = '<tr><td colspan=2 height=' + absoluteMaxRowColorTableHeight.toString() + 'px; style=""></td></tr>';
                        absoluteMaxRowLegendLabelTable = '<tr><td height=' + labelColumnHeight.toString() + 'px; style="font-weight: bold; font-size:' + fontSizeLabels.toString() + 'px;  padding:0px; margin: 0px; padding-left:5px;" valign="middle" align="left">' + record.get('group_label') + '</td></tr>';
                    }
                }
                // Add color column
                // convert row['color_rgb'] from RGB to html color
                var color_rgb = record.get('color_rgb').split(' ');
                var r = color_rgb[0];
                var g = color_rgb[1];
                var b = color_rgb[2];
                var color_html = 'rgb(' + r + ',' + g + ',' + b + ')';

                legendColorTable += '<tr> ' +
                    '<td width=' + colorColumnWidth.toString() + 'px; height=' + colorColumnHeight.toString() + 'px; style="padding:0px; margin: 0px; border-left:1px solid black; ' + borderbottom + bordertop + ' background-color: ' + color_html + '"></td>' +
                    '<td width=' + tickColumnWidth.toString() + 'px; height=' + tickColumnHeight.toString() + 'px; style="padding:0px; margin: 0px; border-top:1pt solid black; border-left:1px solid black; ' + borderbottomtick + '"></td>' +
                    '</tr>';

                legendColorTable += absoluteMaxRowColorTable;

                var color_label = '';
                if (record.get('color_label') != null && record.get('color_label') != '')
                    color_label = record.get('color_label').trim();
                legendLabelTable += '<tr><td height=' + labelColumnHeight.toString() + 'px; style="font-weight: bold; font-size:' + fontSizeLabels.toString() + 'px;  padding:0px; margin: 0px; padding-left:5px;" valign="middle" align="left">' + color_label + '</td></tr>';

                legendLabelTable += absoluteMaxRowLegendLabelTable;
            });

            legendColorTable += '</table>';
            legendLabelTable += '</table>';

            var columnEnd = '</td>';
            var legendRowEnd = '</tr>';
            mainTableEnd = '</table>';

            legendHTMLVertical = mainTableBegin + legendHeaderRow + legendRowBegin + firstColumnBegin + legendColorTable + columnEnd + secondColumnBegin + legendLabelTable + columnEnd + legendRowEnd + mainTableEnd;
        }

        Ext.getCmp('legendpreview').setHtml(legendHTMLVertical);
    }

    ,setLegendPreviewOld:function() {
//        var tempStore = this.store;
//         Ext.getCmp('legendpreview').setHtml('title_in_legend changed');
        var me = this.getView();
        var legendClassesStore = me.getViewModel().getStore('legendClassesStore');
        // var records = [];
        // legendClassesStore.each(function(r){
        //     records.push(r.copy());
        // });
        // var tempStore = new Ext.data.Store({
        //     recordType: legendClassesStore.recordType
        // });
        // tempStore.add(records);

        // update Preview Legend Panel
        var TotClasses = parseInt(legendClassesStore.getCount());
        var TotColorLabels = 0;
        var TotGroupLabels = 0;
        legendClassesStore.each( function (record){
            var color_label = Ext.String;
            color_label = record.data.color_label;
            var group_label = Ext.String;
            group_label = record.data.group_label;
            if (color_label.trim() != '') {
               TotColorLabels=TotColorLabels+1;
            }
            if (group_label.trim() != '') {
               TotGroupLabels=TotGroupLabels+1;
            }
        });
        legendClassesStore.sort('from_step', 'asc');

        var legendWidth=450;
        if (TotClasses > 20) legendWidth=750;
        var stepWidth = legendWidth;
        if (TotClasses > 5) stepWidth = legendWidth/TotClasses; else stepWidth = 50;
        if (stepWidth < 3) stepWidth = 1;


        var ColumnSpan = 1;
        if (TotColorLabels > 0){
            ColumnSpan = parseFloat(TotClasses/TotColorLabels); //.toFixed(0);   // round(TotClasses/TotColorLabels);
        }
        var legendname = me.lookupReference('title_in_legend').getValue();

        var legendHeader = '<h3>'+legendname+'</h3>';
        var legendTableBegin = '<table class="legendMap" style="border: 1px solid white; margin: 0px; padding: 0px; "> ';
//        var legendHeader = '<tr><td colspan="'+TotClasses+'"><h2>'+legendname+'</h2></td></tr>';

        var legendGroupLabels = '';
        if (TotGroupLabels > 0) {
            legendGroupLabels = '<tr>';
            var PrevGroupLabel = '';
            var Counter = 0;
            legendClassesStore.each( function (record){
                var group_label = Ext.String;
                group_label = record.data.group_label;
                var GroupLabel = group_label.trim();

                if (GroupLabel == PrevGroupLabel) {
                    Counter += 1;
                    PrevGroupLabel = GroupLabel;
                }
                else {
                    if (Counter != 0) {
                         legendGroupLabels = legendGroupLabels + '<td colspan="'+Counter+'" align="center">'+PrevGroupLabel+'</td><td rowspan="3" style="background-color: black;"><img src="img/clearpixel.gif" width="1" height="15" /></td>';
                    }
                    PrevGroupLabel = GroupLabel;
                    Counter = 1;
               }
            });

            legendGroupLabels = legendGroupLabels + '<td colspan="'+Counter+'" align="center">'+PrevGroupLabel+'</td>';
            legendGroupLabels = legendGroupLabels + '</tr>';
        }

        var border = "";
        if (TotClasses<=30) border = "border:1px solid black; ";

        var legendColors = '<tr>';
        legendClassesStore.each( function (record){
             var arr = record.data.color_rgb.split(" ");
             var R = arr[0];
             var G = arr[1];
             var B = arr[2];
             var color_html = esapp.Utils.RGBtoHex(R,G,B);
//             if (TotClasses <= 1)
//                 legendColors = legendColors + '<td><img src="img/clearpixel.gif" width="5" height="15" /></td>';   // Add 5px space between colors.

             legendColors = legendColors + '<td style="'+border+' background-color: '+color_html+';"><img src="img/clearpixel.gif" width="'+stepWidth+'" height="15" /></td>';
        });
        legendColors = legendColors + '</tr>';

        var legendColorLabels = '<tr>';
        var ColorLabel = '';
        legendClassesStore.each( function (record){
            var color_label = Ext.String;
            color_label = record.data.color_label;
            if (color_label.trim() != '')
                ColorLabel = '&nbsp;'+record.data.color_label+'&nbsp;';
            else ColorLabel = '<img src="img/clearpixel.gif" width="'+stepWidth+'" height="15" />';   // No label exists so fill space transparent image
            // maybe here a function has to analize the color label on its length and put <BR /> where needed!

            if (TotClasses <= 1){
                legendColorLabels = legendColorLabels + '<td style="max-width:50px;" align="center">'+ColorLabel+'</td>';
            }
            else{
                legendColorLabels = legendColorLabels + '<td style="max-width:50px;" align="center">'+ColorLabel+'</td>';
            }
        });

        legendColorLabels = legendColorLabels + '</tr>';
        var legendTableEnd = '</table>';

        var finalLegendPreview =  legendHeader + legendTableBegin + legendGroupLabels + legendColors + legendColorLabels + legendTableEnd;
        Ext.getCmp('legendpreview').setHtml(finalLegendPreview);
    } // eo function getLegendPreview
});
