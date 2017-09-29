from waitress import serve
from curriculumBuilder import wsgi

# touch app-initialized
open('/tmp/app-initialized', 'w').close()
# start waitress
serve(wsgi.application, unix_socket='/tmp/nginx.socket', send_bytes=1)