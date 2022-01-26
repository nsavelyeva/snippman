import os
import errno
import json


CONFIG_FOLDER = os.path.dirname(os.path.abspath(__file__))
CUSTOM_SETTINGS_FILE = os.path.join(CONFIG_FOLDER, "custom.json")
with open(CUSTOM_SETTINGS_FILE, "r") as _f:
    CUSTOM_SETTINGS = json.loads(_f.read().strip())


def mkdir_if_not_exists(abs_path, dir_name):
    full_path = os.path.normpath(os.path.join(abs_path, dir_name))
    try:
        os.makedirs(full_path)
    except OSError as err:
        if err.errno != errno.EEXIST:
            print("Could not create directory %s: %s" % (full_path, err))
            raise
    return True


class BaseConf(object):
    """
    Base configuration including settings configurable by user
    """

    APP_FOLDER = CONFIG_FOLDER[:-5]  # strip "/conf" (Linux) or "\conf" (Windows)
    CONFIG_FOLDER = CONFIG_FOLDER
    SETTINGS_FILE = CUSTOM_SETTINGS_FILE
    DATABASE = os.path.join(CONFIG_FOLDER, "..", "sqlite3.db")
    SQLALCHEMY_DATABASE_URI = "sqlite:///%s" % DATABASE
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.normpath("app/uploads")  # will be created if does not exist
    DOWNLOAD_FOLDER = "downloads"  # will be created if does not exist
    ALLOWED_EXTENSIONS = ["xlsx", "json"]
    GDOCS_CREDS_FILENAME = "gdocs.json"
    GDOCS_CREDS = os.path.join(CONFIG_FOLDER, GDOCS_CREDS_FILENAME)
    GDOCS_SPREADSHEET_ID = CUSTOM_SETTINGS["GDOCS_SPREADSHEET_ID"]
    TESTING = False
    # Below is configurable by user:
    ITEMS_PER_PAGE = CUSTOM_SETTINGS["ITEMS_PER_PAGE"]
    MAX_BACKUPS = CUSTOM_SETTINGS["MAX_BACKUPS"]
    EMAIL = CUSTOM_SETTINGS["EMAIL"]


class DevConf(BaseConf):
    """
    Development configuration
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProdConf(BaseConf):
    """
    Production configuration
    """

    DEBUG = False
    SQLALCHEMY_ECHO = False
