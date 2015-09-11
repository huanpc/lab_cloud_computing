__author__ = 'huanpc'


import asyncio
import json
from aiohttp import web
import Model

@asyncio.coroutine
def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(body=text.encode('utf-8'))

@asyncio.coroutine
def get_app(request):
    name = request.match_info.get('name')
    raw_data = Model.get_app(name)
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@asyncio.coroutine
def get_all_app(request):
    raw_data = Model.get_app()
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))


@asyncio.coroutine
def get_policy(request):
    policy_uuid = request.match_info.get('policy_uuid')
    raw_data = Model.get_policy(policy_uuid,'')
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@asyncio.coroutine
def get_policy_by_app_uuid(request):
    app_uuid = request.match_info.get('app_uuid')
    raw_data = Model.get_policy_by_app_uuis(app_uuid)
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@asyncio.coroutine
def get_all_policy(request):
    raw_data = Model.get_policy()
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@asyncio.coroutine
def get_cron(request):
    cron_uuid = request.match_info.get('cron_uuid')
    raw_data = Model.get_cron(cron_uuid)
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@asyncio.coroutine
def get_all_cron(request):
    raw_data = Model.get_cron()
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@asyncio.coroutine
def delete(request):
    if str(request.path).__contains__('apps'):
        result = Model.delete_app(request.match_info.get('name'))
    elif str(request.path).__contains__('policies'):
        result = Model.delete_policy(request.match_info.get('policy_uuid'))
    else:
        result = Model.delete_cron(request.match_info.get('cron_uuid'))
    if result:
        return web.Response(status=200,body='OK'.encode('utf-8'))
    return web.Response(status=200,body='Error!'.encode('utf-8'))

@asyncio.coroutine
def delete_all(request):
    if str(request.path).__contains__('apps'):
        result = Model.delete_app()
    elif str(request.path).__contains__('policies'):
        result = Model.delete_policy()
    else:
        result = Model.delete_cron()
    if result:
        return web.Response(status=200,body='OK'.encode('utf-8'))
    return web.Response(status=200,body='Error!'.encode('utf-8'))


@asyncio.coroutine
def add(request):
    if str(request.path).__contains__('apps'):
        object = Model.App
    elif str(request.path).__contains__('policies'):
        object = Model.Policy
    else:
        object = Model.Cron

    data = yield from request.text()
    json_data = json.loads(object,data)
    is_ok = Model.insert_json_data(json_data)
    if(is_ok):
        return web.Response(status=200,body='OK'.encode('utf-8'))
    return web.Response(status=200,body='Error!'.encode('utf-8'))

@asyncio.coroutine
def update(request):
    app_name = request.match_info.get('name')
    if str(request.path).__contains__('apps'):
        object = Model.App
    elif str(request.path).__contains__('policies'):
        object = Model.Policy
    else:
        object = Model.Cron
    result = Model.update(object,app_name)
    if(result):
        return web.Response(status=200,body='OK'.encode('utf-8'))
    return web.Response(status=200,body='Error!'.encode('utf-8'))

@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    # Get app info by name
    app.router.add_route('GET', '/apps/{name}', get_app)
    # Get all app info in database
    app.router.add_route('GET', '/apps', get_all_app)
    # Get policy by policy_uuid
    app.router.add_route('GET', '/policies/{policy_uuid}', get_policy)
    # Get policy by app uuid
    app.router.add_route('GET', '/policies/apps/{app_uuid}', get_policy)
    # Get all policy in database
    app.router.add_router('GET','/policies',get_all_policy)
    # Delete all app info in database
    app.router.add_router('DELETE','/apps/{name}',delete)
    app.router.add_router('DELETE','/apps',delete_all)
    # Delete policy by policy_uuid
    app.router.add_router('DELETE','/policies/{policy_uuid}',delete)
    # Delete all
    app.router.add_router('DELETE','/policies',delete_all)
    # Create new
    app.router.add_router('POST','/apps',add)
    app.router.add_router('POST','/policies',add)
    app.router.add_router('POST','/crons',add)
    #Update by app name
    app.router.add_router('PUT','/apps/{name}',update)
    app.router.add_router('PUT','/policies/{policy_uuid}',update)
    app.router.add_router('PUT','/crons/{cron_uuid}',update)

    srv = yield from loop.create_server(app.make_handler(),'127.0.0.1', 5050)
    print("Server started at http://127.0.0.1:5050")
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
