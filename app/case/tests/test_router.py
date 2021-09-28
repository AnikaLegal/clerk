from case.utils.router import Route, Router


def test_router__add_child():
    router = Router("test")
    child_router = Router("child")
    router.add_child("extra", child_router)
    child_router.add_path("foo").pk("pk").path("detail")

    @child_router.use_path("foo")
    def view():
        pass

    urlpatterns, _, _ = router.include()
    assert urlpatterns[0].pattern._regex == r"extra/(?P<pk>[0-9]+)/detail/$"
    assert urlpatterns[0].name == r"test-child-foo"


def test_router___include():
    router = Router("test")
    router.add_path("detail").pk("pk").path("detail")
    assert router._defined_paths["detail"].to_url() == r"(?P<pk>[0-9]+)/detail/$"

    @router.use_path("detail")
    def view():
        pass

    assert router._used_paths[0] == (view, router._defined_paths["detail"])

    urlpatterns, _, _ = router.include()
    assert urlpatterns[0].pattern._regex == r"(?P<pk>[0-9]+)/detail/$"
    assert urlpatterns[0].name == r"test-detail"


def test_routed_path__with_no_params():
    rp = Route("test")
    assert rp.to_url() == r"$"


def test_routed_path__with_many_params():
    rp = Route("test").path("aaa").pk("bbb").path("ccc").slug("ddd")
    assert rp.to_url() == r"aaa/(?P<bbb>[0-9]+)/ccc/(?P<ddd>[\-\w]+)/$"


def test_routed_path__with_path():
    rp = Route("test").path("foo")
    assert rp.to_url() == r"foo/$"


def test_routed_path__with_slug():
    rp = Route("test").slug("foo")
    assert rp.to_url() == r"(?P<foo>[\-\w]+)/$"


def test_routed_path__with_optional_slug():
    rp = Route("test").slug("foo", optional=True)
    assert rp.to_url() == r"(?P<foo>[\-\w]+)?/?$"


def test_routed_path__with_pk():
    rp = Route("test").pk("foo")
    assert rp.to_url() == r"(?P<foo>[0-9]+)/$"


def test_routed_path__with_optional_pk():
    rp = Route("test").pk("foo", optional=True)
    assert rp.to_url() == r"(?P<foo>[0-9]+)?/?$"


def test_routed_path__with_uuid():
    rp = Route("test").uuid("foo")
    assert (
        rp.to_url()
        == r"(?P<foo>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})/$"
    )


def test_routed_path__with_optional_uuid():
    rp = Route("test").uuid("foo", optional=True)
    assert (
        rp.to_url()
        == r"(?P<foo>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})?/?$"
    )
