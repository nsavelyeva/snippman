from sqlalchemy import func, or_, exc, desc
from .models import Snippets, Languages, db, get_time_str
from .messages import fmsg


def get_statistics():
    query = db.session.query(Languages.name, func.count(Languages.name).label("total"))
    data = query.join(Snippets, Snippets.language == Languages.id)
    stats = data.group_by(Languages.name).order_by(desc("total")).all()  # ("total DESC").all()
    return stats


def find_snippets(fields, entry):
    query = Snippets.query.join(Languages, Snippets.language == Languages.id)
    data = query.filter(or_(Snippets.description.contains(entry),
                            Snippets.snippet.contains(entry))
                        ).add_columns(*fields)
    return data


def get_top_snippets(fields, url, count):
    query = Snippets.query.join(Languages, Snippets.language == Languages.id)
    if "pop" in url:
        query = query.order_by(Snippets.visits.desc())
    elif "new" in url:
        query = query.order_by(Snippets.created.desc())
    elif "fresh" in url:
        query = query.order_by(Snippets.modified.desc())
    data = query.limit(count).add_columns(*fields)
    return data


def get_all_snippets(fields=None):
    fields = fields or [Languages.name, Snippets.description, Snippets.snippet,
                        Snippets.comment, Snippets.created, Snippets.modified,
                        Snippets.accessed, Snippets.visits]
    query = Snippets.query.join(Languages, Snippets.language == Languages.id)
    data = query.add_columns(*fields)
    return data


def get_snippets_per_language(fields, language):
    query = Snippets.query.join(Languages, Snippets.language == Languages.id)
    data = query.filter(Languages.name == language).add_columns(*fields)
    return data


def get_all_languages(fields):
    data = Languages.query.add_columns(*fields)
    return data


def get_snippet_details(fields, snippet_id):
    query = Snippets.query.join(Languages, Snippets.language == Languages.id)
    snippet = query.filter(Snippets.id==snippet_id).add_columns(*fields).first()
    #  Update last accessed date and visits count:
    values = {"accessed": get_time_str(), "visits": snippet.visits + 1}
    update_snippet_values(snippet.id, values)
    return snippet


def get_snippet(snippet_id):
    data = db.session.query(Snippets).filter_by(id=snippet_id).first()
    return data


def get_language(language_id):
    data = db.session.query(Languages).filter_by(id=language_id).first()
    return data


def find_language_by_name(name):
    language = db.session.query(Languages).filter_by(name=name).first()
    return language


def find_snippet_by_attributes(description, body):
    query = Snippets.query.join(Languages, Snippets.language == Languages.id)
    snippet = query.filter(or_(Snippets.description == description,
                               Snippets.snippet == body)
                          ).first()
    return snippet


def update_snippet_values(snippet_id, values):
    db.session.query(Snippets).filter_by(id=snippet_id).update(values)
    db.session.commit()
    return fmsg(2050)  # tuple of success message and style


def update_snippet(request_form, snippet_id):
    values = {
        "language": request_form.get("language"),
        "description": request_form.get("description"),
        "snippet": request_form.get("snippet"),
        "comment": request_form.get("comment"),
        "modified": get_time_str(),
    }
    return update_snippet_values(snippet_id, values)   # tuple of success message and style


def update_language(request_form, language_id):
    values = {"name": request_form.get("name")}
    db.session.query(Languages).filter_by(id=language_id).update(values)
    db.session.commit()
    return fmsg(2060, language_id)   # tuple of success message and style


def remove_snippet(snippet_id):
    snippet = Snippets.query.get(snippet_id)
    db.session.delete(snippet)
    db.session.commit()
    return fmsg(2070, snippet_id)   # tuple of success message and style


def remove_language(language_id):
    language = Languages.query.get(language_id)
    snippets_attached = get_snippets_per_language([Snippets.id], language.name).all()
    if snippets_attached:
        msg = "%s - it has %s snippet(s) attached" % (language_id, len(snippets_attached))
        return fmsg(2081, msg)  # Cannot remove language because it has snippets attached
    db.session.delete(language)
    db.session.commit()
    return fmsg(2090, "'%s'" % language.name)  # tuple of success message and style
    

def create_snippet(values):
    description = values[1].strip().lower()
    body = values[2].strip().lower()
    snippet = Snippets.query.filter(or_(Snippets.description == description,
                                        Snippets.snippet == body)).first()
    if snippet:
        return fmsg(2102) + (snippet,)  # Snippet was not added - already exists, return 3-tuple
    try:
        snippet = Snippets(*values)  # values: language_relation, description, snippet, comment
        db.session.add(snippet)
        db.session.commit()
    except exc.IntegrityError as err:
        msg = "'%s' due to Integrity error: %s" % (description, err)
        return fmsg(2111, msg) + (None,)  # bad data, return 3-tuple
    return fmsg(2120) + (snippet, )  # 3-tuple of success message, style, and snippet instance


def create_language(name):
    name = name.strip().lower()
    language = Languages.query.filter(Languages.name == name).first()
    if language:
        return fmsg(2131, "'%s' - already exists" % name) + (language, )
    language = Languages(name)
    db.session.add(language)
    db.session.commit()
    return fmsg(2140, name) + (language, )  # 3-tuple of success message, style, language instance
