import logging
import tempfile
import subprocess
from django.conf import settings
from subprocess import CalledProcessError

logger = logging.getLogger(__name__)

SCRIPT_PATH = settings.BASE_DIR + "/bin/generate-pdf.js" 

def get_pdf_for_url(url):
  try:
    tmp = tempfile.NamedTemporaryFile(delete=True)
    child = subprocess.Popen(["node", SCRIPT_PATH, "-w", tmp.name, "-u %s" % (url)], stdout=subprocess.PIPE)
    child.communicate()
    contents = tmp.read()
    tmp.close()
    return contents
  except CalledProcessError, e:
    logger.exception("getting pdf failed for url %s: %s" % (url, e.output))
