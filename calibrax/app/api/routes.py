from fastapi import APIRouter

from app.services.pricing import (
    get_overview_metrics,
    get_top_overpriced_products,
    get_competitor_price_analysis,
    get_category_price_analysis,
    get_price_index_distribution,
    get_priority_repricing_products,
    get_product_competitor_prices,
    get_filter_values,
    get_buyer_products,
    get_collection_price_analysis,
    get_prod_type_price_analysis,
    get_segment_price_analysis
)

router = APIRouter()


@router.get("/metrics")
def overview_metrics(category: str | None = None,
                        segment: str | None = None,
                        collection: str | None = None,
                        product_type: str | None = None):
    result = get_overview_metrics(category=category,
                                segment=segment,
                                collection=collection,
                                product_type=product_type)

    return result


@router.get("/overpriced-products")
def overpriced_products(limit: int = 20,
                        category: str | None = None,
                        segment: str | None = None,
                        collection: str | None = None,
                        product_type: str | None = None):

    rows = get_top_overpriced_products(
        limit=limit,
        category=category,
        segment=segment,
        collection=collection,
        product_type=product_type
    )


    return [dict(row) for row in rows]


@router.get("/competitor-analysis")
def competitor_analysis(category: str | None = None,
                        segment: str | None = None,
                        collection: str | None = None,
                        product_type: str | None = None):

    rows = get_competitor_price_analysis(
        category=category,
        segment=segment,
        collection=collection,
        product_type=product_type)

    return [dict(row) for row in rows]


@router.get("/category-analysis")
def category_analysis():
    rows = get_category_price_analysis()
    return [dict(row) for row in rows]

@router.get("/prod-type-analysis")
def prod_type_analysis():
    rows = get_prod_type_price_analysis()
    return [dict(row) for row in rows]

@router.get("/segment-analysis")
def segment_analysis():
    rows = get_segment_price_analysis()
    return [dict(row) for row in rows]

@router.get("/collection-analysis")
def collection_analysis():
    rows = get_collection_price_analysis()
    return [dict(row) for row in rows]


@router.get("/price-distribution")
def price_distribution(category: str | None = None,
                        segment: str | None = None,
                        collection: str | None = None,
                        product_type: str | None = None):

    rows = get_price_index_distribution(
        category=category,
        segment=segment,
        collection=collection,
        product_type=product_type)

    return [dict(row) for row in rows]


@router.get("/priority-repricing")
def priority_repricing(limit: int = 20,
                        category: str | None = None,
                        segment: str | None = None,
                        collection: str | None = None,
                        product_type: str | None = None):

    rows = get_priority_repricing_products(
        limit=limit,category=category,
        segment=segment,
        collection=collection,
        product_type=product_type)

    return [dict(row) for row in rows]

@router.get("/product/{product_id}")
def product_competitor_comparison(product_id: str):

    rows = get_product_competitor_prices(product_id)

    return [dict(row) for row in rows]

@router.get("/filters")
def filters(
    category: str | None = None,
    segment: str | None = None,
    collection: str | None = None,
    product_type: str | None = None):

    return get_filter_values(category=category,
        segment=segment,
        collection=collection,
        product_type=product_type)

@router.get("/buyer-products")
def buyer_products(
    search: str | None = None,
    category: str | None = None,
    segment: str | None = None,
    collection: str | None = None,
    product_type: str | None = None
):
    rows = get_buyer_products(
        search, category, segment, collection, product_type
    )

    return [dict(row) for row in rows]