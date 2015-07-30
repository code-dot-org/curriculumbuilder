from data_importer.importers import CSVImporter
from standards.models import Standard

class StandardImporter(CSVImporter):
  fields = ['name', 'shortcode', 'framework', 'category', 'gradeband']
  class Meta:
    delimiter = ','
    model = Standard
    ignore_first_line = True
    raise_errors = True
    