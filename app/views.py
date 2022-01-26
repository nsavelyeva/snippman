from flask import render_template, redirect, url_for, request, jsonify, flash, send_from_directory
from app import app
from .forms import SnippetsForm, LanguagesForm, ExportForm, ImportForm, SettingsForm, \
    validators, validate_gdocs_file, validate_gdocs_email, validate_gdocs_spreadsheet, \
    get_languages_choices
from .models import Snippets, Languages, db
from .gdocs import SpreadSheet
from .messages import fmsg
from . import db_queries
from . import excel
from . import helpers


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/downloads")
def backups():
    files = sorted(helpers.get_files_list(app.config), reverse=True)
    url = helpers.get_spreadsheet_url(app.config) if app.config["GDOCS_SPREADSHEET_ID"] else ""
    return render_template("download.html", files=files, url=url)


@app.route("/_statistics")
def get_statistics():
    data = db_queries.get_statistics()
    return jsonify(result=data)


@app.route("/_snippet_body")
def get_snippet_body():
    snippet_id = request.args.get("snippet_id", 0, type=int)
    data = db_queries.get_snippet(snippet_id)
    result = {"id": data.id, "snippet": data.snippet}
    return jsonify(result)


@app.route("/_pop1_max_visits")
def get_max_visits_count():
    try:
        data = db_queries.get_top_snippets([Snippets.visits], "pop", 1).all()[0][0]
        result = {"id": data.id, "description": data.description, "visits": data.visits}
    except IndexError:
        result = {"id": "", "description": "", "visits": ""}
    return jsonify(result)


@app.route("/_new1_last_created")
def get_last_created_date():
    try:
        data = db_queries.get_top_snippets([Snippets.created], "new", 1).all()[0][0]
        result = {"id": data.id, "description": data.description, "created": data.created}
    except IndexError:
        result = {"id": "", "description": "", "created": ""}
    return jsonify(result)


@app.route("/_fresh1_last_modified")
def get_last_modified_date():
    try:
        data = db_queries.get_top_snippets([Snippets.modified], "fresh", 1).all()[0][0]
        result = {"id": data.id, "description": data.description, "modified": data.modified}
    except IndexError:
        result = {"id": "", "description": "", "modified": ""}
    return jsonify(result)


@app.route("/downloads/<path:filename>", methods=["GET"])
def download(filename):
    return send_from_directory(directory=app.config["DOWNLOAD_FOLDER"],
                               filename=filename, as_attachment=True)


@app.route("/snippets/list", defaults={"page": 1}, methods=["GET"])
@app.route("/snippets/list/<int:page>", methods=["GET"])
def list_snippets(page):
    fields = [Snippets.id, Languages.name, Snippets.description]
    if request.args and "entry" in request.args.to_dict():
        entry = str(request.args.to_dict()["entry"])
        data = db_queries.find_snippets(fields, entry)
    else:
        data = db_queries.get_all_snippets(fields)
    pagination = data.paginate(page, app.config["ITEMS_PER_PAGE"], True)
    rows = pagination.items
    style = 3 if pagination.total > 0 else 2
    flash(*fmsg(2010 + style, pagination.total))  # Found snippets
    return render_template("list.html", rows=rows, pagination=pagination, table="snippets",
                           fields=[field.__dict__["key"] for field in fields])


@app.route("/snippets/pop", defaults={"count": 10}, methods=["GET"])
@app.route("/snippets/pop/<int:count>", methods=["GET"])
@app.route("/snippets/new", defaults={"count": 10}, methods=["GET"])
@app.route("/snippets/new/<int:count>", methods=["GET"])
@app.route("/snippets/fresh", defaults={"count": 10}, methods=["GET"])
@app.route("/snippets/fresh/<int:count>", methods=["GET"])
def top_snippets(count):
    fields = [Snippets.id, Languages.name, Snippets.description]
    rows = db_queries.get_top_snippets(fields, request.url, count)
    pagination = rows.paginate(1, count, True)
    return render_template("list.html", rows=rows, pagination=pagination, table="snippets",
                           fields=[field.__dict__["key"] for field in fields])


@app.route("/snippets/<language>", defaults={"page": 1}, methods=["GET"])
@app.route("/snippets/<language>/<int:page>", methods=["GET"])
def list_snippets_for_language(language, page):
    fields = [Snippets.id, Languages.name, Snippets.description]
    data = db_queries.get_snippets_per_language(fields, language)
    pagination = data.paginate(page, app.config["ITEMS_PER_PAGE"], True)
    rows = pagination.items
    flash(*fmsg(2023, "%s - %s item(s)" % (language, pagination.total)))  # Snippets for language
    return render_template("list.html", rows=rows, pagination=pagination, table="snippets",
                           fields=[field.__dict__["key"] for field in fields])


@app.route("/languages/list", defaults={"page": 1}, methods=["GET"])
@app.route("/languages/list/<int:page>", methods=["GET"])
def list_languages(page):
    fields = [Languages.id, Languages.name]
    data = db_queries.get_all_languages(fields)
    pagination = data.paginate(page, app.config["ITEMS_PER_PAGE"], True)
    rows = pagination.items
    style = 3 if pagination.total > 0 else 2
    flash(*fmsg(2030 + style, pagination.total))  # Found languages
    return render_template("list.html", rows=rows, pagination=pagination, table="languages",
                           fields=[field.__dict__["key"] for field in fields])


@app.route("/snippets/view/<int:snippet_id>", methods=["GET"])
def view_snippet(snippet_id):
    fields = [Snippets.id, Languages.name, Snippets.description,
              Snippets.snippet, Snippets.comment, Snippets.created,
              Snippets.modified, Snippets.accessed, Snippets.visits]
    snippet = db_queries.get_snippet_details(fields, snippet_id)
    return render_template("snippet.html", snippet=snippet)


@app.route("/languages/view/<int:language_id>", methods=["GET"])
def view_language(language_id):
    language = db_queries.get_language(language_id)
    return render_template("language.html", language=language)


@app.route("/snippets/delete/", methods=["POST"])
def delete_snippet():
    if request.form and "item" in request.form:
        snippet_id = int(request.form.get("item", type=int))
        msg, style = db_queries.remove_snippet(snippet_id)
        flash(msg, style)
    return redirect(url_for("list_snippets"))


@app.route("/languages/delete/", methods=["POST"])
def delete_language():
    if request.form and "item" in request.form:
        language_id = int(request.form.get("item", type=int))
        msg, style = db_queries.remove_language(language_id)
        flash(msg, style)
    return redirect(url_for("list_languages"))


@app.route("/snippets/add", methods=["GET", "POST"])
def add_snippet():
    form = SnippetsForm(request.form)
    form.language.choices = get_languages_choices()
    if request.method == "POST" and form.validate():
        values = [form.language.data, form.description.data,
                  form.snippet.data, form.comment.data]
        msg, style, snippet = db_queries.create_snippet(values)
        flash(msg, style)
        if style == "success":
            return redirect(url_for("list_snippets"))
    return render_template("anyform.html", form=form, submit_name="Save")


@app.route("/languages/add", methods=["GET", "POST"])
def add_language():
    form = LanguagesForm(request.form)
    if request.method == "POST" and form.validate():
        msg, style, language = db_queries.create_language(form.name.data)
        flash(msg, style)
        if style == "success":
            return redirect(url_for("list_languages"))
    return render_template("anyform.html", form=form, submit_name="Save")


@app.route("/snippets/edit/<int:snippet_id>", methods=["GET", "POST"])
def edit_snippet(snippet_id):
    snippet = db_queries.get_snippet(snippet_id)
    form = SnippetsForm(obj=snippet)
    form.language.choices = get_languages_choices()
    if request.method == "POST" and form.validate():
        msg, style = db_queries.update_snippet(request.form, snippet_id)
        flash(msg, style)
        if style == "success":
            return redirect(url_for("list_snippets"))
    return render_template("anyform.html", form=form, submit_name="Save")


@app.route("/languages/edit/<int:language_id>", methods=["GET", "POST"])
def edit_language(language_id):
    language = db_queries.get_language(language_id)
    form = LanguagesForm(obj=language)
    if request.method == "POST" and form.validate():
        msg, style = db_queries.update_language(request.form, language_id)
        flash(msg, style)
        if style == "success":
            return redirect(url_for("list_languages"))
    return render_template("anyform.html", form=form, submit_name="Save")


@app.route("/export", methods=["GET", "POST"])
def export_db():
    print(app.config["GDOCS_SPREADSHEET_ID"])
    form = ExportForm(request.form)
    if request.method == "POST" and form.validate():
        flashes = []
        rows = db_queries.get_all_snippets().all()
        if request.form.get("tick_gdocs") == "y":
            form.tick_gdocs.validators.append(validate_gdocs_file)  # validate only if selected
            if not app.config["GDOCS_SPREADSHEET_ID"]:
                form.tick_gdocs.validators.append(validate_gdocs_email)
            if form.validate():
                data = SpreadSheet(app.config).write_all_rows(rows)
                if not data.errors:
                    app.config["GDOCS_SPREADSHEET_ID"] = data.value
                    url = helpers.get_spreadsheet_url(app.config)
                    href = "<a href=\"%s\" class=\"alert-link\" target=\"_blank\">%s</a>"
                    flashes.append(fmsg(3010, href % (url, url)))  # Exported to Google SpreadSheet
                else:
                    msg = "<br>%s" % "<br>".join(list(set(data.errors)))
                    flashes.append(fmsg(3021, msg))  # Failed export data to Google SpreadSheet
            else:
                href = "<a href=\"/settings\" target=\"_blank\">settings</a>"
                flashes.append(fmsg(3201, href))  # Could not export data to Google SpreadSheet
        else:
            form.tick_gdocs.validators = []  # don't validate the form if GDocs is not selected
        if request.form.get("tick_local") == "y":
            data = excel.save_to_local_file(rows, app.config)
            if not data.errors:
                f_name = data.value  # local file name
                href = "<a href=\"/downloads/%s\" class=\"alert-link\">%s</a>" % (f_name, f_name)
                flashes.append(fmsg(2040, href))  # Data have been exported to a local file
                for item in list(set(flashes)):
                    flash(item[0], item[1])
                return render_template("download.html", file_name=data.value,
                                       files=sorted(helpers.get_files_list(app.config), reverse=True))
            for error in data.errors:
                flashes.append((error, "danger"))
        for item in list(set(flashes)):
            flash(item[0], item[1])
    return render_template("anyform.html", form=form, submit_name="Export")


@app.route("/import", methods=["GET", "POST"])
def import_db():
    form = ImportForm(request.form)
    form.tick_gdocs.validators = []
    if request.method == "POST" and form.validate():
        flashes = []
        data = helpers.upload_file(request, app.config)
        local_path = data.value
        if local_path:
            data = excel.read_from_local_file(data.value)
            if data.errors:
                flashes.append((" ".join(data.errors), "danger"))
            else:
                flashes.append(fmsg(4080))  # Read data from a local [uploaded] file successfully
                flashes.extend(helpers.load_to_db(data.value))  # Collect import-messages to flash
        if request.form.get("tick_gdocs") == "y":
            form.tick_gdocs.validators.append(validate_gdocs_file)  # validate only if selected
            if not app.config["GDOCS_SPREADSHEET_ID"]:
                form.tick_gdocs.validators.append(validate_gdocs_spreadsheet)
            if form.validate():
                url = helpers.get_spreadsheet_url(app.config)
                href = "<a href=\"%s\" class=\"alert-link\">%s</a>" % (url, url)
                rows = SpreadSheet(app.config).read_all_rows().value
                flashes.append(fmsg(3030, href))  # Read data from Google SpreadSheet successfully
                flashes.extend(helpers.load_to_db([(1, row) for row in rows[1:]]))
            else:
                href = "<a href=\"/settings\" target=\"_blank\">settings</a>"
                flashes.append(fmsg(3191, href))  # Could not import data from Google SpreadSheet
                for item in list(set(flashes)):
                    flash(item[0], item[1])
                return render_template("uploadform.html", form=form, submit_name="Import")
        for item in list(set(flashes)):
            flash(item[0], item[1])
    return render_template("uploadform.html", form=form, submit_name="Import")


@app.route("/settings/update", methods=["GET", "POST"])
def settings_update():
    form = SettingsForm(request.form)
    form.email.data = app.config["EMAIL"]
    form.email.validators = []  # E-mail and its validation is not needed if GDocs is not used
    if request.method == "POST" and form.validate():
        data = helpers.upload_gdocs_creds_file(request, app.config)
        if not helpers.check_gdocs_creds_file(app.config).errors:
            form.email.validators.append(validators.DataRequired())  # if creds uploaded check email
        if form.validate():  # need re-validate the form, maybe email validation has been enabled
            settings = {"ITEMS_PER_PAGE": int(request.form.get("items_per_page")),
                        "MAX_BACKUPS": int(request.form.get("max_backups")),
                        "EMAIL": request.form.get("email")}
            if helpers.update_settings_file(settings, app.config["SETTINGS_FILE"],
                                            app.config["GDOCS_SPREADSHEET_ID"]):
                app.config.update(settings)  # reload config only after successful file update
                form.email.data = settings["EMAIL"] # update field for form validation
                if data.errors:
                    flash(*fmsg(4023, " ".join(data.errors)))  # Info: No Google creds file uploaded
                else:
                    flash(*fmsg(4030))  # Updated settings
            else:
                flash(*fmsg(4041))  # Could not save settings
            return render_template("settings.html", settings=helpers.collect_settings(app.config))
    return render_template("uploadform.html", form=form, submit_name="Apply")


@app.route("/settings/restore", methods=["GET", "POST"])
def settings_restore():
    settings = {"ITEMS_PER_PAGE": 10, "MAX_BACKUPS": 10, "EMAIL": ""}
    if helpers.update_settings_file(settings, app.config["SETTINGS_FILE"], ""):
        app.config.update(settings)
        app.config["GDOCS_SPREADSHEET_ID"] = ""
        flash(*fmsg(4050))  # Loaded default settings
    else:
        flash(*fmsg(4061))  # Could not restore settings
    return render_template("settings.html", settings=helpers.collect_settings(app.config))


@app.route("/settings", methods=["GET"])
@app.route("/settings/view", methods=["GET"])
def settings_view():
    return render_template("settings.html", settings=helpers.collect_settings(app.config))


@app.route("/gspreadsheets/cleanup", methods=["GET"])
def cleanup():
    errors = SpreadSheet(app.config).remove_spreadsheets().errors
    if errors:
        flash(*fmsg(3041, " ".join(errors)))  # Could not remove SpreadSheets prefixed by 'Snippets'
    else:
        flash(*fmsg(3050))  # Removed all Google SpreadSheets prefixed by 'Snippets'
    app.config["GDOCS_SPREADSHEET_ID"] = ""
    settings = {"MAX_BACKUPS": app.config["MAX_BACKUPS"], "EMAIL": app.config["EMAIL"],
                "ITEMS_PER_PAGE": app.config["ITEMS_PER_PAGE"]}
    updated_ok = helpers.update_settings_file(settings, app.config["SETTINGS_FILE"],
                                              app.config["GDOCS_SPREADSHEET_ID"])
    if not updated_ok:
        flash(*fmsg(4071))  # Could not update settings after cleanup
    return render_template("settings.html", settings=helpers.collect_settings(app.config))


@app.errorhandler(404)
def page_not_found(e):
    error = "Page Not Found"
    return render_template("error.html", code=404, error=error), 404


@app.errorhandler(500)
def internal_server_error(e):
    error = "Internal Server Error"
    return render_template("error.html", code=500, error=error), 500


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()




