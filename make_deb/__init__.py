import codecs
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
            return {"latest_git_commit": stdout[0].decode('utf-8')}
        except OSError:
            raise DebianConfigurationException("Please install git")
        except Exception as e:
            raise DebianConfigurationException(
                "Unknown error occurred when invoking git: %s" % e)

    def _context_from_setuppy(self):
        setuppy_path = os.path.join(self.rootdir, "setup.py")
        if not os.path.exists(setuppy_path):
            raise DebianConfigurationException("Failed to find setup.py")
        stdout = subprocess.Popen(
            ["python", os.path.join(self.rootdir, "setup.py"),
             "--name", "--version", "--maintainer", "--maintainer-email",
             "--description"], stdout=subprocess.PIPE).communicate()

        setup_values = stdout[0].decode('utf-8').split('\n')[:-1]
        setup_names = ["name", "version", "maintainer", "maintainer_email",
                       "description"]

        context = {}
        for name, value in zip(setup_names, setup_values):
            while not value or value == UNKNOWN:
                value = input(
                    "The '{}' parameter is not defined in setup.py. "
                    "Please define it for debian configuration: ".format(name))
                if not value:
                    print("Invalid value. Please try again")

            context[name] = value

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

            with codecs.open(os.path.join(output_dir, filename), "w", 'utf-8') as f:
                f.write(content)

        # Need to to trigger separately because filename must change
        trigger_content = Template(
            resource_string("make_deb", "resources/debian/triggers.j2").
            decode('utf-8')
        ).render(self.context)

        trigger_filename = "%s.triggers" % self.context['name']
        with open(os.path.join(output_dir, trigger_filename), "w") as f:
            f.write(trigger_content+"\n")
