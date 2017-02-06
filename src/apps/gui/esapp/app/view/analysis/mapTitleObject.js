
Ext.define("esapp.view.analysis.mapTitleObject",{
    extend: "Ext.container.Container",
 
    requires: [
        "esapp.view.analysis.mapTitleObjectController",
        "esapp.view.analysis.mapTitleObjectModel",

        "Ext.form.field.HtmlEditor"
    ],
    
    controller: "analysis-maptitleobject",
    viewModel: {
        type: "analysis-maptitleobject"
    },

    xtype: 'maptitleobject',

    id: 'title_obj',
    reference: 'title_obj',
    autoWidth: true,
    autoHeight: true,
    minWidth: 300,
    minHeight: 45,
    layout: 'fit',
    hidden: true,
    floating: true,
    defaultAlign: 'tl-tl',
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
    html: '',
    title_ImageObj: new Image(),
    titlePosition: [5,5],  // [37, 20],
    changesmade: false,

    config: {
        tpl: [
            '<b style="color: rgb(0, 0, 0);"><font size="3">{selected_area}</font></b><div><b style="color: rgb(0, 0, 0);"><font size="3">{product_name}</font></b><div><b><font size="3" color="#3366ff">{product_date}</font></b></div></div>'
            //'{selected_area}',
            //'{product_name}',       // '{selected_area:htmlEncode} - {product_name:htmlEncode}',
            //'{product_date}'
        ],
        titleData: null
    },
    //bind:{
    //    titleData:'{titleData}'
    //},
    bind:{
        data:'{titleData}'
    },

    initComponent: function () {
        var me = this;

        //me.defaultTpl = '<font size="3" style="color: rgb(0, 0, 0);"><b>{selected_area} - {product_name}&nbsp;</b></font><div><font size="3"><b>Decade of <font color="#3366ff">{product_date}</font></b></font></div>';
        //me.tpl = me.defaultTpl;

        me.listeners = {
            //element  : 'el',
            el: {
                dblclick: function () {
                    var editorpanel = this.component.map_title_editor_panel;
                    //editorpanel.down('htmleditor').setValue(this.component.down().tpl.html);
                    editorpanel.down('htmleditor').setValue(this.component.tpl.html);
                    editorpanel.constrainTo = this.component.constrainTo;
                    editorpanel.show();

                    //Ext.util.Observable.capture(this, function(e){console.log('titleObj ' + e);});
                    //
                    //this.component.up().down('#stopedit_tool_' + me.id).show();
                    //this.component.up().down('htmleditor').setValue(this.component.tpl.html);
                    //this.component.up().down('htmleditor').show();
                    //this.component.hide();
                }
            },
            afterrender: function () {
                Ext.tip.QuickTipManager.register({
                    target: this.id,
                    trackMouse: true,
                    title: 'Title object',
                    text: '<img src="resources/img/pencil_cursor.png" alt="" height="18" width="18">' + 'Double click to edit.'
                });

                //me.mon(me.el, 'click', function(){alert('container click');});
                //me.mon(me.el, 'change', function(){alert('container change');});
            },
            refreshimage: function(){
                //alert('container change');

                if(!me.hidden) {
                    //var titleObjDomClone = Ext.clone(me.getEl().dom);
                    var titleObjDom = me.getEl().dom;

                    var task = new Ext.util.DelayedTask(function() {
                        esapp.Utils.removeClass(titleObjDom, 'rounded-box');
                        //titleObjDomClone.style.width = me.getWidth();
                        html2canvas(titleObjDom, {
                            onrendered: function (canvas) {
                                me.title_ImageObj.src = canvas.toDataURL("image/png");
                                //console.info(me.title_ImageObj);
                                esapp.Utils.addClass(titleObjDom, 'rounded-box');
                            }
                        });
                    });
                    if (me.changesmade){
                        task.delay(500);
                    }
                }
            },
            show: function(){
                me.setPosition(me.titlePosition);
                me.fireEvent('refreshimage');

                me.mon(me, {
                    move: function() {
                       me.titlePosition = me.getPosition(true);
                    }
                });
            }
            //,move: function(){
            //    me.titlePosition = me.getPosition(true);
            //}
            //,single: true  // Remove the listener after first invocation
            //,change: {
            //    element  : 'el',
            //    fn: function(me, x , y , eOpts){
            //        alert('onchange');
            //        //me.on('change', function() {
            //        //    alert('onchange');
            //        //});
            //    }
            //}
        };


        me.map_title_editor = Ext.create('Ext.form.field.HtmlEditor', {
            xtype: 'htmleditor',
            id: 'map_title_editor_' + me.id,
            reference: 'map_title_editor_' + me.id,
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
        });

        me.map_title_editor.getToolbar().insert(1,{
            xtype: 'button',
            //text: 'Fields',
            scope: this,
            tooltip: 'Add a dynamic field',
            overflowText: 'Add a dynamic field',
            hidden: false,
            iconCls: 'fa fa-code',
            floating: false,  // usually you want this set to True (default)
            enableToggle: false,
            arrowVisible: false,
            arrowAlign: 'right',
            collapseDirection: 'left',
            menuAlign: 'tl-tr',
            menu: {
                hideOnClick: false,
                iconAlign: '',
                width: 125,
                defaults: {
                    hideOnClick: false,
                    cls: "x-menu-no-icon",
                    padding: 2
                },
                items: [{
                    text: 'Selected area',
                    handler: function(){
                        me.map_title_editor.insertAtCursor('{selected_area}');
                    }
                },{
                    text: 'Product name',
                    handler: function(){
                        me.map_title_editor.insertAtCursor('{product_name}');
                    }
                },{
                    text: 'Product date',
                    handler: function(){
                        me.map_title_editor.insertAtCursor('{product_date}');
                    }
                }]
            }
        });

        me.map_title_editor_panel = Ext.create('Ext.panel.Panel', {
            autoWidth: true,
            autoHeight: true,
            layout: 'fit',
            modal: true,
            hidden: true,
            floating: true,
            defaultAlign: 'tl-tl',
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
                title: 'Title object',
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
                        var mapTitleObj = me,
                            mapTitleEditor = panel.down('#map_title_editor_' + me.id);
                        panel.hide();
                        mapTitleObj.tpl.set(mapTitleEditor.getValue(), true);   // .replace(/"/g, '&quot;', true);
                        //console.info(mapTitleObj.getData());
                        mapTitleObj.update(mapTitleObj.getData());
                        mapTitleObj.updateLayout();
                        mapTitleObj.changesmade = true;
                        //mapTitleObj.show();
                        mapTitleObj.fireEvent('refreshimage');

                        //mapTitleObj.down().tpl.set(mapTitleEditor.getValue(), true);   // .replace(/"/g, '&quot;', true);
                        //console.info(mapTitleObj.down().getData());
                        //mapTitleObj.down().update(mapTitleObj.down().getData());
                        //mapTitleObj.down().updateLayout();
                        //mapTitleObj.updateLayout();
                        //mapTitleObj.show();
                        //mapTitleObj.down().refresh();
                    }
                }]
            },
            items: me.map_title_editor
        });

        me.callParent();

        //me.relayEvents(me, ['change']);
    }
});
