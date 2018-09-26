/*
 * This file is generated and updated by Sencha Cmd. You can edit this file as
 * needed for your application, but these edits will have to be merged by
 * Sencha Cmd when upgrading.
 */


// console.info('before onReady');
//esapp = [];
//esapp.globals = [];
//esapp.globals['selectedLanguage'] = '';

//esapp.Utils = Ext.create('esapp.Utils');
//console.info(esapp.Utils);

/**
 * The application startup file
 */
Ext.application({
    name: 'esapp',

    requires: [
       'esapp.Application'
    ],

    extend: 'esapp.Application'

    //,mainView: 'esapp.view.main.Main'
    //,autoCreateViewport:  'esapp.view.main.Main'
	
    //-------------------------------------------------------------------------
    // Most customizations should be made to esapp.Application. If you need to
    // customize this file, doing so below this section reduces the likelihood
    // of merge conflicts when upgrading to new versions of Sencha Cmd.
    //-------------------------------------------------------------------------
});

// eof
