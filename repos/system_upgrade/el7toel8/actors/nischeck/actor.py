from leapp.actors import Actor
from leapp.reporting import Report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag
from leapp.libraries.actor.nischeck import scan

class NisCheck(Actor):
    """
    Check configuration of ypbind and nsswitch. Address of NIS server cannot be
    specified by host name if NIS is used to resolve host names.
    """

    name = "check_nis_nsswitch"
    consumes = ()
    produces = (Report,)
    tags = (IPUWorkflowTag, ChecksPhaseTag)

    def process(self):
        scan()
