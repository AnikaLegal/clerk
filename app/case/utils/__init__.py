from django.utils.datastructures import MultiValueDict

from .fields import MultiChoiceField, SingleChoiceField
from .dynamic_table_form import DynamicTableForm
from .selector import Selector
from .htmx_form_view import HtmxFormView
from .pagination import get_page


def merge_form_data(form_data, extra_data):
    return MultiValueDict({**{k: [v] for k, v in extra_data.items()}, **form_data})
