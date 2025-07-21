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
-- Name: public; Type: SCHEMA; Schema: -; Owner: investment_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO investment_user;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: investment_user
--

COMMENT ON SCHEMA public IS '';


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: dataqualityenum; Type: TYPE; Schema: public; Owner: investment_user
--

CREATE TYPE public.dataqualityenum AS ENUM (
    'excellent',
    'good',
    'medium',
    'poor',
    'critical'
);


ALTER TYPE public.dataqualityenum OWNER TO investment_user;

--
-- Name: recommendationenum; Type: TYPE; Schema: public; Owner: investment_user
--

CREATE TYPE public.recommendationenum AS ENUM (
    'strong_buy',
    'buy',
    'hold',
    'sell',
    'strong_sell'
);


ALTER TYPE public.recommendationenum OWNER TO investment_user;

--
-- Name: stockstatusenum; Type: TYPE; Schema: public; Owner: investment_user
--

CREATE TYPE public.stockstatusenum AS ENUM (
    'active',
    'suspended',
    'delisted',
    'under_review'
);


ALTER TYPE public.stockstatusenum OWNER TO investment_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agent_sessions; Type: TABLE; Schema: public; Owner: investment_user
--

CREATE TABLE public.agent_sessions (
    id uuid NOT NULL,
    agent_name character varying(100) NOT NULL,
    session_type character varying(50) NOT NULL,
    parameters jsonb,
    results jsonb,
    performance_metrics jsonb,
    status character varying(20) NOT NULL,
    error_message text,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone
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
    composite_score numeric(5,2) NOT NULL,
    sector_rank integer,
    sector_percentile numeric(5,2),
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
    open_price numeric(10,2) NOT NULL,
    high_price numeric(10,2) NOT NULL,
    low_price numeric(10,2) NOT NULL,
    close_price numeric(10,2) NOT NULL,
    volume bigint NOT NULL,
    adj_close numeric(10,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.market_data OWNER TO investment_user;

--
-- Name: recommendations; Type: TABLE; Schema: public; Owner: investment_user
--

CREATE TABLE public.recommendations (
    id uuid NOT NULL,
    stock_id uuid NOT NULL,
    recommendation_type public.recommendationenum NOT NULL,
    confidence_level numeric(5,2) NOT NULL,
    entry_price numeric(10,2) NOT NULL,
    target_price numeric(10,2),
    stop_loss numeric(10,2),
    rationale text NOT NULL,
    analysis_date timestamp with time zone DEFAULT now() NOT NULL,
    agent_version character varying(20),
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT check_confidence_range CHECK (((confidence_level >= (0)::numeric) AND (confidence_level <= (100)::numeric)))
);


ALTER TABLE public.recommendations OWNER TO investment_user;

--
-- Name: stocks; Type: TABLE; Schema: public; Owner: investment_user
--

CREATE TABLE public.stocks (
    id uuid NOT NULL,
    codigo character varying(10) NOT NULL,
    nome character varying(200) NOT NULL,
    nome_completo character varying(500),
    setor character varying(100) NOT NULL,
    subsetor character varying(100),
    segmento character varying(100),
    industria character varying(100),
    cnpj character varying(20),
    website character varying(300),
    descricao text,
    ceo character varying(150),
    funcionarios integer,
    ano_fundacao smallint,
    sede_cidade character varying(100),
    sede_estado character varying(50),
    status public.stockstatusenum NOT NULL,
    listagem_b3 character varying(50),
    listagem_data timestamp with time zone,
    free_float numeric(5,2),
    current_price numeric(10,2) NOT NULL,
    previous_close numeric(10,2),
    day_high numeric(10,2),
    day_low numeric(10,2),
    week_52_high numeric(10,2),
    week_52_low numeric(10,2),
    volume_medio bigint,
    volume_dia bigint,
    market_cap bigint,
    shares_outstanding bigint,
    pe_ratio numeric(8,2),
    pb_ratio numeric(8,2),
    price_to_sales numeric(8,2),
    ev_to_ebitda numeric(8,2),
    peg_ratio numeric(8,2),
    roe numeric(5,2),
    roa numeric(5,2),
    roic numeric(5,2),
    net_margin numeric(5,2),
    gross_margin numeric(5,2),
    operating_margin numeric(5,2),
    ebitda_margin numeric(5,2),
    debt_to_equity numeric(8,2),
    debt_to_ebitda numeric(8,2),
    current_ratio numeric(8,2),
    quick_ratio numeric(8,2),
    revenue_growth_3y numeric(5,2),
    earnings_growth_3y numeric(5,2),
    dividend_yield numeric(5,2),
    beta_5y numeric(8,4),
    correlation_ibov numeric(5,4),
    volatility_annual numeric(5,2),
    rsi_14 numeric(5,2),
    intrinsic_value_dcf numeric(10,2),
    intrinsic_value_multiples numeric(10,2),
    fair_value_estimate numeric(10,2),
    fundamental_score numeric(5,2),
    technical_score numeric(5,2),
    macro_score numeric(5,2),
    composite_score numeric(5,2),
    overall_rank integer,
    sector_rank integer,
    data_quality public.dataqualityenum NOT NULL,
    data_completeness numeric(5,2),
    confidence_level numeric(5,2),
    financial_data jsonb,
    analyst_estimates jsonb,
    technical_indicators jsonb,
    news_sentiment jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now(),
    last_price_update timestamp with time zone,
    last_fundamentals_update timestamp with time zone,
    last_analysis_date timestamp with time zone,
    CONSTRAINT check_confidence_range CHECK (((confidence_level >= (0)::numeric) AND (confidence_level <= (100)::numeric))),
    CONSTRAINT check_data_completeness_range CHECK (((data_completeness >= (0)::numeric) AND (data_completeness <= (100)::numeric))),
    CONSTRAINT check_fundamental_score_range CHECK (((fundamental_score >= (0)::numeric) AND (fundamental_score <= (100)::numeric))),
    CONSTRAINT check_non_negative_market_cap CHECK ((market_cap >= 0)),
    CONSTRAINT check_positive_price CHECK ((current_price > (0)::numeric))
);


ALTER TABLE public.stocks OWNER TO investment_user;

--
-- Data for Name: agent_sessions; Type: TABLE DATA; Schema: public; Owner: investment_user
--

COPY public.agent_sessions (id, agent_name, session_type, parameters, results, performance_metrics, status, error_message, started_at, finished_at) FROM stdin;
\.


--
-- Data for Name: fundamental_analyses; Type: TABLE DATA; Schema: public; Owner: investment_user
--

COPY public.fundamental_analyses (id, stock_id, analysis_date, valuation_score, profitability_score, growth_score, financial_health_score, dividend_score, composite_score, sector_rank, sector_percentile, analysis_method, data_sources, calculation_details, created_at) FROM stdin;
\.


--
-- Data for Name: market_data; Type: TABLE DATA; Schema: public; Owner: investment_user
--

COPY public.market_data (id, stock_id, date, open_price, high_price, low_price, close_price, volume, adj_close, created_at) FROM stdin;
\.


--
-- Data for Name: recommendations; Type: TABLE DATA; Schema: public; Owner: investment_user
--

COPY public.recommendations (id, stock_id, recommendation_type, confidence_level, entry_price, target_price, stop_loss, rationale, analysis_date, agent_version, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: stocks; Type: TABLE DATA; Schema: public; Owner: investment_user
--

COPY public.stocks (id, codigo, nome, nome_completo, setor, subsetor, segmento, industria, cnpj, website, descricao, ceo, funcionarios, ano_fundacao, sede_cidade, sede_estado, status, listagem_b3, listagem_data, free_float, current_price, previous_close, day_high, day_low, week_52_high, week_52_low, volume_medio, volume_dia, market_cap, shares_outstanding, pe_ratio, pb_ratio, price_to_sales, ev_to_ebitda, peg_ratio, roe, roa, roic, net_margin, gross_margin, operating_margin, ebitda_margin, debt_to_equity, debt_to_ebitda, current_ratio, quick_ratio, revenue_growth_3y, earnings_growth_3y, dividend_yield, beta_5y, correlation_ibov, volatility_annual, rsi_14, intrinsic_value_dcf, intrinsic_value_multiples, fair_value_estimate, fundamental_score, technical_score, macro_score, composite_score, overall_rank, sector_rank, data_quality, data_completeness, confidence_level, financial_data, analyst_estimates, technical_indicators, news_sentiment, created_at, updated_at, last_price_update, last_fundamentals_update, last_analysis_date) FROM stdin;
433b8dfb-48a4-48fb-89fd-34775ce14716	SQL1	Teste SQL	\N	Tech	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	active	\N	\N	\N	100.00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	good	\N	\N	\N	\N	\N	\N	2025-07-20 18:35:18.958485+00	2025-07-20 18:35:18.958485+00	\N	\N	\N
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
-- Name: stocks stocks_cnpj_key; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_cnpj_key UNIQUE (cnpj);


--
-- Name: stocks stocks_pkey; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_pkey PRIMARY KEY (id);


--
-- Name: stocks unique_codigo; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT unique_codigo UNIQUE (codigo);


--
-- Name: market_data unique_stock_date; Type: CONSTRAINT; Schema: public; Owner: investment_user
--

ALTER TABLE ONLY public.market_data
    ADD CONSTRAINT unique_stock_date UNIQUE (stock_id, date);


--
-- Name: idx_agent_session_name_started; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_agent_session_name_started ON public.agent_sessions USING btree (agent_name, started_at);


--
-- Name: idx_agent_session_status; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_agent_session_status ON public.agent_sessions USING btree (status);


--
-- Name: idx_fundamental_score; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_fundamental_score ON public.fundamental_analyses USING btree (composite_score);


--
-- Name: idx_fundamental_stock_date; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_fundamental_stock_date ON public.fundamental_analyses USING btree (stock_id, analysis_date);


--
-- Name: idx_market_data_stock_date; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_market_data_stock_date ON public.market_data USING btree (stock_id, date);


--
-- Name: idx_recommendation_active; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_recommendation_active ON public.recommendations USING btree (is_active, recommendation_type);


--
-- Name: idx_recommendation_stock_date; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_recommendation_stock_date ON public.recommendations USING btree (stock_id, analysis_date);


--
-- Name: idx_stock_nome_trgm; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_nome_trgm ON public.stocks USING gin (nome public.gin_trgm_ops);


--
-- Name: idx_stock_price_update; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_price_update ON public.stocks USING btree (codigo, last_price_update);


--
-- Name: idx_stock_quality; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_quality ON public.stocks USING btree (data_quality, data_completeness);


--
-- Name: idx_stock_setor_score; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_setor_score ON public.stocks USING btree (setor, composite_score);


--
-- Name: idx_stock_status_updated; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX idx_stock_status_updated ON public.stocks USING btree (status, updated_at);


--
-- Name: ix_agent_sessions_agent_name; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_agent_sessions_agent_name ON public.agent_sessions USING btree (agent_name);


--
-- Name: ix_agent_sessions_id; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_agent_sessions_id ON public.agent_sessions USING btree (id);


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
-- Name: ix_stocks_codigo; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE UNIQUE INDEX ix_stocks_codigo ON public.stocks USING btree (codigo);


--
-- Name: ix_stocks_composite_score; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_composite_score ON public.stocks USING btree (composite_score);


--
-- Name: ix_stocks_current_price; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_current_price ON public.stocks USING btree (current_price);


--
-- Name: ix_stocks_data_quality; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_data_quality ON public.stocks USING btree (data_quality);


--
-- Name: ix_stocks_fundamental_score; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_fundamental_score ON public.stocks USING btree (fundamental_score);


--
-- Name: ix_stocks_id; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_id ON public.stocks USING btree (id);


--
-- Name: ix_stocks_last_analysis_date; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_last_analysis_date ON public.stocks USING btree (last_analysis_date);


--
-- Name: ix_stocks_last_price_update; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_last_price_update ON public.stocks USING btree (last_price_update);


--
-- Name: ix_stocks_market_cap; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_market_cap ON public.stocks USING btree (market_cap);


--
-- Name: ix_stocks_nome; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_nome ON public.stocks USING btree (nome);


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
-- Name: ix_stocks_sector_rank; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_sector_rank ON public.stocks USING btree (sector_rank);


--
-- Name: ix_stocks_setor; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_setor ON public.stocks USING btree (setor);


--
-- Name: ix_stocks_status; Type: INDEX; Schema: public; Owner: investment_user
--

CREATE INDEX ix_stocks_status ON public.stocks USING btree (status);


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
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: investment_user
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

