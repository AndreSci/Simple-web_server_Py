from aiohttp import web
import time
import datetime
import json
import redis

PORT = 6379

# Тестировал запросы через Postman
# -----------------------------------------------------------------------------------
# GET адрес http://localhost:8080/DB
# -----------------------------------------------------------------------------------
# POST адрес http://localhost:8080/save/DB
# json в Body-raw-(JSON(application.json)   {"name": "Andrew", "password": "1111"}
# -----------------------------------------------------------------------------------
# DETELE адрес http://localhost:8080/del/DB
# -----------------------------------------------------------------------------------


def unix_time():  # Получаем юникс время для регистрации времени записи в Redis
    dt_now = datetime.datetime.now()
    unixtime = time.mktime(dt_now.timetuple())
    return unixtime


def json_write(value):  # Переделываем Json данные
    # {"value": сохранённое значение для ключа KEY или null, если ключа нет, "timestamp":

    _value = {"value": value, "timestamp": unix_time()}
    data = json.dumps(_value)

    return data


def redis_set(key, value):
    redis_client = redis.Redis(host="localhost", port=PORT, db=0)
    result = redis_client.set(name=key, value=json_write(value))
    redis_client.close()

    return result


def redis_get(key):
    redis_client = redis.Redis(host="localhost", port=PORT, db=0)

    _value = redis_client.get(key)
    redis_client.close()
    return _value


def redis_del(key):
    redis_client = redis.Redis(host="localhost", port=PORT, db=0)

    result = redis_client.delete(key)
    redis_client.close()

    return result


async def set_key(request):
    data = await request.json()
    key = request.match_info['key']

    result = redis_set(key, data)
    return web.Response(text="Save - {}".format(result))


async def get_key(request):
    key = request.match_info['key']

    result = redis_get(key)
    if result:
        result = result.decode("utf-8")
    else:
        return web.json_response(None)

    return web.json_response(result)


async def delete_key(request):
    key = request.match_info['key']
    result = redis_del(key)
    return web.Response(text="Delete - {}".format(result))


if __name__ == "__main__":
    app = web.Application()
    # POST-запрос /save/KEY , принимающий значение VALUE и сохраняющий его (KEY - строка без пробелов, VALUE - JSON)
    # app.router.add_route('POST', '/save/', save_key)
    app.router.add_route('POST', '/save/{key}', set_key, expect_handler=web.Request.json)
    # GET-запрос /show/KEY, возвращающий JSON следующего вида:
    # {"value": сохранённое значение для ключа KEY или null, если ключа нет, "timestamp": unix-time записи ключа
    # (т.е. запроса /save/KEY)
    app.router.add_route('GET', '/{key}', get_key)
    # DELETE-запрос /del/KEY удаляющий пару ключ-значение
    app.router.add_route('DELETE', '/del/{key}', delete_key)

    web.run_app(app)
