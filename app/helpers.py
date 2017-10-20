import os
import sys
import json
from werkzeug.utils import secure_filename
from .messages import fmsg, msg as gmsg
from . import db_queries


class Data(object):
    def __init__(self, values, errors):
        self.value = values   # could be any structure
        self.errors = errors  # is always a list of strings, empty if everything is OK

    def __str__(self):
        result = {"VALUE": self.value, "ERRORS": self.errors}
        return json.dumps(result, indent=4, sort_keys=True)


def allowed_file(file_name, allowed_extensions):
    """A function to check the extension of the file upload."""
    is_allowed = False
    if "." in file_name:
        extension = file_name.rsplit(".", 1)[1].lower()
        is_allowed = extension in allowed_extensions    
    return is_allowed


def upload_file(request, app_conf, file_name=None):
    # check if the POST request has the file part
    data = Data(None, [])
    if "upload" not in request.files:
        data.errors.append(gmsg(4101))
    else:
        upload = request.files["upload"]
        # if a user does not select file, browser submits an empty part without filename
        if not upload.filename:
            data.errors.append(gmsg(4111))
        elif upload:
            file_allowed = allowed_file(upload.filename, app_conf["ALLOWED_EXTENSIONS"])
            if file_allowed:
                file_name = file_name if file_name else secure_filename(upload.filename)
                data.value = os.path.join(app_conf["UPLOAD_FOLDER"], file_name)
                upload.save(data.value)
            else:
                msg = ". Allowed extensions are %s" % ", ".join(app_conf["ALLOWED_EXTENSIONS"])
                data.errors.append(gmsg(4091, msg))
    return data


def upload_gdocs_creds_file(request, app_conf):
    """Uploaded file will be stored in snippman/conf folder always as gdocs.json."""
    data = upload_file(request, app_conf)
    if data.value:
        try:
            src = os.path.normpath(data.value)
            dst = os.path.normpath(app_conf["GDOCS_CREDS"])
            creds_data = check_gdocs_creds_file(app_conf, src)
            if not creds_data.errors:
                if "win" in sys.platform and os.path.isfile(dst):  # In Windows we should remove
                    os.remove(dst)                                 # the file if it exists
                os.rename(src, dst)                                # Move from upload folder to conf
            else:
                data.errors.extend(creds_data.errors)
        except OSError as err:
            data.errors.append(gmsg(1011, err))  # Could not complete upload due to OS error
    return data


def check_gdocs_creds_file(app_conf, path=None):
    """Check JSON data can be loaded from Google creds file (used in upload and settings view)."""
    data = Data(None, [])
    path = path or app_conf["GDOCS_CREDS"]
    try:
        with open(path, "r") as _f:
            data.value = json.loads(_f.read())
    except ValueError as err:
        data.errors.append(gmsg(3171, err))
    except IOError as err:
        data.errors.append(gmsg(1021, err))
    return data


def load_to_db(data):
    """Rows are imported to SQLite DB one by one and skipped if very similar ones already exist."""
    count = skipped = failed = 0
    flashes = []
    for index, row in data:
        if len(row) < 8:
            flashes.append(fmsg(2152, row))
        elif index > 0:  # Skipping title row, so starting from 1 instead of 0
            row = [item.value if hasattr(item, "value") else item for item in row]
            msg, style, language = db_queries.create_language(row[0].lower())
            if style == "success":
                flashes.append((msg, style))
            values = [language.id, row[1], row[2], row[3]]
            msg, style, snippet = db_queries.create_snippet(values)
            values = {"created": row[4], "modified": row[5], "accessed": row[6], "visits": row[7]}
            db_queries.update_snippet_values(snippet.id, values)
            if style == "success":
                count += 1
            elif style == "warning":
                skipped += 1
            elif style == "danger":
                failed += 1
    if count > 0:
        style = 0 if (skipped + failed) == 0 else 3
        flashes.append(fmsg(2160 + style, count))
    if skipped > 0:
        flashes.append(fmsg(2172, skipped))
    if failed > 0:
        flashes.append(fmsg(2181, failed))
    return flashes


def get_download_folder_abs_path(app_conf):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), app_conf["DOWNLOAD_FOLDER"])


def get_files_list(app_conf):
    """Get list of backups *.xlsx available to download."""
    folder = get_download_folder_abs_path(app_conf)
    excels = [xls for xls in os.listdir(folder) \
              if xls.endswith(".xlsx") and os.path.isfile(os.path.join(folder, xls))]
    return excels


def delete_old_local_excels(app_conf):
    data = Data(None, [])
    excels = get_files_list(app_conf)
    folder = get_download_folder_abs_path(app_conf)
    for file_name in sorted(excels, reverse=True)[app_conf["MAX_BACKUPS"]:]:
        try:
            abs_path = os.path.join(folder, file_name)
            os.remove(abs_path)
            data.value = True  # since os.remove does not return any value, set it manually
        except OSError as err:
            msg = "%s due to OS error: %s" % (file_name, err)
            data.errors.append(gmsg(1031, msg))  # Could not delete file
    return data


def get_spreadsheet_url(app_conf):
    return "https://docs.google.com/spreadsheets/d/%s/edit" % app_conf["GDOCS_SPREADSHEET_ID"]


def update_settings_file(settings, conf_file_path, spreadsheet_id):
    """Settings are loaded from conf.py (which takes them from custom.json) at every launch.
    When settings are changed while app is running (through http://.../settings/update) -
    they are loaded into app.config dictionary.
    To "remember" them for next launches they are put into custom.json file.
    Hence, to avoid desynchronization, it is not recommended to edit custom.json manually.
    """
    settings.update({"GDOCS_SPREADSHEET_ID": spreadsheet_id})
    with open(conf_file_path, "w+") as _f:
        _f.write(json.dumps(settings))
    return True


def collect_settings(app_conf):
    data = check_gdocs_creds_file(app_conf)
    status = "OK"
    if not os.path.isfile(app_conf["GDOCS_CREDS"]):
        status = "MISSING"
    elif data.errors:
        status = "INVALID"
    settings = {
        "MAX_BACKUPS": {"value": app_conf["MAX_BACKUPS"], "comment": ""},
        "ITEMS_PER_PAGE": {"value": app_conf["ITEMS_PER_PAGE"], "comment": ""},
        "EMAIL": {"value": app_conf["EMAIL"] or "UNDEFINED",
                  "comment": "Optional, required only for Google Spreadsheets"},
        "GDOCS_SPREADSHEET_ID": {"value": app_conf["GDOCS_SPREADSHEET_ID"] or "UNDEFINED",
                                 "comment": "No manual edits allowed"},
        "GDOCS_CREDS_FILE": {"value": status,
                             "comment": "Optional, required only for Google Spreadsheets"}
    }
    return settings
