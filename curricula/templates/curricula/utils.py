from django.conf import settings
#from wkhtmltopdf import WKHtmlToPdf
#import boto
#from boto.s3.key import Key

import pdfkit
#import dryscrape

'''
New plan!
Generate individual pdfs to /static/curriculum/unit/lesson/lesson.pdf
Stitch into /static/curriculum/complete.pdf
Pull to S3 with collectstatic
Pray that I don't run out of space on this server!
'''

'''
conn = boto.connect_s3()
bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

wkhtmltopdf = WKHtmlToPdf(
  url='http://localhost:8000/curriculum/csp/unit1/1/?pdf=true',
  output_file='csp.pdf',
  s="Letter",
  print_media_type=True)
wkhtmltopdf.render()
'''
compiled = ''

session = dryscrape.Session()
session.visit('http://localhost:8000/curriculum/csp/unit1/1/?pdf=true')

compiled += session.body()
session.visit('http://localhost:8000/curriculum/csp/unit1/1/?pdf=true')

pdfkit.from_string(compiled, 'thePdf.pdf', options=settings.WKHTMLTOPDF_CMD_OPTIONS)