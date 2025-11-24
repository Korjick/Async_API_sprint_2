import uuid
from typing import Optional, TypeVar, Generic, List

from elasticsearch import AsyncElasticsearch, NotFoundError

from internal.pkg.errors import ObjectNotFoundError
from internal.pkg.pagination import Pagination

M = TypeVar('M')


class ElasticBaseRepository(Generic[M]):
    def __init__(self, elastic: AsyncElasticsearch, index_name: str,
                 model: type[M]):
        self.elastic = elastic
        self.index_name = index_name
        self.model = model

    async def get_by_id(self, item_id: uuid.UUID) -> M:
        try:
            doc = await self.elastic.get(index=self.index_name, id=str(item_id))
        except NotFoundError:
            raise ObjectNotFoundError(param_name="id", entity_id=item_id)
        return self._build_model(doc)

    async def get_list(self,
                       pagination: Optional[Pagination] = Pagination(page=1, per_page=50),
                       body: dict = None) -> List[M]:
        # Если тело запроса не передано, ищем всё
        if body is None:
            body = {"query": {"match_all": {}}}

        from_ = (pagination.page - 1) * pagination.per_page

        body['from'] = from_
        body['size'] = pagination.per_page

        try:
            response = await self.elastic.search(
                index=self.index_name,
                body=body
            )
        except NotFoundError:
            raise ObjectNotFoundError(param_name="index", entity_id=self.index_name)

        hits = response['hits']['hits']
        return [self._build_model(hit) for hit in hits]

    def _build_model(self, hit: dict) -> M:
        """
        Преобразование документа Elasticsearch в доменную модель.
        Ожидается, что доменная модель принимает параметр `oid` для идентификатора.
        """
        source = hit.get('_source', {}).copy()
        raw_id = source.pop('id', None)

        oid: Optional[uuid.UUID] = None
        if raw_id is not None:
            try:
                oid = uuid.UUID(str(raw_id))
            except (ValueError, TypeError):
                oid = None
        else:
            try:
                oid = uuid.UUID(str(hit.get('_id')))
            except (ValueError, TypeError):
                oid = None

        if oid is not None:
            return self.model(oid=oid, **source)
        return self.model(**source)
