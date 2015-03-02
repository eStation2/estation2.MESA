__author__ = 'tklooju'


def reloadallmodules():
    from config import es_constants
    from database import connectdb
    from database import querydb
    from apps.productmanagement import datasets
    from apps.productmanagement import products

    import reloader
    reloader.enable()
    # print reloader.get_dependencies(es_constants)
    reloader.reload(es_constants)
    reloader.reload(connectdb)
    reloader.reload(querydb)
    reloader.reload(datasets)
    reloader.reload(products)
    reloader.disable()
    # reloader.reload(sys.modules['config'])

    # from config import es_constants as constantsreloaded
    # for setting in constantsreloaded.es2globals:
    #     logger.info(setting + ': ' + str(es_constants.es2globals[setting]))