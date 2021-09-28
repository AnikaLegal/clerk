from django.urls import re_path, include

UUID_PARAM = "(?P<{arg_name}>[0-9a-fA-F]{{8}}-[0-9a-fA-F]{{4}}-4[0-9a-fA-F]{{3}}-[89abAB][0-9a-fA-F]{{3}}-[0-9a-fA-F]{{12}})"
INT_PK_PARAM = "(?P<{arg_name}>[0-9]+)"
SLUG_PARAM = "(?P<{arg_name}>[\-\w]+)"


class Route:
    def __init__(self, name: str):
        self.name = name
        self._params = []
        self._view_func = None

    def __call__(self, view_fn):
        self._view_func = view_fn
        return view_fn

    def to_url(self, is_base=False) -> str:
        url_path = "^" if is_base else ""
        for arg_name, param_template, is_optional in self._params:
            if not param_template:
                url_path += arg_name + "/"
            else:
                param_str = param_template.format(arg_name=arg_name)
                url_path += param_str + "?/?" if is_optional else param_str + "/"

        url_path += "$"
        return url_path

    def uuid(self, arg_name: str, optional=False):
        self._params.append((arg_name, UUID_PARAM, optional))
        return self

    def pk(self, arg_name: str, optional=False):
        self._params.append((arg_name, INT_PK_PARAM, optional))
        return self

    def slug(self, arg_name: str, optional=False):
        self._params.append((arg_name, SLUG_PARAM, optional))
        return self

    def path(self, path_name: str):
        self._params.append((path_name, None, False))
        return self


class Router:
    def __init__(self, name: str):
        self._name = name
        self._routes = {}
        self._children = {}

    def add_child(self, path: str, child_router):
        assert path not in self._children, f"Child with path {path} already exists."
        self._children[path] = child_router

    def include(self):
        return include(self._get_urlpatterns())

    def _get_urlpatterns(self, base_path: str = None, base_name: str = None):
        urlpatterns = []
        base_paths = set()
        for path, child_router in self._children.items():
            # Check that we don't have a path conflict
            msg = f"Path {path} already defined for router {self._name}: {base_paths}"
            assert path not in base_paths, msg
            base_paths.add(msg)

            # Add the child URLs with the base path.
            urlpatterns += child_router._get_urlpatterns(
                base_path=path, base_name=self._name
            )

        for route_name, route in self._routes.items():
            assert route._view_func, f"Route {route_name} not in use."
            if base_name:
                name_fragments = [base_name, self._name, route_name]
            else:
                name_fragments = [self._name, route_name]

            path_name = "-".join(name_fragments)
            path_url = route.to_url(is_base=not base_path)

            # Add the URL, optionally with base path.
            if base_path:
                path_url = base_path + path_url

            urlpatterns.append(re_path(path_url, route._view_func, name=path_name))

        return urlpatterns

    def create_route(self, name: str) -> Route:
        route = Route(name)
        self._routes[name] = route
        return route

    def add_route(self, route: Route):
        self._routes[route.name] = route

    def use_route(self, name: str):
        def decorator(view_fn):
            route = self._routes[name]
            route._view_func = view_fn
            return view_fn

        return decorator
