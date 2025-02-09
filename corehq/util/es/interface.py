from corehq.apps.es.client import manager
from corehq.apps.es.const import SCROLL_KEEPALIVE
from corehq.apps.es.transient_util import doc_adapter_from_alias


class ElasticsearchInterface:

    SCROLL_KEEPALIVE = SCROLL_KEEPALIVE

    def __init__(self, es):
        # TODO: verify that the `es` arg came from the client module and is not
        #       a real client (would indicate the caller is not compliant).
        self.es = es

    def get_aliases(self):
        return manager.get_aliases()

    def update_index_settings_reindex(self, index):
        manager.index_configure_for_reindex(index)

    def update_index_settings_standard(self, index):
        manager.index_configure_for_standard_ops(index)

    def doc_exists(self, index_alias, doc_id, doc_type):
        doc_adapter = self._get_doc_adapter(index_alias, doc_type)
        return doc_adapter.exists(doc_id)

    def get_doc(self, index_alias, doc_type, doc_id, source_includes=None):
        doc_adapter = self._get_doc_adapter(index_alias, doc_type)
        if source_includes is None:
            source_includes = []
        return doc_adapter.get(doc_id, source_includes=source_includes)

    def get_bulk_docs(self, index_alias, doc_type, doc_ids):
        doc_adapter = self._get_doc_adapter(index_alias, doc_type)
        return doc_adapter.get_docs(doc_ids)

    def index_doc(self, index_alias, doc_type, doc_id, doc):
        doc_adapter = self._get_doc_adapter(index_alias, doc_type)
        if doc.get("_id", object()) != doc_id:
            # TODO: raise an exception
            # This replicates previous functionality, but would be a worrying
            # scenario if it happens.  Raising an exception here could cause a
            # regression in production code so this is left "as built" for now.
            doc["_id"] = doc_id
        doc_adapter.index(doc)

    def update_doc_fields(self, index_alias, doc_type, doc_id, fields, params=None):
        doc_adapter = self._get_doc_adapter(index_alias, doc_type)
        kw = {} if params is None else params
        doc_adapter.update(doc_id, fields, **kw)

    def count(self, index_alias, doc_type, query):
        doc_adapter = self._get_doc_adapter(index_alias, doc_type)
        return doc_adapter.count(query)

    def delete_doc(self, index_alias, doc_type, doc_id):
        doc_adapter = self._get_doc_adapter(index_alias, doc_type)
        doc_adapter.delete(doc_id)

    def bulk_ops(self, index_alias, doc_type, actions, **kwargs):
        doc_adapter = self._get_doc_adapter(index_alias, doc_type)
        return doc_adapter.bulk(actions, **kwargs)

    def search(self, index_alias, doc_type, body=None, **kwargs):
        doc_adapter = self._get_doc_adapter(index_alias, doc_type)
        query = {} if body is None else body
        return doc_adapter.search(query, **kwargs)

    def iter_scroll(self, index_alias, doc_type, body=None,
                    scroll=SCROLL_KEEPALIVE, **kwargs):
        doc_adapter = self._get_doc_adapter(index_alias, doc_type)
        query = {} if body is None else body
        yield from doc_adapter.scroll(query, scroll=scroll, **kwargs)

    def _get_doc_adapter(self, index_alias, doc_type):
        doc_adapter = doc_adapter_from_alias(index_alias)
        if doc_adapter.type != doc_type:
            raise ValueError(f"wrong type ({doc_type}) for adapter: {doc_adapter}")
        return doc_adapter
