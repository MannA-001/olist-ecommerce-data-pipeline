-- Run these queries in DuckDB after loading the cleaned CSVs as tables.
-- Expected table names: orders, order_items, order_payments, order_reviews,
-- products, sellers, customers, category_translation.

-- 1. Orders by status
SELECT order_status, COUNT(*) AS orders
FROM orders
GROUP BY order_status
ORDER BY orders DESC;

-- 2. Payment value by payment type
SELECT payment_type,
       COUNT(*) AS payment_records,
       ROUND(SUM(payment_value), 2) AS total_payment_value
FROM order_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;

-- 3. Review score distribution
SELECT review_score, COUNT(*) AS review_count
FROM order_reviews
GROUP BY review_score
ORDER BY review_score;

-- 4. Delivered orders: actual delivery versus estimated date
SELECT
    COUNT(*) AS delivered_orders,
    ROUND(AVG(date_diff('day', CAST(order_purchase_timestamp AS TIMESTAMP),
        CAST(order_delivered_customer_date AS TIMESTAMP))), 2) AS avg_days_purchase_to_delivery,
    SUM(CASE WHEN CAST(order_delivered_customer_date AS TIMESTAMP) >
        CAST(order_estimated_delivery_date AS TIMESTAMP) THEN 1 ELSE 0 END) AS delivered_late
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL;

-- 5. Category item-price and freight totals (not profit)
SELECT COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
       ROUND(SUM(i.price), 2) AS item_price_total,
       ROUND(SUM(i.freight_value), 2) AS freight_total,
       COUNT(*) AS item_lines
FROM order_items i
JOIN products p USING (product_id)
LEFT JOIN category_translation t USING (product_category_name)
GROUP BY 1
ORDER BY item_price_total DESC
LIMIT 15;

-- 6. Top sellers by item price
SELECT i.seller_id, COUNT(*) AS item_lines,
       ROUND(SUM(i.price), 2) AS item_price_total
FROM order_items i
GROUP BY i.seller_id
ORDER BY item_price_total DESC
LIMIT 20;
