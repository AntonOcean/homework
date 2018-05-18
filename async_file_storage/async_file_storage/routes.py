from async_file_storage.async_file_storage.views import handle, search


def setup_routes(app):
    app.router.add_get('/', handle)
    app.router.add_post('/', handle)
    app.router.add_get('/{file_name}', search)