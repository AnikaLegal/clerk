from django.contrib.auth.models import Group
from microsoft import service


def set_new_user_as_cms_editor(backend, user, is_new=False, *args, **kwargs):
    """
    Ensure new users can access the Wagtail CMS
    """
    if is_new:
        editors = Group.objects.get(name="Editors")
        editors.user_set.add(user)


def set_up_new_user_in_microsoft(backend, user, is_new=False, *args, **kwargs):
    """
    Give new users MS account and E1 license
    """
    if is_new:
        service.set_up_new_user(user)
