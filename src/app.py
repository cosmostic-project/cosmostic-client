# avoid noconsole error with bottle
import sys
class dummyStream:
    def write(data, *args, **kwargs): pass
sys.stdout = dummyStream()
sys.stderr = dummyStream()

from bottle import run, template, route, error, request, response
from gevent import monkey; monkey.patch_all()
import json

import api


@error(404)
def not_found(_):
    """
    Handles the 404 error by redirecting the user to the home page.
    """
    response.status = 303 if request.get('SERVER_PROTOCOL') == "HTTP/1.1" else 302
    response.set_header('Location', '/')
    return

@route('/', method='GET')
def status():
    """
    Renders the status page of the COSMOSTIC client.
    """
    return template("""<li>COSMOSTIC CLIENT : <span style="color: green; font-weight: bold;">UP</span></li><li>COSMOSTIC API : <span style="color: {{"green" if api_status else "red"}}; font-weight: bold;">{{"UP" if api_status else "DOWN"}}</span></li><li>MOJANG API : <span style="color: {{"green" if mojang_api_status else "red"}}; font-weight: bold;">{{"UP" if mojang_api_status else "DOWN"}}</span></li>""", api_status=api.api_ping(), mojang_api_status=api.mojang_api_ping())


@route('/capes/<username>.png', method='GET')
def cape(username:str):
    """
    Retrieves the cape texture of a Minecraft user by their username.

    Args:
        username (str): The Minecraft username.

    Returns:
        image/png: The cape texture of the user if successful, 404 overwise.
    """
    # get user uuid by username
    user_uuid = api.get_uuid(username)
    if not user_uuid:
        response.status = 404
        return
    
    # get cape uuid
    cape_uuid = api.get_user_cape(user_uuid)
    if not cape_uuid:
        response.status = 404
        return
    
    # get cape texture
    cape_texture = api.get_cape_texture(cape_uuid)
    if not cape_texture:
        response.status = 404
        return
    
    # send texture
    response.content_type = 'image/png'
    response.headers['Content-Disposition'] = 'attachment; filename="%s.png"' % username
    return cape_texture


@route('/users/<username>.cfg', method='GET')
def user(username:str):
    """
    Retrieves the user configuration file for a given Minecraft username.

    Args:
        username (str): The Minecraft username.

    Returns:
        str: The user configuration file in JSON format if successful, 404 overwise.
    """
    # get user uuid by username
    user_uuid = api.get_uuid(username)
    if not user_uuid:
        response.status = 404
        return
    
    # get user accessories
    accessories = api.get_user_accessories(user_uuid)
    if not accessories:
        response.status = 404
        return
    
    # create user config
    config = api.create_user_config(accessories)
    
    # send config file
    response.content_type = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename="%s.cfg"' % username
    return json.dumps(config)

@route('/models/<uuid>.cfg', method='GET')
def model(uuid:str):
    """
    Retrieves the model of an accessory for a given accessory UUID.

    Parameters:
        uuid (str): The accessory UUID.

    Returns:
        str: The accessory model in JSON format if successful, 404 overwise.
    """
    # get accessory model
    model = api.get_accessory_model(uuid)
    if not model:
        response.status = 404
        return
    
    response.content_type = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename="%s.cfg"' % uuid
    return json.dumps(model)

@route('/textures/<uuid>.png', method='GET')
def texture(uuid:str):
    # get accessory texture
    """
    Retrieves the texture of an accessory for a given accessory UUID.

    Parameters:
        uuid (str): The accessory UUID.

    Returns:
        image/png: The accessory texture if successful, 404 overwise.
    """
    texture = api.get_accessory_texture(uuid)
    if not texture:
        response.status = 404
        return
    
    # send texture
    response.content_type = 'image/png'
    response.headers['Content-Disposition'] = 'attachment; filename="%s.png"' % uuid
    return texture


if __name__ == '__main__':
    # run with async server
    run(host='localhost', port=80, server='gevent', quiet=True)