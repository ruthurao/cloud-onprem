"""Homeowners applications with enrichment already attached.

Week 8 lookup rows for these two ids are copied here so the scorer does not
import intake, enrichment, or the lookup module.
"""

APP_1001 = {
    "id": "APP-1001",
    "applicant_id": "APP-1001",
    "full_name": "Alice Chen",
    "product": "homeowners",
    "claims": {"at_fault": 0, "not_at_fault": 0, "total_loss": False, "dui_related": False},
    "credit": {"band": "excellent"},
    "assets": {
        "flood_zone": "X",
        "roof_year": 2019,
        "unpermitted_structure": False,
        "prior_damage": False,
    },
}

APP_1003 = {
    "id": "APP-1003",
    "applicant_id": "APP-1003",
    "full_name": "Jordan Pike",
    "product": "homeowners",
    "claims": {"at_fault": 2, "not_at_fault": 0, "total_loss": True, "dui_related": True},
    "credit": {"band": "poor"},
    "assets": {
        "flood_zone": "AE",
        "roof_year": 2012,
        "unpermitted_structure": False,
        "prior_damage": False,
    },
}

APPLICATIONS = {
    "APP-1001": APP_1001,
    "APP-1003": APP_1003,
}


def enrichment_for(application):
    return {
        "claims": application["claims"],
        "credit": application["credit"],
        "assets": application["assets"],
    }
