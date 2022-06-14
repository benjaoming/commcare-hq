# Adds the default mobile worker role to existing projects that don't yet have one.
from django.db import migrations

from corehq.apps.domain.models import Domain
from corehq.apps.users.models import Permissions
from corehq.apps.users.models_role import UserRole
from corehq.apps.users.role_utils import UserRolePresets
from corehq.util.django_migrations import skip_on_fresh_install


@skip_on_fresh_install
def _add_default_mobile_worker_role(apps, schema_editor):
    default_mobile_worker_roles = UserRole.objects.filter(is_commcare_user_default=True)
    for domain in Domain.get_all():
        dmw_roles_in_domain = default_mobile_worker_roles.filter(domain=domain)
        if len(dmw_roles_in_domain) == 0:
            UserRole.create(
                domain,
                UserRolePresets.MOBILE_WORKER,
                permissions=Permissions(),
                is_commcare_user_default=True,
            )
        elif 1 <= len(dmw_roles_in_domain) == 1:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0045_add_view_tableau_permission'),
    ]

    operations = [
        migrations.RunPython(_add_default_mobile_worker_role, migrations.RunPython.noop)
    ]
