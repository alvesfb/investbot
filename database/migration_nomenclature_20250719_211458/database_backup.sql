--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13
-- Dumped by pg_dump version 15.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: analytics; Type: SCHEMA; Schema: -; Owner: investment_user
--

CREATE SCHEMA analytics;


ALTER SCHEMA analytics OWNER TO investment_user;

--
-- Name: audit; Type: SCHEMA; Schema: -; Owner: investment_user
--

CREATE SCHEMA audit;


ALTER SCHEMA audit OWNER TO investment_user;

--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: data_quality_enum; Type: TYPE; Schema: public; Owner: investment_user
--

CREATE TYPE public.data_quality_enum AS ENUM (
    'excellent',
    'good',
    'medium',
    'poor',
    'critical'
);


ALTER TYPE public.data_quality_enum OWNER TO investment_user;

--
-- Name: dataqualityenum; Type: TYPE; Schema: public; Owner: investment_user
--

CREATE TYPE public.dataqualityenum AS ENUM (
    'EXCELLENT',
    'GOOD',
    'MEDIUM',
    'POOR',
    'CRITICAL'
);


ALTER TYPE public.dataqualityenum OWNER TO investment_user;

--
-- Name: recommendation_enum; Type: TYPE; Schema: public; Owner: investment_user
--

CREATE TYPE public.recommendation_enum AS ENUM (
    'strong_buy',
    'buy',
    'hold',
    'sell',
    'strong_sell'
);


ALTER TYPE public.recommendation_enum OWNER TO investment_user;

--
-- Name: recommendationenum; Type: TYPE; Schema: public; Owner: investment_user
--

CREATE TYPE public.recommendationenum AS ENUM (
    'STRONG_BUY',
    'BUY',
    'HOLD',
    'SELL',
    'STRONG_SELL'
);


ALTER TYPE public.recommendationenum OWNER TO investment_user;

--
-- Name: stock_status_enum; Type: TYPE; Schema: public; Owner: investment_user
--

CREATE TYPE public.stock_status_enum AS ENUM (
    'active',
    'suspended',
    'delisted',
    'under_review'
);


ALTER TYPE public.stock_status_enum OWNER TO investment_user;

--
-- Name: stockstatusenum; Type: TYPE; Schema: public; Owner: investment_user
--

CREATE TYPE public.stockstatusenum AS ENUM (
    'ACTIVE',
    'SUSPENDED',
    'DELISTED',
    'UNDER_REVIEW'
);


ALTER TYPE public.stockstatusenum OWNER TO investment_user;

--
-- Name: audit_trigger_function(); Type: FUNCTION; Schema: public; Owner: investment_user
--

CREATE FUNCTION public.audit_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.audit_trigger_function() OWNER TO investment_user;

--
-- Name: calculate_percentile_rank(numeric, text, text, text); Type: FUNCTION; Schema: public; Owner: investment_user
--

CREATE FUNCTION public.calculate_percentile_rank(score numeric, table_name text, score_column text, filter_condition text DEFAULT ''::text) RETURNS numeric
    LANGUAGE plpgsql
    AS $_$
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
$_$;


ALTER FUNCTION public.calculate_percentile_rank(score numeric, table_name text, score_column text, filter_condition text) OWNER TO investment_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agent_sessions; Type: TABLE; Schema: public; Owner: investment_user
--

CREATE TABLE public.agent_sessions (
    id uuid NOT NULL,
    session_id character varying(100) NOT NULL,
    agent_name character varying(100) NOT NULL,
    agent_version character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    input_data jsonb,
    output_data jsonb,
    error_message text,
    execution_time_seconds numeric(8,2),
    stocks_processed integer,
    memory_usage_mb numeric(8,2),
    config_snapshot jsonb,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.agent_sessions OWNER TO investment_user;

--
-- Name: fundamental_analyses; Type: TABLE; Schema: public; Owner: investment_user
--

CREATE TABLE public.fundamental_analyses (
    id uuid NOT NULL,
    stock_id uuid NOT NULL,
    analysis_date timestamp with time zone DEFAULT now() NOT NULL,
    valuation_score numeric(5,2) NOT NULL,
    profitability_score numeric(5,2) NOT NULL,
    growth_score numeric(5,2) NOT NULL,
    financial_health_score numeric(5,2) NOT NULL,
    dividend_score numeric(5,2),
    management_score numeric(5,2),
    composite_score numeric(5,2) NOT NULL,
    sector_rank integer,
    sector_percentile numeric(5,2),
    market_rank integer,
    analysis_method character varying(50),
    data_sources jsonb,
    calculation_details jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.fundamental_analyses OWNER TO investment_user;

--
-- Name: market_data; Type: TABLE; Schema: public; Owner: investment_user
--

CREATE TABLE public.market_data (
    id uuid NOT NULL,
    stock_id uuid NOT NULL,
    date timestamp with time zone NOT NULL,
    open_price numeric(12,2) NOT NULL,
    high_price numeric(12,2) NOT NULL,
    low_price numeric(12,2) NOT NULL,
    close_price numeric(12,2) NOT NULL,
    adjusted_close numeric(12,2) NOT NULL,
    volume bigint NOT NULL,
    dividend_amount numeric(8,4),
    split_ratio numeric(8,4),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.market_data OWNER TO investment_user;

--
-- Name: recommendations; Type: TABLE; Schema: public; Owner: investment_user
--

CREATE TABLE public.recommendations (
    id uuid NOT NULL,
    stock_id uuid NOT NULL,
    analysis_date timestamp with time zone DEFAULT now() NOT NULL,
    recommendation_type public.recommendationenum NOT NULL,
    fundamental_score numeric(5,2) NOT NULL,
    technical_score numeric(5,2),
    macro_score numeric(5,2),
    composite_score numeric(5,2) NOT NULL,
    target_price numeric(12,2),
    entry_price numeric(12,2),
    stop_loss numeric(12,2),
    upside_potential numeric(5,2),
    rationale text NOT NULL,
    risk_factors text,
    catalysts text,
    time_horizon_days smallint,
    is_active boolean NOT NULL,
    confidence_level numeric(4,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    reviewed_at timestamp with time zone,
    agent_version character varying(20),
    analysis_context jsonb
);


ALTER TABLE public.recommendations OWNER TO investment_user;

--
-- Name: stocks; Type: TABLE; Schema: public; Owner: investment_user
--

CREATE TABLE public.stocks (
    id uuid NOT NULL,
    symbol character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    long_name character varying(500),
    sector character varying(100) NOT NULL,
    industry character varying(100),
    sub_industry character varying(100),
    segment character varying(100),
    tax_id character varying(20),
    website character varying(300),
    description text,
    ceo character varying(150),
    employees integer,
    founded_year smallint,
    headquarters_city character varying(100),
    headquarters_state character varying(50),
    status public.stockstatusenum NOT NULL,
    listing_segment character varying(50),
    share_type character varying(10),
    current_price numeric(12,2) NOT NULL,
    previous_close numeric(12,2),
    day_high numeric(12,2),
    day_low numeric(12,2),
    fifty_two_week_high numeric(12,2),
    fifty_two_week_low numeric(12,2),
    average_volume_30d bigint,
    current_volume bigint,
    market_cap bigint,
    enterprise_value bigint,
    shares_outstanding bigint,
    free_float_percent numeric(5,2),
    pe_ratio numeric(8,2),
    pb_ratio numeric(8,2),
    ps_ratio numeric(8,2),
    ev_ebitda numeric(8,2),
    ev_revenue numeric(8,2),
    peg_ratio numeric(8,2),
    roe numeric(5,2),
    roa numeric(5,2),
    roic numeric(5,2),
    gross_margin numeric(5,2),
    operating_margin numeric(5,2),
    net_margin numeric(5,2),
    ebitda_margin numeric(5,2),
    debt_to_equity numeric(8,2),
    debt_to_ebitda numeric(8,2),
    current_ratio numeric(5,2),
    quick_ratio numeric(5,2),
    interest_coverage numeric(8,2),
    asset_turnover numeric(5,2),
    inventory_turnover numeric(5,2),
    receivables_turnover numeric(5,2),
    revenue_ttm bigint,
    revenue_annual bigint,
    gross_profit_ttm bigint,
    operating_income_ttm bigint,
    net_income_ttm bigint,
    ebitda_ttm bigint,
    total_assets bigint,
    total_equity bigint,
    total_debt bigint,
    net_debt bigint,
    cash_and_equivalents bigint,
    working_capital bigint,
    revenue_growth_yoy numeric(5,2),
    revenue_growth_3y numeric(5,2),
    earnings_growth_yoy numeric(5,2),
    earnings_growth_3y numeric(5,2),
    book_value_growth_3y numeric(5,2),
    fundamental_score numeric(5,2),
    valuation_score numeric(5,2),
    profitability_score numeric(5,2),
    growth_score numeric(5,2),
    financial_health_score numeric(5,2),
    overall_rank integer,
    sector_rank integer,
    market_cap_rank integer,
    data_quality public.dataqualityenum NOT NULL,
    data_completeness numeric(4,2),
    confidence_level numeric(4,2),
    last_analysis_date timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now(),
    last_price_update timestamp with time zone,
    last_fundamentals_update timestamp with time zone,
    yfinance_raw_data jsonb,
    additional_metrics jsonb,
    analyst_estimates jsonb,
    esg_scores jsonb,
    CONSTRAINT check_data_completeness_range CHECK (((data_completeness >= (0)::numeric) AND (data_completeness <= (100)::numeric))),
    CONSTRAINT check_fundamental_score_range CHECK (((fundamental_score >= (0)::numeric) AND (fundamental_score <= (100)::numeric))),
    CONSTRAINT check_non_negative_market_cap CHECK ((market_cap >= 0)),
    CONSTRAINT check_positive_price CHECK ((current_price > (0)::numeric))
);


ALTER TABLE public.stocks OWNER TO investment_user;

--
-- Data for Name: agent_sessions; Type: TABLE DATA; Schema: public; Owner: investment_user
--

COPY public.agent_sessions (id, session_id, agent_name, agent_version, status, input_data, output_data, error_message, execution_time_seconds, stocks_processed, memory_usage_mb, config_snapshot, started_at, finished_at, created_at) FROM stdin;
\.


--
-- Data for Name: fundamental_analyses; Type: TABLE DATA; Schema: public; Owner: investment_user
--

COPY public.fundamental_analyses (id, stock_id, analysis_date, valuation_score, profitability_score, growth_score, financial_health_score, dividend_score, management_score, composite_score, sector_rank, sector_percentile, market_rank, analysis_method, data_sources, calculation_details, created_at) FROM stdin;
\.


--
-- Data for Name: market_data; Type: TABLE DATA; Schema: public; Owner: investment_user
--

COPY public.market_data (id, stock_id, date, open_price, high_price, low_price, close_price, adjusted_close, volume, dividend_amount, split_ratio, created_at) FROM stdin;
\.


--
-- Data for Name: recommendations; Type: TABLE DATA; Schema: public; Owner: investment_user
--

COPY public.recommendations (id, stock_id, analysis_date, recommendation_type, fundamental_score, technical_score, macro_score, composite_score, target_price, entry_price, stop_loss, upside_potential, rationale, risk_factors, catalysts, time_horizon_days, is_active, confidence_level, created_at, expires_at, reviewed_at, agent_version, analysis_context) FROM stdin;
\.


--
-- Data for Name: stocks; Type: TABLE DATA; Schema: public; Owner: investment_user
--

COPY public.stocks (id, symbol, name, long_name, sector, industry, sub_industry, segment, tax_id, website, description, ceo, employees, founded_year, headquarters_city, headquarters_state, status, listing_segment, share_type, current_price, previous_close, day_high, day_low, fifty_two_week_high, fifty_two_week_low, average_volume_30d, current_volume, market_cap, enterprise_value, shares_outstanding, free_float_percent, pe_ratio, pb_ratio, ps_ratio, ev_ebitda, ev_revenue, peg_ratio, roe, roa, roic, gross_margin, operating_margin, net_margin, ebitda_margin, debt_to_equity, debt_to_ebitda, current_ratio, quick_ratio, interest_coverage, asset_turnover, inventory_turnover, receivables_turnover, revenue_ttm, revenue_annual, gross_profit_ttm, operating_income_ttm, net_income_ttm, ebitda_ttm, total_assets, total_equity, total_debt, net_debt, cash_and_equivalents, working_capital, revenue_growth_yoy, revenue_growth_3y, earnings_growth_yoy, earnings_growth_3y, book_value_growth_3y, fundamental_score, valuation_score, profitability_score, growth_score, financial_health_score, overall_rank, sector_rank, market_cap_rank, data_quality, data_completeness, confidence_level, last_analysis_date, created_at, updated_at, last_price_update, last_fundamentals_update, yfinance_raw_data, additional_metrics, analyst_estimates, esg_scores) FROM stdin;
\.


--
-- Name: agent_sessions agent_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.agent_sessions
    ADD CONSTRAINT agent_sessions_pkey PRIMARY KEY (id);


--
-- Name: fundamental_analyses fundamental_analyses_pkey; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.fundamental_analyses
    ADD CONSTRAINT fundamental_analyses_pkey PRIMARY KEY (id);


--
-- Name: market_data market_data_pkey; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.market_data
    ADD CONSTRAINT market_data_pkey PRIMARY KEY (id);


--
-- Name: recommendations recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.recommendations
    ADD CONSTRAINT recommendations_pkey PRIMARY KEY (id);


--
-- Name: stocks stocks_pkey; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_pkey PRIMARY KEY (id);


--
-- Name: stocks stocks_tax_id_key; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_tax_id_key UNIQUE (tax_id);


--
-- Name: market_data unique_stock_date; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.market_data
    ADD CONSTRAINT unique_stock_date UNIQUE (stock_id, date);


--
-- Name: stocks unique_symbol; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT unique_symbol UNIQUE (symbol);


--
-- Name: idx_market_data_stock_date; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_market_data_stock_date ON public.market_data USING btree (stock_id, date);


--
-- Name: idx_recommendation_active; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_recommendation_active ON public.recommendations USING btree (is_active, analysis_date);


--
-- Name: idx_recommendation_stock_date; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_recommendation_stock_date ON public.recommendations USING btree (stock_id, analysis_date);


--
-- Name: idx_recommendation_type_score; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_recommendation_type_score ON public.recommendations USING btree (recommendation_type, composite_score);


--
-- Name: idx_stock_market_cap_score; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_market_cap_score ON public.stocks USING btree (market_cap, fundamental_score);


--
-- Name: idx_stock_name_gin; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_name_gin ON public.stocks USING gin (name public.gin_trgm_ops);


--
-- Name: idx_stock_pe_pb; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_pe_pb ON public.stocks USING btree (pe_ratio, pb_ratio);


--
-- Name: idx_stock_quality; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_quality ON public.stocks USING btree (data_quality, data_completeness);


--
-- Name: idx_stock_roe_roic; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_roe_roic ON public.stocks USING btree (roe, roic);


--
-- Name: idx_stock_sector_rank; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_sector_rank ON public.stocks USING btree (sector, sector_rank);


--
-- Name: idx_stock_sector_status; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_sector_status ON public.stocks USING btree (sector, status);


--
-- Name: idx_stock_updated; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_updated ON public.stocks USING btree (updated_at);


--
-- Name: ix_agent_sessions_agent_name; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_agent_sessions_agent_name ON public.agent_sessions USING btree (agent_name);


--
-- Name: ix_agent_sessions_id; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_agent_sessions_id ON public.agent_sessions USING btree (id);


--
-- Name: ix_agent_sessions_session_id; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE UNIQUE INDEX ix_agent_sessions_session_id ON public.agent_sessions USING btree (session_id);


--
-- Name: ix_agent_sessions_status; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_agent_sessions_status ON public.agent_sessions USING btree (status);


--
-- Name: ix_fundamental_analyses_analysis_date; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_fundamental_analyses_analysis_date ON public.fundamental_analyses USING btree (analysis_date);


--
-- Name: ix_fundamental_analyses_composite_score; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_fundamental_analyses_composite_score ON public.fundamental_analyses USING btree (composite_score);


--
-- Name: ix_fundamental_analyses_id; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_fundamental_analyses_id ON public.fundamental_analyses USING btree (id);


--
-- Name: ix_fundamental_analyses_stock_id; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_fundamental_analyses_stock_id ON public.fundamental_analyses USING btree (stock_id);


--
-- Name: ix_market_data_date; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_market_data_date ON public.market_data USING btree (date);


--
-- Name: ix_market_data_id; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_market_data_id ON public.market_data USING btree (id);


--
-- Name: ix_market_data_stock_id; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_market_data_stock_id ON public.market_data USING btree (stock_id);


--
-- Name: ix_recommendations_analysis_date; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_recommendations_analysis_date ON public.recommendations USING btree (analysis_date);


--
-- Name: ix_recommendations_composite_score; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_recommendations_composite_score ON public.recommendations USING btree (composite_score);


--
-- Name: ix_recommendations_id; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_recommendations_id ON public.recommendations USING btree (id);


--
-- Name: ix_recommendations_is_active; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_recommendations_is_active ON public.recommendations USING btree (is_active);


--
-- Name: ix_recommendations_recommendation_type; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_recommendations_recommendation_type ON public.recommendations USING btree (recommendation_type);


--
-- Name: ix_recommendations_stock_id; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_recommendations_stock_id ON public.recommendations USING btree (stock_id);


--
-- Name: ix_stocks_debt_to_equity; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_debt_to_equity ON public.stocks USING btree (debt_to_equity);


--
-- Name: ix_stocks_fundamental_score; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_fundamental_score ON public.stocks USING btree (fundamental_score);


--
-- Name: ix_stocks_id; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_id ON public.stocks USING btree (id);


--
-- Name: ix_stocks_market_cap; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_market_cap ON public.stocks USING btree (market_cap);


--
-- Name: ix_stocks_name; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_name ON public.stocks USING btree (name);


--
-- Name: ix_stocks_overall_rank; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_overall_rank ON public.stocks USING btree (overall_rank);


--
-- Name: ix_stocks_pb_ratio; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_pb_ratio ON public.stocks USING btree (pb_ratio);


--
-- Name: ix_stocks_pe_ratio; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_pe_ratio ON public.stocks USING btree (pe_ratio);


--
-- Name: ix_stocks_roe; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_roe ON public.stocks USING btree (roe);


--
-- Name: ix_stocks_roic; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_roic ON public.stocks USING btree (roic);


--
-- Name: ix_stocks_sector; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_sector ON public.stocks USING btree (sector);


--
-- Name: ix_stocks_sector_rank; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_sector_rank ON public.stocks USING btree (sector_rank);


--
-- Name: ix_stocks_status; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_status ON public.stocks USING btree (status);


--
-- Name: ix_stocks_symbol; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE UNIQUE INDEX ix_stocks_symbol ON public.stocks USING btree (symbol);


--
-- Name: fundamental_analyses fundamental_analyses_stock_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.fundamental_analyses
    ADD CONSTRAINT fundamental_analyses_stock_id_fkey FOREIGN KEY (stock_id) REFERENCES public.stocks(id);


--
-- Name: market_data market_data_stock_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.market_data
    ADD CONSTRAINT market_data_stock_id_fkey FOREIGN KEY (stock_id) REFERENCES public.stocks(id);


--
-- Name: recommendations recommendations_stock_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.recommendations
    ADD CONSTRAINT recommendations_stock_id_fkey FOREIGN KEY (stock_id) REFERENCES public.stocks(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO investment_user;


--
-- PostgreSQL database dump complete
--

