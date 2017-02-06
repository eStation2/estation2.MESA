
Ext.define("esapp.view.analysis.mapDisclaimerObject",{
    extend: "Ext.container.Container",
 
    requires: [
        "esapp.view.analysis.mapDisclaimerObjectController",
        "esapp.view.analysis.mapDisclaimerObjectModel",

        "Ext.form.field.HtmlEditor"
    ],
    
    controller: "analysis-mapdisclaimerobject",
    viewModel: {
        type: "analysis-mapdisclaimerobject"
    },

    xtype: 'mapdisclaimerobject',

    id: 'disclaimer_obj',
    reference: 'disclaimer_obj',
    autoWidth: true,
    autoHeight: true,
    minWidth: 250,
    minHeight: 30,
    layout: 'fit',
    hidden: true,
    floating: true,
    defaultAlign: 'bl-bl',
    closable: false,
    closeAction: 'hide',
    draggable: true,
    constrain: true,
    alwaysOnTop: true,
    autoShow: false,
    resizable: false,
    frame: false,
    frameHeader : false,
    border: false,
    shadow: false,
    cls: 'rounded-box',
    //style: 'background: white; cursor:url(resources/img/pencil_cursor.png),auto;',
    style: 'background: white; cursor:move;',

    //bodyStyle:  'background:transparent;',
    margin: 0,
    padding: 3,
    disclaimer_ImageObj: new Image(),
    disclaimerPosition: [267,710],
    changesmade: true,
    config: {
        html: '',
        content: ''
    },

    initComponent: function () {
        var me = this;

        //me.defaultContent = '<font size="1">​Geographical map, WGS 84 - Resolution 5km</font><div><font size="1">Sources: 1) Image NDVI &nbsp;2) Vectors FAO GAUL 2015</font></div>';
        //me.html = me.defaultContent;
        //me.setHtml(me.defaultContent);

        me.listeners = {
            //element  : 'el',
            el: {
                dblclick: function () {
                    var editorpanel = this.component.map_disclaimer_editor;
                    editorpanel.down('htmleditor').setValue(this.component.getContent());
                    editorpanel.constrainTo = this.component.constrainTo;
                    editorpanel.show();
                }
            },
            afterrender: function () {
                Ext.tip.QuickTipManager.register({
                    target: this.id,
                    trackMouse: true,
                    title: 'Disclaimer object',
                    text: '<img src="resources/img/pencil_cursor.png" alt="" height="18" width="18">' + 'Double click to edit.'
                });

                //this.setPosition(14, 588);
            },
            refreshimage: function(){
                if(!me.hidden) {
                    //var disclaimerObjDomClone = Ext.clone(me.getEl().dom);
                    var disclaimerObjDom = me.getEl().dom;

                    var task = new Ext.util.DelayedTask(function() {
                        esapp.Utils.removeClass(disclaimerObjDom, 'rounded-box');
                        //disclaimerObjDomClone.style.width = me.getWidth();
                        html2canvas(disclaimerObjDom, {
                            width: me.getWidth(),
                            onrendered: function (canvas) {
                                me.disclaimer_ImageObj.src = canvas.toDataURL("image/png");
                                //console.info(me.disclaimer_ImageObj);
                                esapp.Utils.addClass(disclaimerObjDom, 'rounded-box');
                                me.changesmade = false;
                            }
                        });
                    });
                    if (me.getContent() != '' && me.changesmade){
                        task.delay(500);
                    }
                }
            },
            show: function(){
                me.setPosition(me.disclaimerPosition);
                me.fireEvent('refreshimage');
                me.mon(me, {
                    move: function() {
                       me.disclaimerPosition = me.getPosition(true);
                    }
                });
            }
        };

        me.map_disclaimer_editor = Ext.create('Ext.panel.Panel', {
            autoWidth: true,
            autoHeight: true,
            layout: 'fit',
            modal: true,
            hidden: true,
            floating: true,
            defaultAlign: 'bl-bl',
            closable: true,
            closeAction: 'hide',
            draggable: true,
            constrain: true,
            constrainTo: me.constrainTo,
            alwaysOnTop: false,
            autoShow: false,
            resizable: false,
            frame: false,
            frameHeader : false,
            border: false,
            shadow: true,
            headerOverCls: 'grayheader',
            header: {
                title: 'Disclaimer object',
                titleAlign: 'right',
                cls: 'transparentheader',
                hidden: false,
                items: [{
                    xtype:'button',
                    itemId: 'stopedit_tool_' + me.id,
                    tooltip:'Save changes',
                    glyph:0xf0c7,
                    cls: 'btntransparent',
                    hidden: false,
                    margin: '3 0 0 5',
                    handler: function (btn) {
                        var panel = btn.up().up();
                        var mapDisclaimerObj = me,
                            mapDisclaimerEditor = panel.down('#map_disclaimer_editor_' + me.id);

                        mapDisclaimerObj.update(mapDisclaimerEditor.getValue());
                        mapDisclaimerObj.setContent(mapDisclaimerEditor.getValue());
                        mapDisclaimerObj.changesmade = true;
                        //mapDisclaimerObj.show();  // Show event not triggered because the object is not hidden!
                        mapDisclaimerObj.fireEvent('refreshimage');
                        panel.hide();
                    }
                }]
            },
            items: [{
                xtype: 'htmleditor',
                id: 'map_disclaimer_editor_' + me.id,
                reference: 'map_disclaimer_editor_' + me.id,
                layout: 'fit',
                style: 'background: white;',
                hidden: false,
                enableAlignments: false,
                enableColors: true,
                enableFont: true,
                enableFontSize: true,
                enableFormat: true,
                enableLinks: false,
                enableLists: false,
                enableSourceEdit: true,
                autoWidth: true,
                autoHeight: true,
                minWidth: 250,
                minHeight: 45,
                value: ''
            }]
        });

        me.callParent();

    }
});
