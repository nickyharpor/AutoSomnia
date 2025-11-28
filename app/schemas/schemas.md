## account

{
"user_id": int,
"address": evm-compatible address (str or bytes),
"private_key": evm-compatible private key (str or bytes),
"is_imported": boolean,
"created_at": datetime,
"updated_at": datetime
}

## user

{
"user_id": int,
"first_name": str,
"last_name": str,
"username": str,
"photo_url": str,
"api_key": str,
"auto_exchange": boolean,
"created_at": datetime,
"updated_at": datetime
}

## payment

{
"payment_id": str,
"merchant_id": int,
"order_id": str,
"price_in_cents": int,
"status": str,
"created_at": datetime,
"updated_at": datetime
}

## payment_account

{
"payment_id": str,
"address": str,
"private_key": str,
"chain_id": int,
"memo": str,
"is_imported": boolean,
"created_at": datetime,
"updated_at": datetime
}

## gateway

{
"gateway_id": int,
"name": str,
"redirect_url": str,
"callback": str,
"allowed_origin": str,
"created_at": datetime,
"updated_at": datetime
}