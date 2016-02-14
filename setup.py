#!/usr/bin/env python

from setuptools import setup


setup(
    name='make-deb',
    version='0.0.5',
    include_package_data = True,
    packages = ['make_deb'],
    author = "Rob McQueen",
    author_email = "rob@nylas.com",
    maintainer = "Nylas Team",
    maintainer_email = "support@nylas.com",
    description = "Generates Debian configuration based on your setup.py",
    package_data = {
        "make_deb": [
            "resources/debian/control.j2",
            "resources/debian/rules.j2",
            "resources/debian/triggers.j2",
            "resources/debian/changelog.j2",
            "resources/debian/compat.j2"
            ]
        },
    scripts=['bin/make-deb'],
    install_requires=['future', 'Jinja2'],
    zip_safe=False
)
