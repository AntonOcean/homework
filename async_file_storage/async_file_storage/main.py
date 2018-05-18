from aiohttp import web
import aiohttp_jinja2
import jinja2
import os

from async_file_storage.async_file_storage.routes import setup_routes
from async_file_storage.async_file_storage.settings import config

app = web.Application()
setup_routes(app)
app['config'] = config
aiohttp_jinja2.setup(
    app, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
web.run_app(app, port=8081)
# web.run_app(app, port=8082)
# web.run_app(app, port=8083)