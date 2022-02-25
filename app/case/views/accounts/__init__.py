from case.utils.router import Router
from .list import list_route
from .detail import router as detail_router
from .create import create_route

router = Router("account")
router.add_child("user/", detail_router)
router.add_route(list_route)
router.add_route(create_route)