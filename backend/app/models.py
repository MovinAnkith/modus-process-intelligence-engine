from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    industry = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    processes = relationship("Process", back_populates="organization", cascade="all, delete")


class Process(Base):
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    description = Column(Text)
    status = Column(Text, default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    organization = relationship("Organization", back_populates="processes")
    analysis = relationship("ProcessAnalysis", back_populates="process", uselist=False, cascade="all, delete")
    evidence = relationship("Evidence", back_populates="process", cascade="all, delete")


class ProcessAnalysis(Base):
    __tablename__ = "process_analysis"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("processes.id", ondelete="CASCADE"), unique=True)
    business_purpose = Column(Text)
    key_activities = Column(Text)
    current_challenges = Column(Text)
    ai_opportunity = Column(Text)
    automation_potential = Column(Text)
    human_involvement = Column(Text)
    technologies = Column(Text)
    business_benefit = Column(Text)
    risks = Column(Text)
    rationale = Column(Text)
    confidence = Column(Text, default="grounded")
    created_at = Column(TIMESTAMP, server_default=func.now())

    process = relationship("Process", back_populates="analysis")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("processes.id", ondelete="CASCADE"))
    source_title = Column(Text)
    source_url = Column(Text)
    snippet = Column(Text)
    retrieved_at = Column(TIMESTAMP, server_default=func.now())

    process = relationship("Process", back_populates="evidence")
