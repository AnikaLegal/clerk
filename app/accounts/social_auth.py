from django.contrib.auth.models import Group


def set_new_user_as_cms_editor(backend, user, is_new=False, *args, **kwargs):
    editors = Group.objects.get(name="Editors")
    editors.user_set.add(user)
