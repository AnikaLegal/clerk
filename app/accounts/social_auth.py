from django.contrib.auth.models import Group


def set_new_user_as_cms_editor(backend, user, is_new=False, *args, **kwargs):
    """
    Ensure new users can access the Wagtail CMS
    """
    if is_new:
        editors = Group.objects.get(name="Editors")
        editors.user_set.add(user)
