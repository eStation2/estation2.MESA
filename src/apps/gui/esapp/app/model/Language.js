Ext.define('esapp.model.Language', {
    extend : 'esapp.model.Base',

    fields: [
       {name: 'langcode'},
       {name: 'langdescription'},
       {name: 'selected', type: 'boolean'}
    ]

});