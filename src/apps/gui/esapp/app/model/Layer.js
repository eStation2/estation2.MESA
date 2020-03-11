Ext.define('esapp.model.Layer', {
    extend: 'esapp.model.Base',

    fields: [
        {name: 'layerid'},
        {name: 'layerlevel'},
        {name: 'layername'},
        {name: 'description'},
        {name: 'filename'},
        {name: 'layerorderidx'},
        {name: 'layertype'},
        {name: 'polygon_outlinecolor'},
        {name: 'polygon_outlinewidth'},
        {name: 'polygon_fillcolor'},
        {name: 'polygon_fillopacity'},
        {name: 'feature_display_column'},
        {name: 'feature_highlight_outlinecolor'},
        {name: 'feature_highlight_outlinewidth'},
        {name: 'feature_highlight_fillcolor'},
        {name: 'feature_highlight_fillopacity'},
        {name: 'feature_selected_outlinecolor'},
        {name: 'feature_selected_outlinewidth'},
        {name: 'enabled', type: 'boolean'},
        {name: 'deletable', type: 'boolean'},
        {name: 'background_legend_image_filename'},
        {name: 'projection'},
        {name: 'submenu'},
        {name: 'menu'},
        {name: 'defined_by'},
        {name: 'open_in_mapview', type: 'boolean'},
        {name: 'provider'}
    ]
});
