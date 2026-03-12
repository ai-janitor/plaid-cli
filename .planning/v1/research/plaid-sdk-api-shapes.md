# Plaid SDK API Shapes

## /transactions/sync
- Request: `TransactionsSyncRequest(access_token, cursor?, count?)` — count default 100, max 500
- Response: `added[]`, `modified[]`, `removed[]`, `next_cursor`, `has_more`, `accounts[]`
- Transaction fields: `transaction_id`, `account_id`, `date`, `amount`, `name`, `merchant_name`, `pending`, `iso_currency_code`, `category[]`, `payment_channel`, `authorized_date`, `location`
- Pagination: loop while `has_more == true`, pass `next_cursor`
- Cursor valid for 1+ year

## Sandbox Public Token Creation
- Request: `SandboxPublicTokenCreateRequest(institution_id, initial_products)`
- Default institution: `ins_109508` (Chase-like)
- Response: `public_token` → exchange for `access_token`
- Options: `days_requested` (1-730) to control transaction history depth

## Token Exchange
- Request: `ItemPublicTokenExchangeRequest(public_token)`
- Response: `access_token`, `item_id`

## Account Metadata (/accounts/get)
- Request: `AccountsGetRequest(access_token)`
- Response: `accounts[]` with: `account_id`, `name`, `official_name`, `type`, `subtype`, `mask` (last 4), `balances` (available, current, limit)

## Institution Info (/institutions/get_by_id)
- Request: `InstitutionsGetByIdRequest(institution_id, country_codes)`
- Response: `institution_id`, `name`, `url`, `logo`, `products[]`, `routing_numbers[]`

## Multi-Item Management
- **No API to list all Items.** Track access_tokens yourself.
- Per-Item metadata: `ItemGetRequest(access_token)` → `item_id`, `institution_id`, `institution_name`, `products[]`, `status`
- Pattern: store `{item_id: access_token}` in DB, call `/accounts/get` per token for account details
