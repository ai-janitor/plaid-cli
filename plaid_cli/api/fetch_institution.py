# SPEC: s2-plaid-api-client-and-sync.md
# PURPOSE: Fetch institution info (bank name) from Plaid
# RESPONSIBILITIES: Call institutions_get_by_id, return dict with institution_id and name
# NOT RESPONSIBLE FOR: Storing institution data (embedded in items table)
# DEPENDENCIES: plaid.model.institutions_get_by_id_request, plaid.model.country_code

from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.country_code import CountryCode


# --- fetch_institution(client, institution_id) → dict ---
def fetch_institution(client, institution_id: str) -> dict:
    #   --- Build InstitutionsGetByIdRequest(institution_id=institution_id, country_codes=[CountryCode('US')]) ---
    request = InstitutionsGetByIdRequest(
        institution_id=institution_id,
        country_codes=[CountryCode("US")],
    )

    #   --- response = client.institutions_get_by_id(request) ---
    response = client.institutions_get_by_id(request)

    #   --- Return {"institution_id": ..., "name": response['institution']['name']} ---
    return {
        "institution_id": institution_id,
        "name": response["institution"]["name"],
    }
