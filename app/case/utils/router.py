from django.urls import re_path, include

UUID_PARAM = "(?P<{arg_name}>[0-9a-fA-F]{{8}}-[0-9a-fA-F]{{4}}-4[0-9a-fA-F]{{3}}-[89abAB][0-9a-fA-F]{{3}}-[0-9a-fA-F]{{12}})"
INT_PK_PARAM = "(?P<{arg_name}>[0-9]+)"
SLUG_PARAM = "(?P<{arg_name}>[\-\w]+)"


class RoutedPath:
    def __init__(self, name: str):
        self.name = name
        self._params = []

    def to_url(self) -> str:
        url_path = ""
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
        self._used_paths = []
        self._defined_paths = {}

    def urls(self):
        urlpatterns = []
        for view_fn, routed_path in self._used_paths:
            path_name = "-".join([self._name, routed_path.name])
            path_url = routed_path.to_url()
            urlpatterns.append(re_path(path_url, view_fn, name=path_name))

        return include(urlpatterns)

    def add_path(self, name: str) -> RoutedPath:
        routed_path = RoutedPath(name)
        self._defined_paths[name] = routed_path
        return routed_path

    def use_path(self, name: str):
        def decorator(view_fn):
            routed_path = self._defined_paths[name]
            self._used_paths.append((view_fn, routed_path))
            return view_fn

        return decorator
