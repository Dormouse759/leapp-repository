from leapp.actors import Actor
from leapp.tags import ChecksPhaseTag
from leapp.models import PythonScl, Report
from leapp.libraries.common import reporting


class PythonGetSclInfo(Actor):
    """
    This actor finds out which Python collections are installed and
    (if they exist) installs equivalents on RHEL 8.
    """

    name = 'python_get_scl_info'
    consumes = ()
    produces = (PythonScl,Report)
    tags = (ChecksPhaseTag,)

    class SCLToRHELConverter:

        def __init__(self):
            import json
            # Determines which SCLs are installed
            self.scls = {}

            # Warn that Python 3 is Python 3.6
            # if user has Python < 3.6 SCL
            self.raise_3x_warning = False

            with open("collections_to_el8.json", "r") as f:
                dump = f.read()
                self.pkg_pairs = json.loads(dump)[0]

        def scan_dirs(self):
            from os import path
            scl_dir = "/opt/rh/"

            # Return and exit, as there is nothing to do
            if not path.exists(scl_dir):
                return False

            # Search for directories with specific SCLs
            for python in ["python27", "python33", "rh-python34",
                           "rh-python35", "rh-python36"]:
                python_dir = path.join(scl_dir, python)
                if path.exists(python_dir):
                    # Assign empty list for packages to replace
                    self.scls[python] = []
                    # If any Python 3 < 3.6 is present, raise a warning
                    if (python == "python33"
                       or python == "rh-python34"
                       or python == "rh-python35"):
                        self.raise_3x_warning = True


            return True

        def get_installed_scl_pkgs(self):
            import yum

            # Get yum database
            db = yum.YumBase()

            # Scan through rpmdb (installed only) packages, find collections
            # and assign them to a corresponding list in the scls dict.
            for pkg in db.rpmdb.pkglist:
                name = pkg[0]

                for key in self.scls:
                    if name.startswith(str(key)):
                        self.scls[key].append(name)

        def print_packages(self):
            "Test only, delete me before pull request."
            for key in self.scls:
                print(key)
                for pkg in self.scls[key]:
                    print "    " + pkg + " : " + self.pkg_pairs[key][pkg]

        def get_lists(self):
            retval = {
                        "SCL" : [],
                        "el8" : []
                    }

            for key in self.scls:
                for pkg in self.scls[key]:
                    to_append = self.pkg_pairs[key][pkg]
                    retval["SCL"].append(pkg)

                    if to_append == "None":
                        continue
                    elif to_append == "Gone":
                        self.raise_warning(to_append)
                        continue
                    else:
                        retval["el8"].append(to_append)

            return retval

        def raise_warning(self, missing):
            #FIXME
            reporting.report_generic(title="Missing: {pkg}".format(pkg=missing,
                                     severity="high",
                                     summary="The package {pkg} is missing.".format(pkg=missing)))


    def process(self):

        con = self.SCLToRHELConverter()

        if not con.scan_dirs():
            return

        con.get_installed_scl_pkgs()

        con.print_packages()

        lists = con.get_lists()
        if con.raise_3x_warning:
            reporting.report_generic(title="FIXME",
                                     severity="high",
                                     summary="FIXME")

        self.produce(PythonScl(pkgs=lists["el8"],
                               scls=lists["SCL"]
                               ))


