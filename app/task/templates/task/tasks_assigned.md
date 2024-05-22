{% if tasks|length > 1 %}New tasks have{% else %}A new task has{% endif %} been assigned to you in Clerk:
{% for task in tasks %}
- {{ task.type }} - {{ task.name }}
{% endfor %}