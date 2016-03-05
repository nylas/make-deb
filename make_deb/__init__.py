import setuptools
from distutils.core import run_setup
import datetime
import os
from pkg_resources import resource_string
import shutil
import subprocess

from builtins import input
from jinja2 import Template

# String setuptools uses to specify None
UNKNOWN = "UNKNOWN"


class DebianConfigurationException(Exception):
    pass


class DebianConfiguration(object):
    '''
    Given a root directory which contains a setup.py file,
    initializes debian configuration files in the debian directory
    '''

    DEBIAN_CONFIGURATION_TEMPLATES = [
        "resources/debian/changelog.j2",
        "resources/debian/compat.j2",
        "resources/debian/control.j2",
        "resources/debian/rules.j2",
    ]

    DEFAULT_CONTEXT = {
        "compat": 9,
    }

    def __init__(self, rootdir):
        self.rootdir = rootdir
        self.context = self.DEFAULT_CONTEXT.copy()
        self.context.update({"date": datetime.datetime.now()})
        self.context.update(self._context_from_setuppy())
        self.context.update(self._context_from_git())

    def _context_from_git(self):
        try:
            stdout = subprocess.Popen(
                ["git", "log", "-1", "--oneline"],
                cwd=self.rootdir,
                stdout=subprocess.PIPE).communicate()
            return {"latest_git_commit": stdout[0]}
        except OSError:
            raise DebianConfigurationException("Please install git")
        except Exception as e:
            raise DebianConfigurationException(
                "Unknown error occurred when invoking git: %s" % e)

    def _context_from_setuppy(self):
        setuppy_path = os.path.join(self.rootdir, "setup.py")
        if not os.path.exists(setuppy_path):
            raise DebianConfigurationException("Failed to find setup.py")

        dist = run_setup(setuppy_path)
        context = {
            'name': dist.get_name(),
            'version': dist.get_version(),
            'maintainer': dist.get_maintainer(),
            'maintainer_email': dist.get_maintainer_email(),
            'description': dist.get_description(),
        }

        scripts = []
        if dist.entry_points is not None and 'console_scripts' in dist.entry_points:
            scripts += [script.split('=')[0] for script in dist.entry_points['console_scripts']]

        if dist.scripts is not None:
            scripts += [script.rsplit('/', 1)[-1] for script in dist.scripts]

        for name, value in context.items():
            while not value or value == UNKNOWN:
                value = input(
                    "The '{}' parameter is not defined in setup.py. "
                    "Please define it for debian configuration: ".format(name))
                if not value:
                    print("Invalid value. Please try again")

            context[name] = value

        context['scripts'] = scripts

        return context

    def render(self):
        output_dir = os.path.join(self.rootdir, "debian")

        if os.path.exists(output_dir):
            res = input("A debian directory exists. Replace it? [Y/n]: ")
            if res.lower() in ["n", "no"]:
                raise DebianConfigurationException(
                    "Not removing debian directory")
            shutil.rmtree(output_dir)

        os.mkdir(output_dir)

        for template in self.DEBIAN_CONFIGURATION_TEMPLATES:
            filename = os.path.basename(template).replace(".j2", "")
            content = Template(
                resource_string("make_deb", template).decode('utf-8')
            ).render(self.context)

            with open(os.path.join(output_dir, filename), "w") as f:
                f.write(content)

        # Need to to trigger separately because filename must change
        for template in ['resources/debian/triggers.j2', 'resources/debian/links.j2']:
            trigger_content = Template(
                resource_string("make_deb", template).
                decode('utf-8')
            ).render(self.context)

            trigger_filename = "%s.%s" % (self.context['name'], template.split('.j2')[0].rsplit('/',1)[-1])
            with open(os.path.join(output_dir, trigger_filename), "w") as f:
                f.write(trigger_content+"\n")
