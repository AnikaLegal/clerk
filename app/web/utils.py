from case.utils.react import render_react_page_base


def render_react_page(
    request, title, react_page_name, react_context, public=False, status=None
):
    return render_react_page_base(
        request,
        title,
        react_page_name,
        react_context,
        public,
        status,
        "web/react_base.html",
    )
