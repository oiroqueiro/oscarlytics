from portfolio import portfolio

import datetime

def add_to_index(index, model):
    if not portfolio.meilisearch:
        return
    
    data = {}
    data['id'] = model.id
    data['languageid'] = model.languageid
    for field in model.__searchable__:
        val = getattr(model, field)
        if isinstance(val, (datetime.date, datetime.datetime)):
            val = val.isoformat()
        data[field] = val

    portfolio.meilisearch.index(index).add_documents([data])
    
def remove_from_index(index, model):
    if not portfolio.meilisearch:
        return

    portfolio.meilisearch.index(index).delete_document(str(model.id))
    
def query_index(index, query, page, per_page, filter=None):
    if not portfolio.meilisearch:
        return
    
    search_params = {
        'offset': (page - 1) * per_page,
        'limit': per_page
    }
    if filter:
        search_params['filter'] = filter

    search = portfolio.meilisearch.index(index).search(query, search_params)

    ids = [int(hit['id']) for hit in search['hits']]

    return ids, search['estimatedTotalHits']
    