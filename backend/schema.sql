-- =============================================================================
-- Orders Management System — Schema inicial
-- Entregável obrigatório conforme especificação do desafio técnico
-- PostgreSQL 16+
-- =============================================================================

-- Garante idempotência: pode ser re-executado sem erros
-- Ordem de criação respeita as dependências de FK

-- -----------------------------------------------------------------------------
-- 1. Clientes
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id   VARCHAR(20)  PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    city          VARCHAR(100),
    state         CHAR(2),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_customers_email
    ON customers (customer_email);

-- -----------------------------------------------------------------------------
-- 2. Produtos
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id   VARCHAR(20)  PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category     VARCHAR(100) NOT NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_category
    ON products (category);

-- -----------------------------------------------------------------------------
-- 3. Pedidos
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id    VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL
        REFERENCES customers (customer_id) ON DELETE RESTRICT,
    status      VARCHAR(20) NOT NULL
        CONSTRAINT ck_orders_status
            CHECK (status IN ('processing', 'shipped', 'delivered', 'cancelled')),
    created_at  TIMESTAMPTZ NOT NULL,
    updated_at  TIMESTAMPTZ NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices individuais para filtros isolados
CREATE INDEX IF NOT EXISTS idx_orders_status
    ON orders (status);

CREATE INDEX IF NOT EXISTS idx_orders_created_at
    ON orders (created_at);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id
    ON orders (customer_id);

-- Índice composto para o filtro mais comum: status + período
CREATE INDEX IF NOT EXISTS idx_orders_status_created_at
    ON orders (status, created_at);

-- -----------------------------------------------------------------------------
-- 4. Itens de pedido
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id     VARCHAR(20) NOT NULL
        REFERENCES orders (order_id) ON DELETE CASCADE,
    product_id   VARCHAR(20) NOT NULL
        REFERENCES products (product_id) ON DELETE RESTRICT,
    quantity     INTEGER     NOT NULL
        CONSTRAINT ck_order_items_quantity_positive CHECK (quantity > 0),
    unit_price   NUMERIC(10, 2) NOT NULL
        CONSTRAINT ck_order_items_unit_price_non_negative CHECK (unit_price >= 0),
    discount_pct NUMERIC(5, 2)  NOT NULL DEFAULT 0
        CONSTRAINT ck_order_items_discount_range CHECK (discount_pct >= 0 AND discount_pct <= 100),

    -- Coluna calculada e persistida — fonte única de verdade para o preço final
    -- Evita divergência entre cálculo na app e valor armazenado
    total_price  NUMERIC(10, 2) NOT NULL
        GENERATED ALWAYS AS (
            ROUND(unit_price * quantity * (1 - discount_pct / 100.0), 2)
        ) STORED
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id
    ON order_items (order_id);

CREATE INDEX IF NOT EXISTS idx_order_items_product_id
    ON order_items (product_id);

-- =============================================================================
-- FIM DO SCHEMA
-- Para popular o banco, execute o script ETL:
--   python -m etl.load_orders /app/data/orders.csv
-- =============================================================================
