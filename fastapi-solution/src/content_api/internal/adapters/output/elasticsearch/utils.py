def es_sort(sort_field: str):
    order = "desc" if sort_field.startswith("-") else "asc"
    sort_field = sort_field.lstrip("-")
    return [{sort_field: {"order": order}}]
