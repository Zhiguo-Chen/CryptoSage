-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Prices table
CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    source VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL DEFAULT 'BTC/USDT',
    open DECIMAL(18, 8),
    high DECIMAL(18, 8),
    low DECIMAL(18, 8),
    close DECIMAL(18, 8),
    volume DECIMAL(18, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp, source, symbol)
);

CREATE INDEX idx_prices_timestamp ON prices(timestamp DESC);

-- News table
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    published_at TIMESTAMP NOT NULL,
    source VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT,
    sentiment_score DECIMAL(5, 4),
    keywords TEXT[],
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_news_published ON news(published_at DESC);
CREATE INDEX idx_news_embedding ON news USING ivfflat (embedding vector_cosine_ops);

-- Signals table
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    signal_type VARCHAR(20) NOT NULL CHECK (signal_type IN ('BUY', 'SELL', 'HOLD')),
    confidence DECIMAL(5, 4) NOT NULL,
    price DECIMAL(18, 8),
    technical_score DECIMAL(5, 4),
    news_score DECIMAL(5, 4),
    reasoning TEXT,
    agents_consensus JSONB,
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signals_timestamp ON signals(timestamp DESC);

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    signal_id INTEGER REFERENCES signals(id),
    actual_outcome VARCHAR(20),
    profit_loss DECIMAL(10, 4),
    accuracy_score DECIMAL(5, 4),
    evaluation_time TIMESTAMP NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Models evaluation table
CREATE TABLE IF NOT EXISTS models_eval (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    evaluation_period VARCHAR(50) NOT NULL,
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy DECIMAL(5, 4),
    avg_confidence DECIMAL(5, 4),
    weight DECIMAL(5, 4) DEFAULT 0.5,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_name, evaluation_period)
);

-- Agent discussions log
CREATE TABLE IF NOT EXISTS agent_discussions (
    id SERIAL PRIMARY KEY,
    signal_id INTEGER REFERENCES signals(id),
    round INTEGER NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    position VARCHAR(20),
    argument TEXT,
    confidence DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
