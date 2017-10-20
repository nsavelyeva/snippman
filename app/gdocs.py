import time
import json
import httplib2
import apiclient.discovery
from apiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from .messages import msg as gmsg
from . import helpers


def generate_sheet_title():
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))


class SpreadSheet(object):
    """A class to interact with Google SpreadSheets."""

    def __init__(self, app_conf):
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            app_conf["GDOCS_CREDS"],
            ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
        )
        self.auth = creds.authorize(httplib2.Http())
        self.service = apiclient.discovery.build("sheets", "v4", http=self.auth)
        self.email = app_conf["EMAIL"]
        self.spreadsheet_id = app_conf["GDOCS_SPREADSHEET_ID"]
        self.max_backups = app_conf["MAX_BACKUPS"]
        self.items_per_page = app_conf["ITEMS_PER_PAGE"]
        self.conf_file = app_conf["SETTINGS_FILE"]

    def add_sheet(self, sheet_title=None):
        """Add a sheet to the front of a given SpreadSheet (i.e. sheet index = 0)."""
        sheet_title = sheet_title or generate_sheet_title()
        request = {"addSheet": {"properties": {"index": 0, "title": sheet_title}}}
        try:
            result = self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                                             body={"requests": [request]}
                                                            ).execute()
        except HttpError as err:
            err = json.loads(err.content)["error"]
            msg = "%s into %s - returned %s %s" % (sheet_title, self.spreadsheet_id,
                                                   err["code"], err["message"])
            return helpers.Data(None, [gmsg(3061, msg)])
        return helpers.Data(result, [])

    def read_all_rows(self):
        """Read data from the latest sheet of a given SpreadSheet."""
        data = self.get_latest_sheet()
        if data.errors:
            return data
        range_name = "%s!A1:H" % data.value
        try:
            result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id,
                                                              range=range_name
                                                             ).execute().get("values", [])
        except HttpError as err:
            err = json.loads(err.content)["error"]
            msg = "range %s in %s - returned %s %s" % (range_name, self.spreadsheet_id,
                                                       err["code"], err["message"])
            return helpers.Data(None, [gmsg(3071, msg)])
        return helpers.Data(result, [])

    def write_all_rows(self, rows=None):
        """Write data to a new sheet, if a SpreadSheet does not exist - it will be created."""
        data = helpers.Data(self.spreadsheet_id, [])
        rows = rows or []
        sheet_title = generate_sheet_title()
        if self.spreadsheet_id:
            data.errors.extend(self.add_sheet(sheet_title).errors)  # add new sheet to SpreadSheet
            data.errors.extend(self.delete_old_sheets().errors)     # if needed remove oldest sheet
        else:
            data = self.create_spreadsheet(sheet_title)
            if data.errors:
                return data
            settings = {"ITEMS_PER_PAGE": self.items_per_page, "MAX_BACKUPS": self.max_backups,
                        "EMAIL": self.email}
            helpers.update_settings_file(settings, self.conf_file, self.spreadsheet_id)
        header = ["", "Language", "Description", "Snippet", "Comment",
                  "Created", "Modified", "Accessed", "Visits"]
        line_num = 0  # now we are ready to write data
        for row in [header] + rows:
            line_num += 1
            items = [str(item) for item in row[1:]]
            try:
                result = self.service.spreadsheets().values().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={"valueInputOption": "USER_ENTERED",
                          "data": {"range": "%s!A%s:H%s" % (sheet_title, line_num, line_num),
                                   "majorDimension": "ROWS", "values": [items]}
                    }
                ).execute()
                if result["responses"][0]["updatedCells"] != len(row[1:]):
                    msg = "values %s, row #%s" % (row[line_num], line_num)
                    data.errors.append(gmsg(3081, msg))  # Failed writing row N line_num
            except TypeError as err:
                data.errors.append(gmsg(3091, err))  # Failed writing data
            except HttpError as err:
                err = json.loads(err.content)["error"]
                msg = "returned %s %s" % (err["code"], err["message"])
                data.errors.append(gmsg(3101, msg))  # Google API has not accepted the data
        return data

    def get_all_sheets(self):
        """Get all sheets data of the given SpreadSheet."""
        try:
            response = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            result = response.get("sheets", "")
        except HttpError as err:
            err = json.loads(err.content)["error"]
            msg = "%s - returned %s %s" % (self.spreadsheet_id, err["code"], err["message"])
            return helpers.Data(None, [gmsg(3111, msg)])
        return helpers.Data(result, [])

    def get_latest_sheet(self):
        """Obtain a title of the latest sheet."""
        data = self.get_all_sheets()
        if data.errors:
            return data
        sheets = data.value
        props = [(sheet["properties"]["title"], sheet["properties"]["index"]) for sheet in sheets]
        result = sorted(props, key=lambda item: item[1])[0][0]
        return helpers.Data(result, [])

    def delete_old_sheets(self):  # by sheet index
        """Oldest sheets will be removed if the number of sheets exceeds MAX_BACKUPS value."""
        data = self.get_all_sheets()
        if data.errors:
            return data
        sheets = data.value
        if len(sheets) <= self.max_backups:  # no redundant backups
            return helpers.Data(None, [])
        props = [(sheet["properties"]["sheetId"], sheet["properties"]["index"]) for sheet in sheets]
        requests = []
        # Iterate through tuples sorted by sheet index ascending, only old sheets (greater indices):
        for item in sorted(props, key=lambda x: x[1])[self.max_backups:]:
            requests.append({"deleteSheet": {"sheetId": item[0]}})
        try:
            result = self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                                             body={"requests": requests}
                                                            ).execute()
        except HttpError as err:
            err = json.loads(err.content)["error"]
            msg = "%s %s" % (err["code"], err["message"])
            return helpers.Data(None, [msg])
        return helpers.Data(result, [])

    def create_spreadsheet(self, sheet_title):
        """A SpreadSheet will be created and shared using e-mail."""
        body = {"properties": {"title": "Snippets", "locale": "en_US"},
                "sheets": [{"properties": {"sheetType": "GRID", "title": sheet_title}}]}
        try:
            spreadsheet = self.service.spreadsheets().create(body=body).execute()  # create
        except HttpError as err:
            err = json.loads(err.content)["error"]
            msg = "returned %s %s" % (err["code"], err["message"])
            return helpers.Data(None, [gmsg(3121, msg)])
        drive_service = apiclient.discovery.build("drive", "v3", http=self.auth)   # share
        try:
            body = {"type": "user", "role": "writer", "emailAddress": self.email}
            drive_service.permissions().create(fileId=spreadsheet["spreadsheetId"],
                                               body=body, fields="id"
                                              ).execute()
            self.spreadsheet_id = spreadsheet["spreadsheetId"]
        except HttpError as err:
            err = json.loads(err.content)["error"]
            msg = "%s to %s - returned %s %s" % (self.spreadsheet_id, self.email,
                                                 err["code"], err["message"])
            return helpers.Data(None, [gmsg(3131, msg)])
        return helpers.Data(self.spreadsheet_id, [])

    def get_all_spreadsheets(self, prefix="Snippets", do_delete=False):
        """List all SpreadSheets created by SnippMan and remove them if needed (on-demand)."""
        drive_service = apiclient.discovery.build("drive", "v3", http=self.auth)  # get list
        try:
            response = drive_service.files().list(pageSize=10,
                                                  fields="nextPageToken, files(id, name)"
                                                 ).execute()
        except (ValueError, IOError) as err:              # Failed to communicate
            return helpers.Data(None, [gmsg(3141, err)])  # with Google SpreadSheets
        except HttpError as err:
            err = json.loads(err.content)["error"]
            msg = "returned %s %s" % (err["code"], err["message"])
            return helpers.Data(None, [gmsg(3151, msg)])  # Could not collect SpreadSheets names
        result = [resp["id"] for resp in response["files"] if resp["name"].startswith(prefix)]
        if do_delete:
            for res in result:
                try:
                    drive_service.files().delete(fileId=res).execute()          # delete all
                except HttpError as err:
                    err = json.loads(err.content)["error"]
                    msg = "%s - returned %s %s" % (res, err["code"], err["message"])
                    return helpers.Data(None, [gmsg(3161, msg)])  # Could not delete SpreadSheet
            return helpers.Data(True, [])
        return helpers.Data(result, [])

    def remove_spreadsheets(self):
        """An alias to call get_all_spreadsheets() method with do_delete=True."""
        return self.get_all_spreadsheets("Snippets", True)
