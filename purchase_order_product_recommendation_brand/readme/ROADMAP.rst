* Due to `api.onchange` overriding limitations the full original list of
  fields for `_generate_recommendations` is copied here so we can add the new
  `product_brand_ids` field. This can cause that other modules extending
  `purchase_order_product_recommendation` could shadow this field list.
