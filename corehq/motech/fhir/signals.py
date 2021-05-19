from couchforms.signals import successful_form_received

from corehq.motech.repeaters.signals import create_repeat_records


def create_fhir_repeat_records(sender, xform, **kwargs):
    from .repeaters import FHIRRepeater
    create_repeat_records(FHIRRepeater, xform)


successful_form_received.connect(create_fhir_repeat_records)
