Ext.define('esapp.view.analysis.timeseriesChartViewController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-timeserieschartview',

    openChartProperties: function(callComponent) {
        var me = this;
        //var layerrecord = callComponent.layerrecord;

        //var texteditor = new Ext.grid.GridEditor(new Ext.form.TextField({allowBlank: false,selectOnFocus: true}));
        //var numbereditor = new Ext.grid.GridEditor(new Ext.form.NumberField({allowBlank: false,selectOnFocus: true}));
        //
        //var cedit = new Ext.grid.GridEditor(new Ext.ux.ColorField({allowBlank: false,selectOnFocus: true}));
        var crenderer = function(color) {
            renderTpl = color;

            if (color.trim()==''){
                renderTpl = 'transparent';
            }
            else {
                renderTpl = '<span style="background:rgb('+esapp.Utils.HexToRGB(color)+'); color:'+esapp.Utils.invertHexToRGB(color)+';">'+esapp.Utils.HexToRGB(color)+'</span>';
            }
            return renderTpl;
        };

        var drawproperties = Ext.create('Ext.panel.Panel', {
            title: 'Edit chart draw properties',
            width: 450,
            autoHeight: true,
            margin: '0 0 10 0',
            maximizable: false,
            collapsible: true,
            resizable: true,
            //constrainHeader: true,
            //autoWidth: true,
            //autoHeight: true,
            layout: 'fit',
            hidden: true,
            floating: true,
            defaultAlign: 'bl-bl',
            closable: true,
            closeAction: 'hide',
            draggable: true,
            constrain: true,
            alwaysOnTop: true,
            autoShow: false,
            frame: true,
            frameHeader : false,
            border: false,
            shadow: false,
            defaults: {
              //align: 'right'
            },
            items: [
                {   text: esapp.Utils.getTranslation('Chart draw properties'),
                    xtype: 'propertygrid',
                    //nameField: 'Property',
                    //width: 400,
                    nameColumnWidth: 180,
                    sortableColumns: false,
                    source: {
                        chart_width: '',
                        chart_height: '',
                        chart_title: '',   // layerrecord.get('polygon_outlinecolor'),
                        chart_title_colour: '',
                        chart_title_font_size: '',
                        chart_subtitle: '',
                        chart_subtitle_colour: '',
                        chart_subtitle_font_size: '',

                        yaxe1_title: '',
                        yaxe1_font_size: '',
                        yaxe1_colour: '',
                        yaxe1_min: '',
                        yaxe1_max: '',

                        yaxe2_title: '',
                        yaxe2_font_size: '',
                        yaxe2_colour: '',
                        yaxe2_min: '',
                        yaxe2_max: '',

                        legend_font_size: '',
                        xaxe_font_size: ''
                    },
                    sourceConfig: {
                        chart_width: {
                            displayName: 'Chart width (in px)',
                            type: 'number'
                        },
                        chart_height: {
                            displayName: 'Chart height (in px)',
                            type: 'number'
                        },
                        chart_title: {
                            displayName: 'Title',
                            type: 'text'
                        },
                        chart_title_colour: {
                            displayName: 'Title colour',
                            editor: {
                                xtype: 'mycolorpicker'
                            }
                            ,renderer: crenderer
                        },
                        chart_title_font_size: {
                            displayName: 'Title font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        },
                        chart_subtitle: {
                            displayName: 'Sub title',
                            type: 'text'    // 'number'
                        },
                        chart_subtitle_colour: {
                            displayName: 'Sub title colour',
                            editor: {
                                xtype: 'mycolorpicker'
                                //,floating: false
                            }
                            ,renderer: crenderer
                        },
                        chart_subtitle_font_size: {
                            displayName: 'Sub title font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        },
                        yaxe1_title: {
                            displayName: 'yAxe 1 title',
                            type: 'text'
                        },
                        yaxe1_font_size: {
                            displayName: 'yAxe 1 font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        },
                        yaxe1_colour: {
                            displayName: 'yAxe 1 colour',
                            editor: {
                                xtype: 'mycolorpicker'
                                //,floating: false
                            }
                            ,renderer: crenderer
                        },
                        yaxe1_min: {
                            displayName: 'yAxe 1 min',
                            type: 'number'
                        },
                        yaxe1_max: {
                            displayName: 'yAxe 1 max',
                            type: 'number'
                        },
                        yaxe2_title: {
                            displayName: 'yAxe 2 title',
                            type: 'text'
                        },
                        yaxe2_font_size: {
                            displayName: 'yAxe 2 font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        },
                        yaxe2_colour: {
                            displayName: 'yAxe 2 colour',
                            editor: {
                                xtype: 'mycolorpicker'
                                //,floating: false
                            }
                            ,renderer: crenderer
                        },
                        yaxe2_min: {
                            displayName: 'yAxe 2 min',
                            type: 'number'
                        },
                        yaxe2_max: {
                            displayName: 'yAxe 2 max',
                            type: 'number'
                        },
                        legend_font_size: {
                            displayName: 'Legend font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        },
                        xaxe_font_size: {
                            displayName: 'xAxe font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        }
                    },
                    //customEditors: {
                    //    myProp: new Ext.grid.GridEditor(combo, {})
                    //},
                    //customRenders: {
                    //    myProp: function(value){
                    //        var record = combo.findRecord(combo.valueField, value);
                    //        return record ? record.get(combo.displayField) : combo.valueNotFoundText;
                    //    }
                    //},
                    listeners: {
                        propertychange: function( source, recordId, value, oldValue, eOpts ){
                            //console.info(source);
                            //console.info(recordId);
                            //console.info(value);
                            //console.info(oldValue.toLowerCase());
                            //if (value != oldValue)
                                //layerrecord.set(recordId, value)
                        }
                    }
                },
                {   title: esapp.Utils.getTranslation('Timeseries draw properties'),
                    xtype: 'grid'

                }
            ]
        });
        me.getView().add(drawproperties);
        drawproperties.show();

    },

    saveChart: function() {

        //function saveImageAs (imgOrURL) {
        //    if (typeof imgOrURL == 'object')
        //      imgOrURL = imgOrURL.src;
        //    window.win = open (imgOrURL);
        //    setTimeout('win.document.execCommand("SaveAs")', 500);
        //}

        function download(data, filename) {
          var a = document.createElement('a');
          a.download = filename;
          a.href = data;
          document.body.appendChild(a);
          a.click();
          a.remove();
        }

        var EXPORT_WIDTH = 1200;
        var me = this.getView();
        var chart = me.tschart;

        var render_width = EXPORT_WIDTH;
        var render_height = render_width * chart.chartHeight / chart.chartWidth;

        // Get the cart's SVG code
        var svg = chart.getSVG({
            exporting: {
              sourceWidth: chart.chartWidth,
              sourceHeight: chart.chartHeight
            }
        });

        // Create a canvas
        var canvas = document.createElement('canvas');
        canvas.height =  render_height;
        canvas.width = render_width;
        //document.body.appendChild(canvas);

        // Create an image and draw the SVG onto the canvas
        var image = new Image;
            image.onload = function() {
                canvas.getContext('2d').drawImage(this, 0, 0, render_width, render_height);
                var data = canvas.toDataURL("image/png");
                download(data, me.filename + '.png');
            };
        image.src = 'data:image/svg+xml;base64,' + window.btoa(svg);


        //console.info(data);
        // data = data.replace(/^data:image\/(png|jpg);base64,/, "");
        //download(data, me.filename + '.png');

        // console.info(image);
        // saveImageAs(image);
    },

    tsDownload: function() {

        var chart = this.getView().tschart;
        var type = Highcharts.exporting.MIME_TYPES.XLS;
        chart.exportChartLocal({ type: type, filename: this.getView().filename});
    }

    ,_saveChart: function() {
        // FROM : http://willkoehler.net/2014/11/07/client-side-solution-for-downloading-highcharts-charts-as-images.html

        function download(canvas, filename) {
            download_in_ie(canvas, filename) || download_with_link(canvas, filename);
        }

        // Works in IE10 and newer
        function download_in_ie(canvas, filename) {
            return(navigator.msSaveOrOpenBlob && navigator.msSaveOrOpenBlob(canvas.msToBlob(), filename));
        }

        // Works in Chrome and FF. Safari just opens image in current window, since .download attribute is not supported
        function download_with_link(canvas, filename) {
            var a = document.createElement('a')
            a.download = filename
            a.href = canvas.toDataURL("image/png")
            document.body.appendChild(a);
            a.click();
            a.remove();
        }

        var chart = this.getView().tschart;

        var render_width = 1000;
        var render_height = render_width * chart.chartHeight / chart.chartWidth;

        var svg = chart.getSVG({
            exporting: {
                sourceWidth: chart.chartWidth,
                sourceHeight: chart.chartHeight
            }
        });

        var canvas = document.createElement('canvas');
        canvas.height = render_height;
        canvas.width = render_width;

        canvg(canvas, svg, {
            scaleWidth: render_width,
            scaleHeight: render_height,
            ignoreDimensions: true
        });

        download(canvas, this.getView().filename + '.png');

    }
});
