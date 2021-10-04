from case.utils.router import Router
from .list import list_route
from .detail import detail_route


router = Router("account")
router.add_route(detail_route)
router.add_route(list_route)
