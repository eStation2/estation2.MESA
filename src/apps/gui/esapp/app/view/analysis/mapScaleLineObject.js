
Ext.define("esapp.view.analysis.mapScaleLineObject",{
    extend: "Ext.container.Container",
 
    requires: [
        "esapp.view.analysis.mapScaleLineObjectController",
        "esapp.view.analysis.mapScaleLineObjectModel"
    ],
    
    controller: "analysis-mapscalelineobject",
    viewModel: {
        type: "analysis-mapscalelineobject"
    },

    xtype: 'mapscalelineobject',

    id: 'scale-line',
    reference: 'scale-line',
    autoWidth: true,
    autoHeight: true,
    minWidth: 175,
    minHeight: 30,
    layout: 'fit',
    hidden: false,
    floating: true,
    defaultAlign: 'bl-bl',
    closable: false,
    closeAction: 'hide',
    draggable: true,
    constrain: true,
    alwaysOnTop: true,
    autoShow: true,
    resizable: false,
    frame: false,
    frameHeader : false,
    border: false,
    shadow: false,
    bodyStyle:  'background:transparent;',
    header: {
        style: 'background:transparent;'
    },
    style: 'background: transparent; cursor:move;',
    margin: 0,
    padding: 0,

    scaleline_ImageObj: new Image(),
    scalelinePosition: [217,611],
    config: {
        html: '',
        mapView: null
    },

    //html: '<div id="scale-line_' + me.id + '">Hallooooooooooooooo</div>',

    initComponent: function () {
        var me = this;
        me.scaleline_ImageObj = new Image();
        me.scalelinePosition = [217,611];

        me.listeners = {
            el: {
                dblclick: function () {
                    me.fireEvent('refreshimage');
                }
            },
            afterrender: function () {

                var scaleline = new ol.control.ScaleLine({
                    units: 'metric',       // 'degrees'  'nautical mile'
                    //className: 'scale-line',
                    target: me.getEl()  //document.getElementById('scale-line_' + me.id)
                });
                me.mapView.map.addControl(scaleline);
                me.fireEvent('refreshimage');
            },
            refreshimage: function(){
                if(!me.hidden) {
                    var task = new Ext.util.DelayedTask(function() {
                        html2canvas(me.getEl().dom, {
                            //width: me.getWidth(),
                            onrendered: function (canvas) {
                                me.scaleline_ImageObj.src = canvas.toDataURL("image/png");
                            }
                        });
                    });
                    task.delay(350);
                }
            },
            show: function(){
                if (me.scalelinePosition != null){
                    me.setPosition(me.scalelinePosition);
                }
                me.fireEvent('refreshimage');
            }
        };

        me.callParent();
    }

});