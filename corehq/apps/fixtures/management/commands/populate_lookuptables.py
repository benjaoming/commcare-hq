from corehq.apps.cleanup.management.commands.populate_sql_model_from_couch_model import PopulateSQLCommand

from ...models import TypeField


class Command(PopulateSQLCommand):

    @classmethod
    def couch_db_slug(cls):
        return "fixtures"

    @classmethod
    def couch_doc_type(cls):
        return 'FixtureDataType'

    @classmethod
    def sql_class(cls):
        from ...models import LookupTable
        return LookupTable

    @classmethod
    def commit_adding_migration(cls):
        return "TODO: add once the PR adding this file is merged"

    @classmethod
    def diff_couch_and_sql(cls, couch, sql):
        """
        Compare each attribute of the given couch document and sql
        object. Return a list of human-readable strings describing their
        differences, or None if the two are equivalent. The list may
        contain `None` or empty strings.
        """
        diffs = [cls.diff_attr(name, couch, sql) for name in ["domain", "tag"]]
        diffs.append(cls.diff_value(
            "is_global",
            couch.get("is_global") or False,
            sql.is_global,
        ))
        for field in ["item_attributes", "description"]:
            diffs.append(cls.diff_maybe_empty_field(field, couch, sql))
        diffs.append(cls.diff_value(
            "fields",
            [transform_field(f) for f in couch["fields"]],
            sql.fields,
        ))
        return diffs

    @classmethod
    def diff_maybe_empty_field(cls, field, couch, sql):
        if couch.get(field) or getattr(sql, field):
            return cls.diff_value(field, couch.get(field), getattr(sql, field))


def transform_field(data):
    if isinstance(data, str):
        return TypeField(name=data)
    copy = data.copy()
    copy.pop("doc_type")
    return TypeField(name=copy.pop("field_name"), **copy)
