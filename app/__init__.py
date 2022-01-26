from flask import Flask
from conf import conf


app = Flask(__name__, template_folder="templates")

# Create upload and download folders if they do not exist:
app.config.from_object(conf.BaseConf)
for folder in [app.config["UPLOAD_FOLDER"], "app/%s" % app.config["DOWNLOAD_FOLDER"]]:
    conf.mkdir_if_not_exists(app.config["APP_FOLDER"], folder)


app.secret_key = "In the fog an orange frog eats mosquitoes with a fork"
app.url_map.strict_slashes = False


def url_for_other_page(page):
    args = request.view_args.copy()
    args["page"] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals["url_for_other_page"] = url_for_other_page


from .views import *


