from case.utils.router import Router

from .list import (
    list_route,
    inbox_route,
    review_route,
    checks_route,
    review_search_route,
)
from .detail import router as detail_router
from .email import router as email_router
from .docs import docs_route, docs_sharepoint_route

router = Router("case")
router.add_child("email/", email_router)
router.add_child("detail/", detail_router)
router.add_route(list_route)
router.add_route(inbox_route)
router.add_route(review_search_route)
router.add_route(review_route)
router.add_route(docs_route)
router.add_route(docs_sharepoint_route)
router.add_route(checks_route)
