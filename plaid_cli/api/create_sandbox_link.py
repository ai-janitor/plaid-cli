# SPEC: s2-plaid-api-client-and-sync.md
# PURPOSE: Create a sandbox public token (skips Plaid Link UI for testing)
# RESPONSIBILITIES: Call sandbox_public_token_create, return public_token
# NOT RESPONSIBLE FOR: Token exchange (separate function), real bank Link flow
# DEPENDENCIES: plaid.model.sandbox_public_token_create_request, plaid.model.products

from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.products import Products


# --- create_sandbox_link(client, institution_id="ins_109508", products=["transactions"]) → str ---
def create_sandbox_link(client, institution_id: str = "ins_109508", products: list[str] | None = None) -> str:
    if products is None:
        products = ["transactions"]

    #   --- Build SandboxPublicTokenCreateRequest(institution_id=institution_id, initial_products=[Products(p) for p in products]) ---
    request = SandboxPublicTokenCreateRequest(
        institution_id=institution_id,
        initial_products=[Products(p) for p in products],
    )

    #   --- response = client.sandbox_public_token_create(request) ---
    response = client.sandbox_public_token_create(request)

    #   --- Return response['public_token'] ---
    return response["public_token"]
