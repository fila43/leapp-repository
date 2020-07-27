from leap.actors import Actor
from leap.reporting import Report
from leap.tags.import ChecksPhaseTag, IPUWorkflowTag
from leap.libraries.actor import nisscanner

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
        scanner = Nisscanner()
        scanner.scan()

