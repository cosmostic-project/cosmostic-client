import requests
import json
import logging.config
from diskcache import Cache
from copy import deepcopy
import os


_API_BASE_URL = 'https://api.cosmostic.letz.dev'
_API_TIMEOUT = 5
_CFG_TEMPLATE = {
    "items":
    [
        # {
        #     "type": "custom",
        #     "model": "models/{uuid}",
        #     "texture": "texture/{uuid}",
        #     "active": "true"
        # },
  ]
}

# configure logging
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s > %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': './cosmostic.log',
            'maxBytes': 100*1024*1024,
            'backupCount': 1,
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['file']
    }
})

# configure caching
cache = Cache('./cache', size_limit=500*1024*1024, eviction_policy='least-recently-used')


def api_ping():
    """
    Ping the API to check its availability.

    Returns:
        bool: True if the API is available, False otherwise.
    """
    try:
        r = requests.get(_API_BASE_URL, timeout=_API_TIMEOUT)
        if r.status_code != 200:
            logging.error("API ping failed: ", r.status_code)
            return False
        
        logging.info(f"API pinged : {r.elapsed.total_seconds()}")
    except Exception as e:
        logging.error("API ping failed")
        logging.exception(e)
        return False
    return True

def mojang_api_ping():
    """
    Ping the Mojang API to check its availability.

    Returns:
        bool: True if the API is available, False otherwise.
    """
    try:
        r = requests.get('https://api.mojang.com/', timeout=_API_TIMEOUT)

        if json.loads(r.text)['Status'] != 'OK':
            logging.error("Mojang API ping failed: Status is not OK")
            return False

        logging.info(f"Mojang API pinged : {r.elapsed.total_seconds()}")
    except Exception as e:
        logging.error("Mojang API ping failed")
        logging.exception(e)
        return False
    return True


@cache.memoize()
def get_uuid(username:str):
    """
    Retrieves the UUID of a Minecraft player by their username using the Mojang API.

    Parameters:
        username (str): The Minecraft username.

    Returns:
        str or None: The UUID of the player if successful, None if the player does not exist.
        bool: False if an error occurred.
    """
    try:
        # try to get uuid by mojang api
        r = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}", timeout=_API_TIMEOUT)
        if r.status_code != 200:
            return None
        
        # extract uuid
        uuid = json.loads(r.text)['id']
    except Exception as e:
        logging.error(f"Failed to get {username} uuid from Mojang API")
        logging.exception(e)
        return False
    return uuid


def get_user_cape(user_uuid:str):
    """
    Retrieves the active cape of a user from the API.

    Args:
        user_uuid (str): The user UUID.

    Returns:
        str or None: The UUID of the user's active cape if successful, None if the user has no active cape or user not found.
        bool: False if an error occurred.
    """
    try:
        # get cape uuid
        r = requests.get(f'{_API_BASE_URL}/user/{user_uuid}/cape', timeout=_API_TIMEOUT)
        if r.status_code != 200:
            return None

        cape_uuid = json.loads(r.text)   # load response
    except Exception as e:
        logging.error(f"Failed to get {user_uuid} cape from API")
        logging.exception(e)
        return False
    return cape_uuid

def get_user_accessories(user_uuid:str):
    """
    Retrieves the active accessories of a user from the API.

    Args:
        user_uuid (str): The user UUID.

    Returns:
        list or None: A list of accessory UUIDs if successful, None if the user has no active accessories.
        bool: False if an error occurred.
    """
    # get user active accessories
    try:
        r = requests.get(f'{_API_BASE_URL}/user/{user_uuid}/accessories', timeout=_API_TIMEOUT)
        if r.status_code != 200:
            return None
        
        accessories = json.loads(r.text)   # load response
    except Exception as e:
        logging.error(f"Failed to get {user_uuid} accessories from API")
        logging.exception(e)
        return False
    return accessories if not accessories == [] else None   # return None if no accessories


@cache.memoize()
def get_cape_texture(cape_uuid:str):
    """
    Retrieves the texture of a cape from the API.

    Parameters:
        cape_uuid (str): The cape UUID.

    Returns:
        image or None: The cape texture if successful, None if cape does not exists.
        bool: False if an error occurred.
    """
    try:
        # get cape texture
        r = requests.get(f'{_API_BASE_URL}/fetch/cape/{cape_uuid}/texture', timeout=_API_TIMEOUT)
        if r.status_code != 200:
            return None
    except Exception as e:
        logging.error(f"Failed to get {cape_uuid} texture from API")
        logging.exception(e)
        return False
    return r.content

@cache.memoize()
def get_accessory_texture(texture_uuid:str):
    """
    Retrieves the texture of an accessory from the API.

    Parameters:
        accessory_uuid (str): The accessory UUID.

    Returns:
        image or None: The accessory texture if successful, None if accessory has no have a texture or does not exists.
        bool: False if an error occurred.
    """
    try:
        # get accessory texture
        r = requests.get(f'{_API_BASE_URL}/fetch/accessory/{texture_uuid}/texture', timeout=_API_TIMEOUT)
        if r.status_code != 200:
            return None
    except Exception as e:
        logging.error(f"Failed to get {texture_uuid} texture from API")
        logging.exception(e)
        return False
    return r.content

@cache.memoize()
def get_accessory_model(accessory_uuid:str):
    """
    Retrieves the model of an accessory from the API.

    Parameters:
        accessory_uuid (str): The accessory UUID.

    Returns:
        dict or None: The accessory model as a dictionary if successful, None if accessory does not exists.
        bool: False if an error occurred.
    """
    try:
        # get accessory model
        r = requests.get(f'{_API_BASE_URL}/fetch/accessory/{accessory_uuid}/model', timeout=_API_TIMEOUT)
        if r.status_code != 200:
            return None
        
        accessory_model = json.loads(r.text)   # load response
    except Exception as e:
        logging.error(f"Failed to get {accessory_uuid} model from API")
        logging.exception(e)
        return False
    return accessory_model

def create_user_config(user_accessories:list):
    """
    Generates a user configuration based on the provided list of accessories.

    Args:
        user_accessories (list): A list of accessories UUIDs.

    Returns:
        dict: User configuration dictionary. 

    """
    # create response
    response = deepcopy(_CFG_TEMPLATE)   # copy template
    for accessory_uuid in user_accessories:
        item = {
            "type": "custom",
            "model": f"models/{accessory_uuid}.cfg",
            "active": "true"
        }
        if get_accessory_texture(accessory_uuid):   # if accessory has texture
            item["texture"] = f"textures/{accessory_uuid}.png"   # add texture path
        response['items'].append(item)

    return response