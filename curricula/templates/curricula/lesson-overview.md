## {{ lesson.unit }}: Lesson {{ lesson.number }} - {{ lesson.title }}

# Background

{{ lesson.overview }}

{% if lesson.vocab.count > 0 %}
# Vocabulary

{% for word in lesson.vocab.all %}
* **{{ word.word }}** - {{ word.detailDef }}
{% endfor %}
{% endif %}

{% if lesson.resources.count > 0 %}
# Resources
{% with lesson.resources.all as resources %}
{% regroup resources|dictsort:"student" by student as resources_by_audience %}
{% for audience in resources_by_audience %}

### For the {{ audience.grouper|yesno:"Students,Teacher" }}

{% for resource in audience.list %}
* {{ resource.formatted|safe }}
{% endfor %}
{% endfor %}
{% endwith %}
{% endif %}
