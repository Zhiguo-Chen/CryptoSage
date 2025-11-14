from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    TIMESTAMP,
    Text,
    ForeignKey,
    ARRAY,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, nullable=False)
    source = Column(String(50), nullable=False)
    symbol = Column(String(20), nullable=False, default="BTC/USDT")
    open = Column(DECIMAL(18, 8))
    high = Column(DECIMAL(18, 8))
    close = Column(DECIMAL(18, 8))
    low = Column(DECIMAL(18, 8))
    volume = Column(DECIMAL(18, 8))
    created_at = Column(TIMESTAMP, server_default=func.now())


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    published_at = Column(TIMESTAMP, nullable=False)
    source = Column(String(100), nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text)
    url = Column(Text)
    sentiment_score = Column(DECIMAL(5, 4))
    keywords = Column(ARRAY(Text))
    embedding = Column(Vector(1536))
    created_at = Column(TIMESTAMP, server_default=func.now())


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, nullable=False)
    signal_type = Column(String(20), nullable=False)
    confidence = Column(DECIMAL(5, 4), nullable=False)
    price = Column(DECIMAL(18, 8))
    technical_score = Column(DECIMAL(5, 4))
    news_score = Column(DECIMAL(5, 4))
    reasoning = Column(Text)
    agents_consensus = Column(JSONB)
    status = Column(String(20), default="PENDING")
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (CheckConstraint("signal_type IN ('BUY', 'SELL', 'HOLD')"),)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey("signals.id"))
    actual_outcome = Column(String(20))
    profit_loss = Column(DECIMAL(10, 4))
    accuracy_score = Column(DECIMAL(5, 4))
    evaluation_time = Column(TIMESTAMP, nullable=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


class ModelEval(Base):
    __tablename__ = "models_eval"

    id = Column(Integer, primary_key=True)
    agent_name = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    evaluation_period = Column(String(50), nullable=False)
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    accuracy = Column(DECIMAL(5, 4))
    avg_confidence = Column(DECIMAL(5, 4))
    weight = Column(DECIMAL(5, 4), default=0.5)
    last_updated = Column(TIMESTAMP, server_default=func.now())


class AgentDiscussion(Base):
    __tablename__ = "agent_discussions"

    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey("signals.id"))
    round = Column(Integer, nullable=False)
    agent_name = Column(String(100), nullable=False)
    position = Column(String(20))
    argument = Column(Text)
    confidence = Column(DECIMAL(5, 4))
    created_at = Column(TIMESTAMP, server_default=func.now())
