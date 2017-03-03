
Ext.define("esapp.view.analysis.mapLegendObject",{
    extend: "Ext.container.Container",  // "Ext.panel.Panel",
 
    requires: [
        "esapp.view.analysis.mapLegendObjectController",
        "esapp.view.analysis.mapLegendObjectModel"
    ],
    
    controller: "analysis-maplegendobject",
    viewModel: {
        type: "analysis-maplegendobject"
    },

    xtype: 'maplegendobject',

    id: 'product-legend',
    reference: 'product-legend',
    autoWidth: true,
    autoHeight: true,
    minWidth: 50,
    minHeight: 50,
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
    //bodyStyle:  'background:transparent;',
    header: {
        style: 'background:transparent;'
    },
    style: 'background: white; cursor:move;',
    // Do not use default Panel dragging: use window type dragging
    // initDraggable: Ext.window.Window.prototype.initDraggable,
    // simpleDrag: true,
    //listeners: {
    //    close: function(){
    //        var maplegend_togglebtn = me.lookupReference('legendbtn_'+me.id.replace(/-/g,'_')); //  + me.getView().id);
    //        maplegend_togglebtn.show();
    //        maplegend_togglebtn.toggle();
    //    }
    //},
    legendHTML_ImageObj: new Image(),
    legendLayout: 'vertical',
    legendPosition: [5, 210],
    showlegend: true,
    html: '&nbsp;',

    initComponent: function () {
        var me = this;
        //Ext.util.Observable.capture(me, function(e){console.log('maplegendobject - ' + me.id + ': ' + e);});

        me.listeners = {
            el: {
                dblclick: function () {
                    if (me.legendLayout=='horizontal') {
                        me.setHtml(me.legendHTMLVertical);
                        me.legendLayout='vertical';
                    }
                    else {
                        me.setHtml(me.legendHTML);
                        me.legendLayout='horizontal';
                    }
                    me.fireEvent('refreshimage');
                }
            },
            afterrender: function () {
                Ext.tip.QuickTipManager.register({
                    target: this.id,
                    trackMouse: true,
                    title: esapp.Utils.getTranslation('legend_object'), // 'Legend object',
                    text: esapp.Utils.getTranslation('doubleclick_to_change_view') // 'Double click to change view.'
                });
                me.fireEvent('refreshimage');
            },
            refreshimage: function(){
                if(!me.hidden) {
                    var legendObjDom = me.getEl().dom;

                    var task = new Ext.util.DelayedTask(function() {
                        html2canvas(legendObjDom, {
                            //width: me.getWidth(),
                            onrendered: function (canvas) {
                                me.legendHTML_ImageObj.src = canvas.toDataURL("image/png");
                                //console.info(me.legendHTML_ImageObj);
                            }
                        });
                    });
                    task.delay(200);
                }
            }
            ,show: function(){
                //console.info('SHOW LEGEND');

                if (me.legendLayout == 'horizontal') {
                    me.setHtml(me.legendHTML);
                }
                else {
                    me.setHtml(me.legendHTMLVertical);
                }

                me.setPosition(me.legendPosition);

                if (!me.showlegend) {
                    me.hide();
                }

                me.mon(me, {
                    move: function() {
                       me.legendPosition = me.getPosition(true);
                    }
                });
            }
            //,move: function(){
            //    me.legendPosition = me.getPosition(true);
            //}
        };

        me.callParent();
    }
});
