import logging
import tempfile
import subprocess
from django.conf import settings
from subprocess import CalledProcessError

logger = logging.getLogger(__name__)

SCRIPT_PATH = settings.BASE_DIR + "/bin/generate-pdf.js" 

def get_pdf_for_url(url):
  try:
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
      child = subprocess.call(["node", SCRIPT_PATH, "-w", tmp.name, "-u %s" % (url)])
      contents = tmp.read()
      return contents
  except CalledProcessError, e:
    logger.exception("getting pdf failed for url %s: %s" % (url, e.output))
