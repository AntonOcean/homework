from aiohttp import web, ClientSession
import os
from time import sleep
import asyncio
from datetime import datetime
import aiohttp_jinja2

from async_file_storage.async_file_storage.settings import BASE_DIR


@aiohttp_jinja2.template('index.html')
async def handle(request):
    error = None
    config = request.app.get('config')
    if request.method == 'POST':
        data = await request.post()
        file_text = data.get('file_text')
        if file_text:
            path = os.path.join(BASE_DIR, config['base_dir'], file_text.filename)
            url = f"http://localhost:{config['node_list'][0]['port']}/{file_text.filename}"
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 404:
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, save_file, path, str(file_text.file.read()))
                    else:
                        error = 1
    text = {
        'error': error,
        'base_dir': config['base_dir'],
        'node_list': config['node_list'],
        'save_file': config['save_file'],
        'time_to_live': config['time_to_live'],
        'file_on': os.listdir(os.path.join(BASE_DIR, config['base_dir']))
    }
    return text


def read_file(path):
    with open(path) as f:
        return f.read()


def save_file(path, text):
    with open(path, 'w') as f:
        f.write(text)


def delete_file(path, timer):
    sleep(timer)
    os.remove(path)


async def download_wiki(url, params):
    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.text()
            else:
                return None


async def search(request):
    time_start = datetime.now()

    config = request.app.get('config')
    file_name = request.match_info.get('file_name')
    path = os.path.join(BASE_DIR, config['base_dir'], file_name)
    result = '404: Файл не найден'
    status_code = 404
    request_from_node = request.query.get('request_from_node')
    loop = asyncio.get_event_loop()

    if os.path.exists(path):
        result = await loop.run_in_executor(None, read_file, path)
        if request_from_node:
            return web.Response(text=result, status=200)

    elif request_from_node:
        return web.Response(status=404)

    else:
        node_list = config['node_list']
        coroutines_list = []
        for node in node_list:
            url = f"http://{node['host']}:{node['port']}/{file_name}"
            params = {'request_from_node': 1}
            coroutines_list.append(download_wiki(url, params))

        for task in asyncio.as_completed(coroutines_list):
            result = await task
            if result:
                status_code = 200
                if config['save_file']:
                    await loop.run_in_executor(None, save_file, path, result)
                    timer = config['time_to_live']
                    await loop.run_in_executor(None, delete_file, path, timer)
                break

    time_end = datetime.now()
    time_wait = time_end - time_start
    return web.Response(text=f"Файл: {result}\nВремя ожидания: {time_wait}", status=status_code)
