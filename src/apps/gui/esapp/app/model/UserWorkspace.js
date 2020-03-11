Ext.define('esapp.model.UserWorkspace', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'workspaceid', mapping: 'workspaceid'},
        {name: 'userid', mapping: 'userid'},
        {name: 'workspacename', mapping: 'workspacename'},
        {name: 'pinned', type: 'boolean', mapping: 'pinned'},
        {name: 'shownewgraph', type: 'boolean', mapping: 'shownewgraph'},
        {name: 'showbackgroundlayer', type: 'boolean', mapping: 'showbackgroundlayer'},
        {name: 'maps', mapping: 'maps'},
        {name: 'graphs', mapping: 'graphs'},
        {name: 'showindefault', type: 'boolean', mapping: 'showindefault'},
        {name: 'isrefworkspace', type: 'boolean', mapping: 'isrefworkspace'}
    ]
});
