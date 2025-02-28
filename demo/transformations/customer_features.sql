-- Transformação SQL para calcular métricas de clientes
WITH order_totals AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.id) as total_orders,
        SUM(oi.price * oi.quantity) as total_spent
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    GROUP BY o.customer_id
)
SELECT
    c.id as customer_id,
    COALESCE(ot.total_orders, 0) as total_orders,
    COALESCE(ot.total_spent, 0.0) as total_spent,
    CASE 
        WHEN ot.total_orders > 0 THEN ot.total_spent / ot.total_orders 
        ELSE 0.0 
    END as avg_order_value
FROM customers c
LEFT JOIN order_totals ot ON c.id = ot.customer_id
