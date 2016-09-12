# {{ lesson.unit }}: Lesson {{ lesson.number }} - {{ lesson.title }}

## Background

{{ lesson.overview }}
{% if lesson.vocab.count > 0 %}# Vocabulary

{% for word in lesson.vocab.all %}* **{{ word.word }}** - {{ word.detailDef }}
{% endfor %}{% endif %}
{% if lesson.blocks.count > 0 %}# New Blocks

{% for block in lesson.blocks.all %}* **{{ block.title }}** - `{{ block.code }}`
{% endfor %}{% endif %}
{% if lesson.resources.count > 0 %}# Resources

{% for resource in lesson.resources.all %}{% if resource.student %}* {{ resource.formatted_md|safe }}{% endif %}
{% endfor %}{% endif %}