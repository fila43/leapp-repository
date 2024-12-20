import os

from leapp import reporting
from leapp.actors import Actor
from leapp.models import FirmwareFacts
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag


class EfiCheckBoot(Actor):
    """
    Adjust EFI boot entry for first reboot
    """

    name = 'efi_check_boot'
    consumes = (FirmwareFacts,)
    produces = (reporting.Report,)
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    def process(self):
        is_system_efi = False
        has_efibootmgr = os.path.exists('/sbin/efibootmgr')
        for fact in self.consume(FirmwareFacts):
            if fact.firmware == 'efi':
                is_system_efi = True
                break

        if is_system_efi and not has_efibootmgr:
            reporting.create_report([
                reporting.Title('efibootmgr package is required on EFI systems'),
                reporting.Summary(
                    'efibootmgr is required so that we can can set proper boot options in between restarts'
                ),
                reporting.Remediation(commands=[['yum', '-y', 'install', 'efibootmgr']]),
                reporting.RelatedResource('package', 'efibootmgr'),
                reporting.Flags([reporting.Flags.INHIBITOR]),
                reporting.Severity(reporting.Severity.HIGH),
                reporting.Tags([reporting.Tags.BOOT])
            ])
