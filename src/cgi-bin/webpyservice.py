#!/usr/bin/python

import sys, os
abspath = os.path.dirname(__file__)
#sys.path.append(abspath)
os.chdir(abspath)
import web


WEBPY_COOKIE_NAME = "webpy_session_id"

urls = (
    "/ext", "ext",
    "/MyApp", "myapp",
    "/template", "templatepage",
    "/(.+)/(.+)", "acquisition",
    "/(.+)/", "acquisition",
    "/", "acquisition")

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()
#session = web.session.Session(app, web.session.DiskStore('../logs/mstmp/webpySessions'))


class ext:
    def GET(self):
        render = web.template.render('/srv/www/JurDev/eStation2/apps/MyApp/ext/')
        return render.index()


class myapp:
    #def __init__(self):
    #    self.param1 = "hoi"

    def GET(self):
        #return web.ctx
        render = web.template.render('/srv/www/JurDev/eStation2/apps/MyApp/')
        #render = web.template.render('/srv/www/JurDev/eStation2/apps/MyApp/build/testing/MyApp/')
        return render.index()


class acquisition:
    def __init__(self):
        self.lang = "en"

    def GET(self):
        #return web.ctx
        render = web.template.render(abspath+'/templates/')
        getparam = web.input(lang=self.lang)

        return render.index(getparam.lang)


class templatepage:
    def __init__(self):
        self.render = web.template.render(abspath+'/templates/')

    def GET(self):
        getInput=web.input(name="World")
        return self.render.mytemplate("mytitle", getInput.name)

if __name__ == "__main__":
    app.run()