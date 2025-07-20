-- Investment System PostgreSQL Initialization
-- Extensions and Basic Setup

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas if needed
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set default permissions
GRANT USAGE ON SCHEMA public TO investment_user;
GRANT CREATE ON SCHEMA public TO investment_user;

-- Create custom types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'data_quality_enum') THEN
        CREATE TYPE data_quality_enum AS ENUM ('excellent', 'good', 'medium', 'poor', 'critical');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'stock_status_enum') THEN
        CREATE TYPE stock_status_enum AS ENUM ('active', 'suspended', 'delisted', 'under_review');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recommendation_enum') THEN
        CREATE TYPE recommendation_enum AS ENUM ('strong_buy', 'buy', 'hold', 'sell', 'strong_sell');
    END IF;
END$$;

-- Configure settings for investment system
ALTER DATABASE investment_system SET timezone TO 'UTC';
ALTER DATABASE investment_system SET lc_monetary TO 'pt_BR.UTF-8';
ALTER DATABASE investment_system SET default_text_search_config TO 'portuguese';

-- Create audit function for tracking changes
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.created_at = COALESCE(NEW.created_at, NOW());
        NEW.updated_at = NOW();
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at = NOW();
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create helper functions
CREATE OR REPLACE FUNCTION calculate_percentile_rank(
    score NUMERIC,
    table_name TEXT,
    score_column TEXT,
    filter_condition TEXT DEFAULT ''
)
RETURNS NUMERIC AS $$
DECLARE
    rank_result NUMERIC;
    query_text TEXT;
BEGIN
    query_text := format(
        'SELECT percent_rank() OVER (ORDER BY %I) FROM %I WHERE %I = $1',
        score_column, table_name, score_column
    );
    
    IF filter_condition != '' THEN
        query_text := query_text || ' AND ' || filter_condition;
    END IF;
    
    EXECUTE query_text USING score INTO rank_result;
    RETURN COALESCE(rank_result * 100, 0);
END;
$$ LANGUAGE plpgsql;

-- Log initialization
INSERT INTO pg_stat_statements_reset();
SELECT 'PostgreSQL initialization completed for Investment System' as status;
