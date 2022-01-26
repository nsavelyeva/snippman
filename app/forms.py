from wtforms import Form, validators, ValidationError, \
                    StringField, SelectField, TextAreaField, BooleanField, DecimalField, HiddenField
from flask_wtf.file import FileField
from sqlalchemy import exc
from app import app
from .models import Languages
from .messages import msg
from .helpers import check_gdocs_creds_file



SETTINGS_URL = "<a href=\"/settings\" target=\"_blank\">settings</a>"


def get_languages_choices():
    try:
        languages = [(lang.id, lang.name) for lang in Languages.query.order_by("name")]
    except exc.OperationalError as err:
        print(err)
        languages = []
    return languages


def validate_gdocs_file(form, field):
    data = check_gdocs_creds_file(app.config)
    if data.errors:
        error = "%s. %s." % (" ".join(data.errors), msg(3211, SETTINGS_URL))
        raise ValidationError(error)


def validate_gdocs_email(form, field):
    if not app.config["EMAIL"]:
        raise ValidationError(msg(4121, SETTINGS_URL))


def validate_gdocs_spreadsheet(form, field):
    if not app.config["GDOCS_SPREADSHEET_ID"]:
        raise ValidationError(msg(3181, SETTINGS_URL))


class SnippetsForm(Form):
    language = SelectField("Language", coerce=int)
    description = StringField("Description", [validators.Length(min=1, max=265)],
                              default="", render_kw={"size": 140})
    snippet = TextAreaField("Snippet", [validators.DataRequired()],
                            render_kw={"rows": 30, "cols": 100})
    comment = TextAreaField("Comment", [validators.DataRequired()],
                            render_kw={"rows": 5, "cols": 100})


class LanguagesForm(Form):
    name = StringField("Language", [validators.Length(min=1, max=30)],
                       default="", render_kw={"size": 140})





class ExportForm(Form):
    tick_gdocs = BooleanField("Export to Google SpreadSheet")
    tick_local = BooleanField("Export to Excel file (file download will be available)")


class ImportForm(Form):
    tick_gdocs = BooleanField("Import from a Google SpreadSheet")
    upload = FileField("Import from a local Excel file.")


class SettingsForm(Form):
    items_per_page = DecimalField("Items per page", [validators.NumberRange(1, 100)],
                         default=app.config["ITEMS_PER_PAGE"], places=0, render_kw={"size": 5})
    max_backups = DecimalField("Max Backups Count", [validators.NumberRange(1, 20)],
                         default=app.config["MAX_BACKUPS"], places=0, render_kw={"size": 5})
    email = StringField("E-mail", [validators.Email(msg(4121, SETTINGS_URL))],
                        default=app.config["EMAIL"], render_kw={"size": 100})
    upload = FileField("JSON file with a private key provided by Google")

