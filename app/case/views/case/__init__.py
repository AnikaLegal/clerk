from case.utils.router import Router

from .list import list_route, inbox_route, review_route
from .detail import detail_route
from .email import router as email_router

router = Router("case")
router.add_child("email/", email_router)
router.add_route(list_route)
router.add_route(inbox_route)
router.add_route(review_route)
router.add_route(detail_route)
