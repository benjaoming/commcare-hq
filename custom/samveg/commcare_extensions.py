from corehq.apps.case_importer.extension_points import (
    custom_case_upload_file_checks,
    custom_case_upload_operations,
)
from custom.samveg.case_importer.validators import MandatoryColumnsValidator, MandatoryValueValidator
from custom.samveg.const import SAMVEG_DOMAINS

validators = [
    MandatoryColumnsValidator,
]

row_level_operations = [
    MandatoryValueValidator,
]


@custom_case_upload_file_checks.extend(domains=SAMVEG_DOMAINS)
def samveg_case_upload_checks(domain, case_upload):
    errors = []
    with case_upload.get_spreadsheet() as spreadsheet:
        for validator in validators:
            errors.extend(getattr(validator, 'run')(spreadsheet))
    return errors


@custom_case_upload_operations.extend(domains=SAMVEG_DOMAINS)
def samveg_case_upload_row_operations(domain, row_num, raw_row, fields_to_update):
    all_errors = []
    for operation in row_level_operations:
        if hasattr(operation, 'run'):
            fields_to_update, errors = getattr(operation, 'run')(row_num, raw_row, fields_to_update)
            all_errors.extend(errors)
    return fields_to_update, all_errors
