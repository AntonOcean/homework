from threading import Timer
from aiohttp import web, ClientSession
import os
import asyncio
from datetime import datetime

from settings import config


def read_file(path):
    with open(path) as f:
        return f.read()


def save_file(path, text):
    with open(path, 'w') as f:
        f.write(text)


async def index(request):
    conf = app.get('config')
    text = f"Сервер запущен с конигурацией:\n" \
           f"--Директория: {conf['base_dir']}\n" \
           f"--Список нод: {conf['node_list']}\n" \
           f"--Сохранение файлов: {conf['save_file']}\n" \
           f"--Время жизни файлов: {conf['time_to_live']}\n\n" \
           f"Файлы на сервере: {os.listdir(conf['base_dir'])}"
    return web.Response(text=text)


async def search(request):
    time_start = datetime.now()

    file = request.match_info.get('file_name')
    conf = app.get('config')
    path = os.path.join(conf['base_dir'], file)
    result = '404: Файл не найден'
    request_from_node = 'aiohttp' in request.headers['User-Agent']

    if os.path.exists(path):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, read_file, path)
        if request_from_node:
            return web.Response(text=result, status=200)

    elif request_from_node:
        return web.Response(status=404)

    else:
        node_list = conf['node_list']
        for node in node_list:
            url = f"http://{node['host']}:{node['port']}/{file}"
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        result = await resp.text()
                        if conf['save_file']:
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, save_file, path, result)
                            timer = conf['time_to_live']
                            time_live_thread = Timer(timer, os.remove, args=(path, ))
                            time_live_thread.start()
                        break

    time_end = datetime.now()
    time_wait = time_end - time_start
    return web.Response(text=f"Файл: {result}\nВремя ожидания: {time_wait}")


app = web.Application()

app.add_routes([
    web.get('/', index),
    web.get('/{file_name}', search),
])

app['config'] = config
web.run_app(app, port=8088)
