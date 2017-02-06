// This is an override because it must be loaded very early, possibly before Ext.app.Application
// in dev mode so that Ext.application() can be called.
// Being an override also ensures that it is only included in a built app if Ext.app.Application
// is present.
//
// @override Ext.app.Application

/**
 * @method application
 * @member Ext
 * Loads Ext.app.Application class and starts it up with given configuration after the
 * page is ready.
 *
 * See `Ext.app.Application` for details.
 *
 * @param {Object/String} config Application config object or name of a class derived
 * from Ext.app.Application.
 */
Ext.application = function(config) {
    var createApp = function(App) {
            // This won't be called until App class has been created.
            Ext.onReady(function() {
                Ext.app.Application.instance = new App();
            });
        },
        paths = config.paths,
        ns;

    if (typeof config === "string") {
        Ext.require(config, function() {
            createApp(Ext.ClassManager.get(config));
        });
    }
    else {
        config = Ext.apply({
            extend: 'Ext.app.Application' // can be replaced by config!
        }, config);

        // We have to process `paths` before creating Application class,
        // or `requires` won't work.
        Ext.app.setupPaths(config.name, config.appFolder, config.paths);

        config['paths processed'] = true;

        // Let Ext.define do the hard work but don't assign a class name.
        Ext.define(config.name + ".$application", config,
            function() {
                createApp(this);
            });
    }
};

(Ext.app || (Ext.app = {})).setupPaths = function(appName, appFolder, paths) {
    var manifestPaths = Ext.manifest,
        ns;

    // Ignore appFolder:null
    if (appName && appFolder !== null) {
        manifestPaths = manifestPaths && manifestPaths.paths;

        // If the manifest has paths, only honor appFolder if defined. If the
        // manifest has no paths (old school mode), then we want to default an
        // unspecified appFolder value to "app". Sencha Cmd will pass in paths
        // to configure the loader via the "paths" property of the manifest so
        // we don't want to try and be "helpful" in that case.
        if (!manifestPaths || appFolder !== undefined) {
            Ext.Loader.setPath(appName, (appFolder === undefined) ? 'app' : appFolder);
        }
    }

    if (paths) {
        for (ns in paths) {
            if (paths.hasOwnProperty(ns)) {
                Ext.Loader.setPath(ns, paths[ns]);
            }
        }
    }
};
