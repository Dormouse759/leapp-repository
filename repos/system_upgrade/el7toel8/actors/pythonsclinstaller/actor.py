from leapp.actors import Actor
from leapp.tags import RPMUpgradePhaseTag
from leapp.models import PythonScl
from subprocess import check_call


class PythonSclInstaller(Actor):
    """
    Call dnf to remove SCL packages and install RHEL 8 equivalents
    using the data passed by PythonScl model.
    """

    name = 'python_scl_installer'
    consumes = (PythonScl,)
    produces = ()
    tags = (RPMUpgradePhaseTag,)

    def process(self):
        for fact in self.consume(PythonScl):
            print fact
        #check_call(["/usr/bin/dnf"] + self.consume(PythonScl))
