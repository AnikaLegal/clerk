{% if tasks|length > 1 %}New tasks have{% else %}A new task has{% endif %} been assigned to you in Clerk:
{% for task in tasks %}
- <{{ base_url }}{{ task.url }}|{{ task.get_type_display }} - {{ task.name }}>
  {% endfor %}
