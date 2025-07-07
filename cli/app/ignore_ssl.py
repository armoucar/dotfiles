"""
SSL Certificate Bypass Module

This module completely disables SSL certificate verification for HTTP requests.
Remove this import from your main code when you want to re-enable SSL verification.
"""

import requests
import urllib3
import ssl
import os


def disable_ssl_verification():
    """
    Completely disable SSL verification for all HTTP requests.
    This affects requests, urllib3, and the default SSL context.
    """
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Set environment variables to ignore SSL
    os.environ["PYTHONHTTPSVERIFY"] = "0"
    os.environ["CURL_CA_BUNDLE"] = ""

    # Create unverified SSL context
    ssl._create_default_https_context = ssl._create_unverified_context

    # Monkey patch requests to ignore SSL verification
    original_request = requests.Session.request

    def patched_request(self, method, url, **kwargs):
        kwargs["verify"] = False
        return original_request(self, method, url, **kwargs)

    requests.Session.request = patched_request

    # Also patch the module-level functions
    original_get = requests.get

    def patched_get(url, **kwargs):
        kwargs["verify"] = False
        return original_get(url, **kwargs)

    requests.get = patched_get

    print("⚠️  SSL certificate verification has been disabled!")
