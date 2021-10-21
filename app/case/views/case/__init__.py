from case.utils.router import Router

from .list import list_route, inbox_route, review_route, search_route
from .detail import detail_route, agent_route, landlord_route
from .email import router as email_router
from .docs import docs_route, docs_sharepoint_route

router = Router("case")
router.add_child("email/", email_router)
router.add_route(list_route)
router.add_route(search_route)
router.add_route(inbox_route)
router.add_route(review_route)
router.add_route(docs_route)
router.add_route(docs_sharepoint_route)
router.add_route(agent_route)
router.add_route(landlord_route)
router.add_route(detail_route)
