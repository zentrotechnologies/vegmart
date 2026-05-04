
from io import BytesIO
from django.core.files.storage import FileSystemStorage
import time
from .validations import hosturl
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from vegmart.settings import *
import locale
from urllib.parse import urlparse, parse_qs
from datetime import datetime,date,timedelta
from mimetypes import guess_type
from django.conf import settings
import logging
from django.utils.text import slugify

import re
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def format_indian_rupees(number):
    """
    Format number in Indian numbering system without using locale
    """
    try:
        number = int(number)
        
        # Handle negative numbers
        sign = '-' if number < 0 else ''
        number = abs(number)
        
        if number == 0:
            return '0'
        
        # Convert to string and process
        num_str = str(number)
        length = len(num_str)
        
        # Indian numbering system: grouped as 3,2,2,...
        if length <= 3:
            return f"{sign}{num_str}"
        
        # Last 3 digits
        result = num_str[-3:]
        num_str = num_str[:-3]
        
        # Group remaining digits in 2s
        while len(num_str) > 0:
            if len(num_str) >= 2:
                result = num_str[-2:] + ',' + result
                num_str = num_str[:-2]
            else:
                result = num_str + ',' + result
                num_str = ''
        
        return f"{sign}{result}"
    
    except (ValueError, TypeError):
        return "0"

def extract_lat_lng_from_url(google_maps_url):
    # Parse the URL
    parsed_url = urlparse(google_maps_url)
    # Extract the path and split by '/'
    path_segments = parsed_url.path.split('/')
    for segment in path_segments:
        if '@' in segment:  # Look for the segment with '@' containing coordinates
            coordinates = segment.split('@')[1].split(',')[:2]  # Get lat and lng
            latitude = coordinates[0]
            longitude = coordinates[1]
            return float(latitude), float(longitude)
    return None, None

def to_float(val, default=0):
    try:
        if val in ["", None]:
            return default
        return float(val)
    except:
        return default
































































