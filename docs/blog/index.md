{% for post in blog.posts   sort(attribute="date", reverse=true) | slice(0, 5) %}
- **[{{ post.title }}]({{ post.url }})** ({{ post.date | format_date }})
  {{ post.excerpt }}
{% endfor %}
