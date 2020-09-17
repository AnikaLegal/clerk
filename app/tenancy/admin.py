from django.contrib import admin

from utils.admin import admin_link
from .models import Tenancy


@admin.register(Tenancy)
class TenancyAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "address",
        "client_link",
        "landlord_link",
        "agent_link",
        "created_at",
    )
    list_select_related = (
        "client",
        "landlord",
        "agent",
    )

    @admin_link("client", "Client")
    def client_link(self, client):
        return client.get_full_name()

    @admin_link("landlord", "Landlord")
    def landlord_link(self, landlord):
        return landlord.full_name

    @admin_link("agent", "Agent")
    def agent_link(self, agent):
        return agent.full_name
