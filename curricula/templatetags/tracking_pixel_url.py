from django import template
import urllib
import random

register = template.Library()

@register.filter(name='tracking_pixel_url')

def tracking_pixel_url(path):
    # Append a random number so that the tracking_pixel
    # isn't cached - we want each visit to a url to go
    # fetch a new tracking pixel image.
    random_num = random.randint(1,1001)
    tracking_pixel_url = 'http://localhost-studio.code.org:3000/tracking_pixel?from=' + urllib.quote_plus(path) + '&r=' + str(random_num)
    return tracking_pixel_url
