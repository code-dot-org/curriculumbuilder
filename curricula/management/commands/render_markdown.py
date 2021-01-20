# pylint: disable=missing-docstring
import json
import os
import io

from django.core.management.base import BaseCommand, CommandError
from mezzanine.core.templatetags.mezzanine_tags import richtext_filters


class Command(BaseCommand):
    help = 'Renders markdown in the given files. Supports JSON.'

    def add_arguments(self, parser):
        parser.add_argument('filepaths', nargs='+', help='the filepath(s) to be rendered')

    def render(self, data):
        if isinstance(data, dict):
            return {key: self.render(value) for key, value in data.iteritems()}
        elif isinstance(data, list):
            return [self.render(datum) for datum in data]
        elif isinstance(data, basestring):
            return richtext_filters(data)
        else:
            raise CommandError("cannot render unknown data type: %s" % type(data))

    def process_file(self, filepath):
        file_name, file_extension = os.path.splitext(os.path.basename(filepath))
        if file_extension != ".json":
            raise CommandError("cannot parse non-json file '%s'" % filepath)

        with open(filepath) as file_object:
            data = json.load(file_object)

        rendered = self.render(data)
        dest = "/tmp/" + file_name + ".python-markdown.json"

        print("writing to " + dest)

        with io.open(dest, 'w', encoding='utf8') as json_file:
            data = json.dumps(rendered, ensure_ascii=False, indent=4)
            json_file.write(unicode(data))

    def handle(self, *args, **options):
        for filepath in options["filepaths"]:
            self.process_file(filepath)
