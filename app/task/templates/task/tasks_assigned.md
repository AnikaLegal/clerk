*New Task Notification*
{% if tasks|length > 1 %}New tasks have{% else %}A new task has{% endif %} been assigned to you for case <{{ base_url }}{% url 'case-detail' issue.pk %}|{{ issue.fileref }}>.
You can view this case's tasks <{{ base_url }}{% url 'case-task-list' issue.pk %}|here>.