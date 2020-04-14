from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
__author__ = 'tklooju'


def reloadallmodules():
    from config import es_constants
    from database import connectdb
    from database import querydb
    from apps.productmanagement import datasets
    from apps.productmanagement import products
    from lib.python import functions
    import webpy_esapp
    import webpy_esapp_helpers

    from importlib import reload

    es_constants = reload(es_constants)
    connectdb = reload(connectdb)
    functions = reload(functions)
    querydb = reload(querydb)
    datasets = reload(datasets)
    products = reload(products)
    webpy_esapp = reload(webpy_esapp)
    webpy_esapp_helpers = reload(webpy_esapp_helpers)

    # import reloader
    # import imp
    # imp.reload(module)
    #
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
