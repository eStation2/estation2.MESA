
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

    // id: 'product-legend',
    // reference: 'product-legend',
    autoWidth: true,
    autoHeight: true,
    minWidth: 65,
    minHeight: 100,
    layout: 'fit',
    hidden: true,
    floating: true,
    defaultAlign: 'tl',
    closable: false,
    closeAction: 'destroy',
    draggable: true,
    constrain: true,
    alwaysOnTop: false,
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
    style: 'background: transparent; cursor:move;',
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


    config: {
        html: '',
        legendHTML_ImageObj: new Image(),
        legendLayout: 'vertical',
        legendPosition: [0, 95],
        showlegend: true
    },

    initComponent: function () {
        var me = this;
        //Ext.util.Observable.capture(me, function(e){console.log('maplegendobject - ' + me.id + ': ' + e);});

        me.legendHTML_ImageObj = new Image();
        me.legendLayout = 'vertical';
        me.legendPosition = [0, 95];
        me.showlegend = true;

        me.listeners = {
            el: {
                dblclick: function () {
                    var htmlimage = '';

                    if (me.legendLayout=='horizontal') {
                        me.setHtml(me.legendHTMLVertical);
                        me.fireEvent('refreshimage');
                        me.legendLayout='vertical';
                    }
                    else {
                        me.setHtml(me.legendHTML);
                        me.fireEvent('refreshimage');
                        me.legendLayout='horizontal';
                    }
                }
            },
            afterrender: function () {
                Ext.tip.QuickTipManager.register({
                    target: this.id,
                    trackMouse: true,
                    title: esapp.Utils.getTranslation('legend_object'), // 'Legend object',
                    text: esapp.Utils.getTranslation('doubleclick_to_change_view') // 'Double click to change view.'
                });

                // me.mon(me, {
                //     move: function() {
                //         console.info('moving legend');
                //         console.info(me.legendPosition);
                //         me.legendPosition = me.getPosition(true);
                //     }
                // });
                // if (!me.showlegend) {
                //     me.hide();
                // }
                // else {
                //     me.fireEvent('refreshimage');
                // }
            },

            // beforerender: function () {
            //     me.fireEvent('refreshimage');
            // },
            refreshimage: function(){
                if(!me.hidden) {
                    // console.info('refreshimage LEGEND');
                    var htmlimage = ''
                    var legendObjDom = me.getEl().dom;
                    // var heightAdjust = me.getHeight();
                    // if (me.getHeight() > 295){
                    //     heightAdjust = 295;
                    // }
                    var task = new Ext.util.DelayedTask(function() {
                        if (legendObjDom != null){
                            html2canvas(legendObjDom, {
                                width: me.getWidth(),
                                height: me.getHeight(),
                                // logging: true,
                                onrendered: function (canvas) {
                                    me.legendHTML_ImageObj.src = canvas.toDataURL("image/png");
                                    htmlimage = '<img width="' + me.getWidth() + '" height="' +  me.getHeight() + '" src="' + me.legendHTML_ImageObj.src + '" />';
                                    me.setHtml(htmlimage);
                                    me.updateLayout();
                                }
                            });
                        }
                    });
                    // console.info('refreshimage legendObj');
                    task.delay(1000);
                }
            }
            ,show: function(){

                if (me.legendLayout == 'horizontal') {
                    me.setHtml(me.legendHTML);
                }
                else {
                    me.setHtml(me.legendHTMLVertical);
                }

                if (!me.showlegend) {
                    me.hide();
                }
                else {
                    me.setPosition(me.legendPosition);
                    // me.fireEvent('refreshimage');
                }
            }
            // ,move: function(){
            //     // me.legendPosition = me.getPosition();
            //     console.info(me.legendPosition);
            //     console.info(me.getPosition(true));
            // }
        };

        me.callParent();

    }
});
