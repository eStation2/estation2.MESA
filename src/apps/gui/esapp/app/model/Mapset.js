Ext.define('esapp.model.MapSet', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'mapsetcode'},
        {name: 'defined_by'},
        {name: 'descriptive_name'},
        {name: 'description'},
        {name: 'resolutioncode'},
        {name: 'center_of_pixel', type: 'boolean'},
        {name: 'pixel_size_x'},
        {name: 'pixel_size_y'},
        {name: 'proj_code'},
        // {name: 'projection_descriptive_name'},
        // {name: 'srs_wkt'},
        {name: 'bboxcode'},
        // {name: 'bbox_descriptive_name'},
        {name: 'predefined', type: 'boolean'},
        {name: 'upper_left_long'},
        {name: 'upper_left_lat'},
        {name: 'lower_right_long'},
        {name: 'lower_right_lat'},
        {name: 'footprint_image'},
        // {name: 'resolution_descriptive_name'},
        // {name: 'pixel_shift_long', type: 'number'},
        // {name: 'pixel_shift_lat', type: 'number'},
        {name: 'ingestions_assigned'}
    ]

    // fields: [
    //     {name: 'mapsetcode'},
    //     {name: 'defined_by'},
    //     {name: 'descriptive_name'},
    //     {name: 'description'},
    //     {name: 'srs_wkt'},
    //     {name: 'upper_left_long'},
    //     {name: 'pixel_shift_long'},
    //     {name: 'rotation_factor_long'},
    //     {name: 'upper_left_lat'},
    //     {name: 'pixel_shift_lat'},
    //     {name: 'rotation_factor_lat'},
    //     {name: 'pixel_size_x'},
    //     {name: 'pixel_size_y'},
    //     {name: 'footprint_image'},
    //     {name: 'ingestions_assigned'}
    // ]
});