/**
 * Plugin that allows inline editing of the titles of the panels in a TabPanel on dblclick.
 */
Ext.define('esapp.TabTitleEditor', {
    extend: "Ext.plugin.Abstract",
    alias: 'plugin.tabtitleedit',

    init : function (cmp) {
        this.setCmp(cmp);
        cmp.on({
            render: this.onRender,
            destroy: this.onDestroy,
            single: true
        });
    },
    onRender: function(cmp){
        // cmp.titleEditor = new Ext.Editor(new Ext.form.TextField({
        //     allowBlank: false,
        //     enterIsSpecial: true
        // }), {
        //     autoSize: 'width',
        //     completeOnEnter: true,
        //     cancelOnEsc: true,
        //     listeners: {
        //         complete: function(editor, value){
        //             console.info(this.idDelimiter);
        //             var item = Ext.getCmp(editor.boundEl.id.split(this.idDelimiter)[1]);
        //             this.setTitle(value);
        //         },
        //         scope: this
        //     }
        // });

        cmp.titleEditor = new Ext.Editor({
            // update the innerHTML of the bound element when editing completes
            updateEl: true,
            alignment: 'l-l',
            autoSize: {
                width: 'boundEl'
            },
            field: {
                xtype: 'textfield',
                border: 1,
                style: {
                    borderColor: 'white',
                    borderStyle: 'solid'
                }
            },
            listeners: {
                complete: function(editor, value, startValue, eOpts){
                    // console.info(cmp);   // cmp is the workspace
                    // console.info(value);
                    cmp.title = value;
                    cmp.workspacename = value;
                    cmp.up().updateLayout();
                    if (!cmp.isNewWorkspace && (value != startValue)){
                        cmp.getController().saveWorkspaceName();
                    }
                }
            }
        });

        // console.info(cmp);
        cmp.mon(cmp.tab.btnInnerEl, {        // cmp.strip
            dblclick: function(e){
                // console.info(e);
                var t = e.getTarget();
                // console.info(t);
                if(t && !t.close && this.titleEditable !== false){
                    this.titleEditor.width = t.width;
                    this.titleEditor.startEdit(t, t.textContent);
                }
            },
            scope: cmp
        });
    },
    onDestroy: function(cmp){
        if(cmp.titleEditor){
            cmp.titleEditor.destroy();
            delete cmp.titleEditor;
        }
    }
});

