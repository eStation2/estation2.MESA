__author__ = 'tklooju'


def reloadallmodules():
    from config import es_constants
    from database import connectdb
    from database import querydb
    from apps.productmanagement import datasets
    from apps.productmanagement import products
    from lib.python import functions

    import webpy_esapp
    # import webpy_esapp_helpers
    # import reloader
    import imp

    imp.reload(es_constants)
    imp.reload(connectdb)
    imp.reload(functions)
    imp.reload(querydb)
    imp.reload(datasets)
    imp.reload(products)
    # imp.reload(webpy_esapp_helpers)
    imp.reload(webpy_esapp)


    # reloader.enable()
    # # print reloader.get_dependencies(es_constants)
    # reloader.reload(es_constants)
    # reloader.reload(connectdb)
    # reloader.reload(functions)
    # reloader.reload(querydb)
    # reloader.reload(datasets)
    # reloader.reload(products)
    # # reloader.reload(webpy_esapp)
    # reloader.reload(webpy_esapp_helpers)
    # reloader.disable()
    # # reloader.reload(sys.modules['config'])

    # from config import es_constants as constantsreloaded
    # for setting in constantsreloaded.es2globals:
    #     logger.info(setting + ': ' + str(es_constants.es2globals[setting]))
    #
    # a solution that is simple and drastic, but it may not work with integrated development environments (IDEs)
    # sys.modules.clear()
    #
    # # A solution that is a bit more careful and is compatible with IDEs
    # if globals(  ).has_key('init_modules'):
    #     # second or subsequent run: remove all but initially loaded modules
    #     for m in sys.modules.keys(  ):
    #         if m not in init_modules:
    #             del(sys.modules[m])
    # else:
    #     # first run: find out which modules were initially loaded
    #     init_modules = sys.modules.keys(  )
    #
