Ext.define('esapp.model.Logo', {
    extend: 'esapp.model.Base',

    fields: [
        {name: 'logo_id'},
        {name: 'logo_filename', type:'string'},
        {name: 'logo_description', type:'string'},
        {name: 'active', type: 'boolean'},
        {name: 'deletable', type: 'boolean'},
        {name: 'defined_by', type:'string'},
        {name: 'isdefault', type: 'boolean'},
        {name: 'orderindex_defaults', type:'integer'},
        {name:'src', type:'string'},
        {name:'width', type:'string'},
        {name:'height', type:'string'}
    ]
});
