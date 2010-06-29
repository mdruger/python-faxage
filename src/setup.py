#! /usr/bin/env python

import os, string, sys
from setuptools import setup

PACKAGE = "faxage"

def main():
    kwargs = {
        'name'                    : "%s" % PACKAGE,
        'version'                 : "1.1",
        'description'             : "Python classes for the Faxage Internet faxing service API.",
        'author'                  : "Ben Timby",
        'author_email'            : "btimby@ftphosting.net",
        'maintainer'              : "Ben Timby",
        'maintainer_email'        : "btimby@ftphosting.net",
        'url'                     : "http://www.ftphosting.net/",
        'license'                 : "GPL",
        'platforms'               : "UNIX",
        'long_description'        : "Faxage Internet faxing service API client. Allows sending and receiving of faxes, as well as allocating additional phone numbers and releasing them.",
        'packages'                : ['faxage'],
    }
    setup(**kwargs)

if __name__ == "__main__":
	main()