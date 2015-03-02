Ext.define('esapp.view.acquisition.logviewer.LogViewController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-logviewer-logview'

    // {{{
    ,getFile: function(win) {
        //console.info(win);

        //var params = Ext.JSON.encode(win.params);
        var params = {
               logtype: win.params.logtype,
               gettype: win.params.record.get('type'),
               productcode:win.params.record.get('productcode'),
               mapsetcode:win.params.record.get('mapsetcode'),
               version:win.params.record.get('version'),
               subproductcode:win.params.record.get('subproductcode')
        };

        Ext.Ajax.request({
            method: 'GET',
            url:'getlogfile',
            params: params,
            loadMask:'Loading data...',
            callback:function(callinfo,responseOK,response ){

                var response_Text = response.responseText.trim();
                Ext.getCmp('logfilecontent').setValue(response_Text);
                //eStation.myGlobals.OriginalContent = Ext.getCmp('logfilecontent').getRawValue();
                //eStation.LogfileShowPanel.setTitle('File: ' + record.data.filename);
            },
            success: function ( result, request ) {},
            failure: function ( result, request) {}
        });
    } // eo getFile
    //   }}}

    // {{{
    ,highlightSearchString: function() {
        var searchText = Ext.getCmp('highlightfindstring').getValue().trim();

        if ( searchText != '') {
            var targetcontent = Ext.getCmp('logfilecontent').getValue(); // eStation.myGlobals.OriginalContent;
            var textColor = "black";
            var bgColor = "yellow";
            var treatAsPhrase = false;
            var warnOnFailure=false;
            var highlightStartTag = "<span style='color:" + textColor + "; background-color:" + bgColor + ";'>";
            var highlightEndTag = "</span>";

            var highlightedcontent = this.highlightSearchTerms(targetcontent, searchText, treatAsPhrase, warnOnFailure, highlightStartTag, highlightEndTag);

            // var contentField = Ext.getCmp('logfilecontent');
            Ext.getCmp('logfilecontent').setValue(highlightedcontent);

        }
        // else Ext.getCmp('logfilecontent').setValue(eStation.myGlobals.OriginalContent);   // No search terms so reset content to original content
    }

    // Animals highlightText function  http://www.extjs.com/forum/showthread.php?t=68599
    ,highlightText: function (node, regex, cls, deep) {
        if (typeof(regex) == 'string') {
            regex = new RegExp(regex, "g");
        } else if (!regex.global) {
            throw "RegExp to highlight must use the global qualifier";
        }

        var value, df, m, l, start = 0, highlightSpan;
        //  Note: You must add the trim function to the String's prototype
        if ((node.nodeType == 3) && (value = node.data.trim())) {

            // Loop through creating a document DocumentFragment containing text nodes interspersed with
            // <span class={cls}> elements wrapping the matched text.
            while (m = regex.exec(value)) {
                if (!df) {
                    df = document.createDocumentFragment();
                }
                if (l = m.index - start) {
                    df.appendChild(document.createTextNode(value.substr(start, l)));
                }
                highlightSpan = document.createElement('span');
                highlightSpan.className = cls;
                highlightSpan.appendChild(document.createTextNode(m[0]));
                df.appendChild(highlightSpan);
                start = m.index + m[0].length;
            }

            // If there is a resulting DocumentFragment, replace the original text node with the fragment
            if (df) {
                if (l = value.length - start) {
                    df.appendChild(document.createTextNode(value.substr(start, l)));
                }
                node.parentNode.replaceChild(df, node);
            }
        }else{
            if(deep){
                Ext.each(node.childNodes, function(child){
                    highlightText(child, regex, cls, deep);
                });
            }
        }
    }

    // Animals removeHighlighting function
    ,removeHighlighting: function (highlightClass, node) {
        var h = Ext.DomQuery.select("span." + highlightClass, node);
        for (var i = 0; i < h.length; i++) {
            var s = h[i], sp = s.parentNode;
            sp.replaceChild(document.createTextNode(s.firstChild.data), s);
            sp.normalize();
        }
    }


    /*
     * This is the function that actually highlights a text string by
     * adding HTML tags before and after all occurrences of the search
     * term. You can pass your own tags if you'd like, or if the
     * highlightStartTag or highlightEndTag parameters are omitted or
     * are empty strings then the default <font> tags will be used.
     */
    ,doHighlight: function (bodyText, searchTerm, highlightStartTag, highlightEndTag)
    {
      // the highlightStartTag and highlightEndTag parameters are optional
      if ((!highlightStartTag) || (!highlightEndTag)) {
        highlightStartTag = "<b style='color:blue; background-color:yellow;'>";
        highlightEndTag = "</b>";
      }

      // find all occurences of the search term in the given text,
      // and add some "highlight" tags to them (we're not using a
      // regular expression search, because we want to filter out
      // matches that occur within HTML tags and script blocks, so
      // we have to do a little extra validation)
      var newText = "";
      var i = -1;
      var lcSearchTerm = searchTerm.toLowerCase();
      var lcBodyText = bodyText.toLowerCase();

      while (bodyText.length > 0) {
        i = lcBodyText.indexOf(lcSearchTerm, i+1);
        if (i < 0) {
          newText += bodyText;
          bodyText = "";
        } else {
          // skip anything inside an HTML tag
          if (bodyText.lastIndexOf(">", i) >= bodyText.lastIndexOf("<", i)) {
            // skip anything inside a <script> block
            if (lcBodyText.lastIndexOf("/script>", i) >= lcBodyText.lastIndexOf("<script", i)) {
              newText += bodyText.substring(0, i) + highlightStartTag + bodyText.substr(i, searchTerm.length) + highlightEndTag;
              bodyText = bodyText.substr(i + searchTerm.length);
              lcBodyText = bodyText.toLowerCase();
              i = -1;
            }
          }
        }
      }

      return newText;
    }


    /*
     * This is sort of a wrapper function to the doHighlight function.
     * It takes the searchText that you pass, optionally splits it into
     * separate words, and transforms the text on the current web page.
     * Only the "searchText" parameter is required; all other parameters
     * are optional and can be omitted.
     */
    ,highlightSearchTerms: function (targetcontent, searchText, treatAsPhrase, warnOnFailure, highlightStartTag, highlightEndTag)
    {
      // if the treatAsPhrase parameter is true, then we should search for
      // the entire phrase that was entered; otherwise, we will split the
      // search string so that each word is searched for and highlighted
      // individually
      if (treatAsPhrase) {
        searchArray = [searchText];
      } else {
        searchArray = searchText.split(" ");
      }

      if (!targetcontent || typeof(targetcontent) == "undefined") {
        if (warnOnFailure) {
          alert("Sorry, for some reason the text of this page is unavailable. Searching will not work.");
        }
        return false;
      }

      for (var i = 0; i < searchArray.length; i++) {
        targetcontent = this.doHighlight(targetcontent, searchArray[i], highlightStartTag, highlightEndTag);
      }

      return targetcontent;
    }
    
});
