import cherrypy, json, os
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from jinjahelper import JinjaHelper
from cp_sqlalchemy import SQLAlchemyTool, SQLAlchemyPlugin

import settings
from model import Base, PopModel

class App:
    @cherrypy.expose
    def index(self):
        HERE = os.path.dirname(os.path.abspath(__file__))
        jh = JinjaHelper(HERE)
        tpl = jh.get_template('index.html')
        return tpl.render([])

class Webservice:
    @property
    def db(self):
        return cherrypy.request.db

    @cherrypy.expose
    def index(self):
        pops = self.db.query(PopModel).all()
        results: PopModel = [
            {
                "id": pop.id,
                "name": pop.name,
                "color": pop.color
            } for pop in pops]
        return json.dumps(results)

def run():
    cherrypy.tools.db = SQLAlchemyTool()

    global_config = {
        'global' : {
            'server.socket_host' : '0.0.0.0',
            'server.socket_port' : 8080
        }
    }

    app_config = {
        '/': {
            'tools.staticdir.root': os.getcwd(),
            'tools.db.on': True
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static'
        }
    }

    cherrypy.config.update(global_config)

    cherrypy.tree.mount(App(), '/', config=app_config)
    cherrypy.tree.mount(Webservice(), '/pops', config=app_config)

    sqlalchemy_plugin = SQLAlchemyPlugin(
        cherrypy.engine, Base,
            '{engine}://{username}:{password}@{host}/{db_name}'.format(
                **settings.SQLSERVER
            ),
        echo=True
    )

    sqlalchemy_plugin.subscribe()
    sqlalchemy_plugin.create()

    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    run()
