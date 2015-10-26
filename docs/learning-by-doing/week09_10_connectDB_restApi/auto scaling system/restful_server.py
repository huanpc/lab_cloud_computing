import base64

__author__ = 'huanpc'


import asyncio
import json
from aiohttp import web
import Model
import constant
import hashlib

# config
HOST = '127.0.0.1'
PORT = 1111
USER_NAME = 'huanpc'
PASWD = '12345678'
#
def check_auth(request):
    request = request.split(' ')
    raw_data = base64.b64decode(request[1]).decode('utf-8')
    author = raw_data.split(':')
    return (author[0]==USER_NAME and author[1]==PASWD)

def authenticate(handler):
    def wapper(request, *arg1, **arg2):
        if request.headers.get('AUTHORIZATION') is None:
            return web.Response(status=401,body='{"message":"Authentication Required"}'.encode('utf-8'))
        elif not check_auth(request.headers.get('AUTHORIZATION')):
            return web.Response(status=401,body='{"message":"Unauthorized Access"}'.encode('utf-8'))
        else:
            return handler(request, *arg1, **arg2)
    return wapper

@authenticate
@asyncio.coroutine
def get_app(request):
    name = request.match_info.get('name')
    raw_data = Model.get_app(name)
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@authenticate
@asyncio.coroutine
def get_all_app(request):
    raw_data = Model.get_app()
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))


@authenticate
@asyncio.coroutine
def get_policy(request):
    policy_uuid = request.match_info.get('policy_uuid')
    raw_data = Model.get_policy(policy_uuid)
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@authenticate
@asyncio.coroutine
def get_policy_by_app_uuid(request):
    app_uuid = request.match_info.get('app_uuid')
    raw_data = Model.get_policy_by_app_uuid(app_uuid)
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@authenticate
@asyncio.coroutine
def get_all_policy(request):
    raw_data = Model.get_policy()
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@authenticate
@asyncio.coroutine
def get_cron(request):
    cron_uuid = request.match_info.get('cron_uuid')
    raw_data = Model.get_cron(cron_uuid)
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@authenticate
@asyncio.coroutine
def get_all_cron(request):
    raw_data = Model.get_cron()
    if raw_data!=None:
        data = str(raw_data)
        return web.Response(status=200,body=data.encode('utf-8'))
    return web.Response(status=200,body='Not found!'.encode('utf-8'))

@authenticate
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

@authenticate
@asyncio.coroutine
def delete_policy_of_app(request):
    app_uuid = request.match_info.get('app_uuid')
    if Model.delete_policy_by_app_uuid(app_uuid):
        return web.Response(status=200,body='OK'.encode('utf-8'))
    return web.Response(status=200,body='Error!'.encode('utf-8'))

@authenticate
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

@authenticate
@asyncio.coroutine
def add(request):
    if str(request.path).__contains__('apps'):
        object = Model.App
    elif str(request.path).__contains__('policies'):
        object = Model.Policy
    else:
        object = Model.Cron

    data = yield from request.text()
    json_data = json.loads(data)
    is_ok = Model.insert_json_data(object,json_data)
    if(is_ok):
        return web.Response(status=200,body='OK'.encode('utf-8'))
    return web.Response(status=200,body='Error!'.encode('utf-8'))

@authenticate
@asyncio.coroutine
def update(request):
    app_name = request.match_info.get('name')
    raw_data = yield from request.text()
    json_data = json.loads(raw_data)
    if str(request.path).__contains__('apps'):
        object = Model.App
    elif str(request.path).__contains__('policies'):
        object = Model.Policy
    else:
        object = Model.Cron
    result = Model.update(object,app_name,json_data)
    if(result):
        return web.Response(status=200,body='OK'.encode('utf-8'))
    return web.Response(status=200,body='Error!'.encode('utf-8'))

@authenticate
@asyncio.coroutine
def update_app(request):
    app_name = request.match_info.get('name')
    raw_data = yield from request.text()
    json_data = json.loads(raw_data)
    result = Model.update_app(app_name,json_data)
    if(result):
        return web.Response(status=200,body='OK'.encode('utf-8'))
    return web.Response(status=200,body='Error!'.encode('utf-8'))

@authenticate
@asyncio.coroutine
def update_cron(request):
    cron_uuid= request.match_info.get('cron_uuid')
    raw_data = yield from request.text()
    json_data = json.loads(raw_data)
    result = Model.update_cron(cron_uuid,json_data)
    if(result):
        return web.Response(status=200,body='OK'.encode('utf-8'))
    return web.Response(status=200,body='Error!'.encode('utf-8'))

@authenticate
@asyncio.coroutine
def update_policy(request):
    policy_uuid = request.match_info.get('policy_uuid')
    raw_data = yield from request.text()
    json_data = json.loads(raw_data)
    result = Model.update_policy(policy_uuid,json_data)
    if(result):
        return web.Response(status=200,body='OK'.encode('utf-8'))
    return web.Response(status=200,body='Error!'.encode('utf-8'))

@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    # app
    app.router.add_route('GET', '/apps/{name}', get_app)
    app.router.add_route('GET', '/apps', get_all_app)
    app.router.add_route('POST','/apps',add)
    app.router.add_route('PUT','/apps/{name}',update_app)
    app.router.add_route('DELETE','/apps/{name}',delete)
    app.router.add_route('DELETE','/apps/policies/{app_uuid}',delete_policy_of_app)
    app.router.add_route('DELETE','/apps',delete_all)
    # cron
    app.router.add_route('GET', '/crons/{name}', get_cron)
    app.router.add_route('GET', '/crons', get_all_cron)
    app.router.add_route('POST','/crons',add)
    app.router.add_route('PUT','/crons/{cron_uuid}',update_cron)
    # policy
    app.router.add_route('GET', '/policies/{policy_uuid}', get_policy)
    app.router.add_route('GET', '/policies/apps/{app_uuid}', get_policy_by_app_uuid)
    app.router.add_route('GET','/policies',get_all_policy)
    app.router.add_route('POST','/policies',add)
    app.router.add_route('PUT','/policies/{policy_uuid}',update_policy)
    app.router.add_route('DELETE','/policies/{policy_uuid}',delete)
    app.router.add_route('DELETE','/policies',delete_all)

    srv = yield from loop.create_server(app.make_handler(),HOST, PORT)
    print("Server started at "+HOST+":"+str(PORT))
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
