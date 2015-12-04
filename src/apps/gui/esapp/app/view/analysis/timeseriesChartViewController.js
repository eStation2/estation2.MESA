Ext.define('esapp.view.analysis.timeseriesChartViewController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-timeserieschartview',

    _saveChart: function() {
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

});
