This `Flask` application is a simple **Snippets Manager**
with Web-interface for CRUD-operations, `highlight.js` as code highlighter,
and `SQL` as a search engine.

`SnippMan` is simple, hardly tested,
but it is useful enough to deliver its main task - manage snippets.

Moreover, SnippMan's import/export-features support backups
in the form of local `Excel` files and `Google SpreadSheets`.

Reason:
 * I had the aim of deepening my knowledge and freshening my practical skills.
 * I wanted to keep my snippets & other notes locally and search through them from a browser.
 * I got inspired by Flask tutorials and StackOverflow.

Tools:
 * Back-end: `Flask` microframework on the top of `Python` + `argparse`
 * Database: `SQLite` (which is inbuilt in Python) + `SQLAlchemy`
 * Frontend: `Bootstrap` + `jQuery` + `highlight.js` and `Jinja`-templates

Attention:
 * I almost did not test my little buggy app, so:
    - do not get surprised when you see it crashed with a scary `Traceback`;
    - I take no responsibility if your snippets leave to the valley of death.
 * In the case of Emergency, please stay calm, go to github and open an issue, or contact me at LinkedIn:
 https://www.linkedin.com/in/natallia-savelyeva/.

Usage:
 * Just launch run.py and open http://127.0.0.1 in your browser. Try `run.py -h` to see options.
 * Note: settings are loaded from `config.py` - feel free to customize them at http://../settings/update.
 * Start your work - add language first, and then you can add snippets.

Features:
 * Search for snippets through `SQLite` database by a string entry.
 * CRUD operations for snippets and programming languages through web-interface.
 * Code highlighting.
 * Listing snippets:
    - pagination;
    - pop-10: popular(=most visited) snippets;
    - new-10: last created snippets;
    - fresh-10: last updated snippets.
 * Statistics:
    - snippets count per programming language;
    - total snippets count;
    - total programming languages count;
    - last updated/created snippet, most popular snippet.
 * Import snippets from a local Excel file to a local sqlite database.
 * Export snippets from a local SQLite database to a local Excel file.
 * Import snippets from Google SpreadSheets to a local sqlite database.
 * Export snippets from a local SQLite database to Google SpreadSheets.
 * Web interface to manage application settings.
 * Support options to launch SnippMan from command line.
