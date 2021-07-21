from collections import Counter

from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from corehq.apps.domain.decorators import login_and_domain_required, domain_admin_required
from corehq.apps.domain.models import Domain
from corehq.apps.enterprise.decorators import require_enterprise_admin
from corehq.apps.registry.models import DataRegistry, RegistryInvitation


@require_enterprise_admin
@login_and_domain_required
def data_registries(request, domain):
    owned, invited = [], []
    for registry in DataRegistry.objects.visible_to_domain(domain):
        if registry.domain == domain:
            owned.append(_registry_list_context(domain, registry))
        else:
            invited.append(_registry_list_context(domain, registry))

    context = {
        'domain': domain,
        'owned_registries': owned,
        'invited_registries': invited,
        'current_page': {
            'title': _('Data Registries'),
            'page_name': _('Data Registries'),
        },
    }
    return render(request, "registry/registry_list.html", context)


def _registry_list_context(domain, registry):
    invitations = registry.invitations.all()
    domain_obj = Domain.get_by_name(registry.domain)
    other_domain_invitations = [
        invitation for invitation in invitations
        if not invitation.domain == domain
    ]
    context = {
        "domain_name": domain_obj.display_name() if domain_obj else registry.domain,
        "name": registry.name,
        "description": registry.description or '',
        "slug": registry.slug,
        "is_active": registry.is_active,
        "participator_count": len([
            invitation for invitation in other_domain_invitations
            if invitation.status == RegistryInvitation.STATUS_ACCEPTED
        ])
    }
    if domain == registry.domain:  # domain is owner
        status_counter = Counter([invitation.status for invitation in other_domain_invitations])
        context.update({
            "invitation_count": len(invitations),
            "accepted_invitation_count": status_counter[RegistryInvitation.STATUS_ACCEPTED],
            "pending_invitation_count": status_counter[RegistryInvitation.STATUS_PENDING],
            "rejected_invitation_count": status_counter[RegistryInvitation.STATUS_REJECTED]
        })
    else:
        for_this_domain = [invitation for invitation in invitations if invitation.domain == domain]
        context.update({
            "invitation": for_this_domain[0].to_json()
        })
    return context


@domain_admin_required
@require_POST
def accept_registry_invitation(request, domain):
    registry_slug = request.POST.get('registry_slug')
    invitation = _get_invitation_or_404(domain, registry_slug)

    if not invitation.is_accepted:
        invitation.accept(request.user)

    return JsonResponse(_registry_list_context(domain, invitation.registry))


@domain_admin_required
@require_POST
def reject_registry_invitation(request, domain):
    registry_slug = request.POST.get('registry_slug')
    invitation = _get_invitation_or_404(domain, registry_slug)

    if not invitation.is_rejected:
        invitation.reject(request.user)

    return JsonResponse(_registry_list_context(domain, invitation.registry))


def _get_invitation_or_404(domain, registry_slug):
    try:
        return RegistryInvitation.objects.get(
            registry__slug=registry_slug,
            domain=domain
        )
    except RegistryInvitation.DoesNotExist:
        raise Http404
