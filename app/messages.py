def msg(code, details="", flash=False):
    """Get message and messaging style by the given code.
    Message will be concatenated with details and single string will be returned if flash is False.
    If flash=True, a tuple of a message and its style is returned.
    """
    code = str(code)
    details = str(details)
    separator = " " if MESSAGES[code[:-1]][-1] in [" ", "#"] else ": "
    statement = MESSAGES[code[:-1]] + separator + details if details else MESSAGES[code[:-1]]
    if flash:
        style = STYLES[code[-1]]
        return statement, style
    return statement


def fmsg(code, details=""):
    """An alias to call msg() function with flash=True."""
    return msg(code, details, True)


STYLES = {"0": "success", "1": "danger", "2": "warning", "3": "info"}  # styles used for flashing

MESSAGES = {
    # OS- and IO-related messages
    "101": "Could not complete upload due to OS error",
    "102": "Could not read Google credentials JSON file due to IO error",
    "103": "Could not delete file",
    "104": "Failed to save a workbook file ",
    "105": "Error while importing data from a local Excel file",
    # DB-related messages
    "201": "Snippets found",
    "202": "Snippets for language",
    "203": "Languages found",
    "204": "Data have been exported to a local file",
    "205": "Snippet has been successfully updated",
    "206": "Language has been successfully updated",
    "207": "Deleted Snippet #",
    "208": "Cannot remove language #",
    "209": "Deleted language ",
    "210": "Snippet has not been added - already exists",
    "211": "Cannot add Snippet ",
    "212": "Snippet has been added",
    "213": "Cannot add language ",
    "214": "Language has been added",
    "215": "Skipped row due to data inconsistency",
    "216": "Imported snippets",
    "217": "Skipped snippets (very similar ones already exist)",
    "218": "Snippets failed due to integrity issues",
    # GDocs-related messages
    "301": "Exported data to Google SpreadSheet",
    "302": "Failed export data to Google SpreadSheet",
    "303": "Data have been read from Google SpreadSheet",
    "304": "Could not delete Google SpreadSheets prefixed by 'Snippets'",
    "305": "Removed all Google SpreadSheets prefixed by 'Snippets'",
    "306": "Error adding sheet",
    "307": "Error reading data",
    "308": "Failed writing row",
    "309": "Failed writing data due to",
    "310": "Google API has not accepted the data",
    "311": "Error getting all sheets",
    "312": "Could not create a SpreadSheet",
    "313": "Could not share a SpreadSheet",
    "314": "Failed to communicate with Google SpreadSheets",
    "315": "Could not collect SpreadSheets names",
    "316": "Could not delete SpreadSheet",
    "317": "Google credentials JSON file seems to be invalid",
    "318": "No SpreadSheet ID found, please check ",
    "319": "Import data from Google SpreadSheet failed, please check ",
    "320": "Export data to Google SpreadSheet failed, please check ",
    "321": "Please upload valid credentials file provided by Google. Use ",
    # App-related common messages
    "401": "Please tick at least one export type",
    "402": "Settings updated, but no Google creds uploaded",
    "403": "Settings have been updated successfully",
    "404": "Error saving settings. Sorry...",
    "405": "Default settings have been loaded",
    "406": "Error restoring settings. Sorry...",
    "407": "Error updating settings after cleanup. Please try again",
    "408": "Data have been read from the local file",
    "409": "Cannot upload file: file is not accepted",
    "410": "Cannot upload file: no file part",
    "411": "Cannot upload file: no file selected",
    "412": "E-mail is required for GDocs SpreadSheets. Please check "
}
