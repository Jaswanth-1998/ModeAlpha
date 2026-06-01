from math import ceil

from flask import url_for


def get_page_number(args, page_param="page", default=1):
    try:
        page = int(args.get(page_param, default))
    except (TypeError, ValueError):
        return default

    return max(page, 1)


def paginate_list(
    items,
    page,
    per_page,
    endpoint,
    page_param="page",
    route_kwargs=None,
    query_args=None,
):
    total = len(items)
    pages = max(1, ceil(total / per_page)) if per_page else 1
    current_page = min(max(page, 1), pages)
    start = (current_page - 1) * per_page
    end = start + per_page

    pagination = {
        "items": items[start:end],
        "page": current_page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
        "endpoint": endpoint,
        "page_param": page_param,
        "route_kwargs": route_kwargs or {},
        "query_args": query_args or {},
    }

    pagination["has_prev"] = current_page > 1
    pagination["has_next"] = current_page < pages
    pagination["prev_num"] = current_page - 1 if pagination["has_prev"] else None
    pagination["next_num"] = current_page + 1 if pagination["has_next"] else None
    pagination["start_index"] = 0 if total == 0 else start + 1
    pagination["end_index"] = 0 if total == 0 else min(current_page * per_page, total)
    pagination["is_paginated"] = pages > 1
    pagination["links"] = build_pagination_links(pagination)
    return pagination


def build_pagination_links(pagination):
    links = [
        create_pagination_link(
            label="Previous",
            url=build_pagination_url(pagination, pagination["prev_num"])
            if pagination["has_prev"]
            else None,
            disabled=not pagination["has_prev"],
        )
    ]

    for page_number in iter_page_numbers(pagination["page"], pagination["pages"]):
        if page_number is None:
            links.append(
                create_pagination_link(
                    label="...",
                    url=None,
                    disabled=True,
                    ellipsis=True,
                )
            )
            continue

        links.append(
            create_pagination_link(
                label=str(page_number),
                url=build_pagination_url(pagination, page_number),
                active=page_number == pagination["page"],
            )
        )

    links.append(
        create_pagination_link(
            label="Next",
            url=build_pagination_url(pagination, pagination["next_num"])
            if pagination["has_next"]
            else None,
            disabled=not pagination["has_next"],
        )
    )
    return links


def create_pagination_link(label, url, active=False, disabled=False, ellipsis=False):
    return {
        "label": label,
        "url": url,
        "active": active,
        "disabled": disabled,
        "ellipsis": ellipsis,
    }


def build_pagination_url(pagination, page_number):
    if page_number is None:
        return None

    params = dict(pagination["query_args"] or {})
    params[pagination["page_param"]] = page_number
    return url_for(
        pagination["endpoint"],
        **pagination["route_kwargs"],
        **params,
    )


def iter_page_numbers(current_page, total_pages):
    if total_pages <= 7:
        return list(range(1, total_pages + 1))

    page_numbers = [1]

    if current_page > 3:
        page_numbers.append(None)

    for page_number in range(max(2, current_page - 1), min(total_pages, current_page + 2)):
        page_numbers.append(page_number)

    if current_page < total_pages - 2:
        page_numbers.append(None)

    page_numbers.append(total_pages)
    return page_numbers
