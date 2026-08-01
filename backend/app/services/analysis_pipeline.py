"""
The core pipeline. THIS is the function that proves the app is real:
every process - whether seeded on day one or typed live by a judge as
Process 101 - flows through this exact same code path.

Input -> Research/Evidence -> AI Analysis -> Validation -> Storage
"""
from sqlalchemy.orm import Session
from app import models
from app.services.research import gather_evidence, evidence_to_text
from app.services.llm_provider import analyze_process_with_llm


def analyze_process(db: Session, process: models.Process) -> models.Process:
    """
    Analyzes a single process and persists the result.
    Safe to call on ANY process row, regardless of when/how it was created.
    """
    # 1. Research grounding
    evidence = gather_evidence(process.name, process.category)
    evidence_text = evidence_to_text(evidence)

    # 2. AI analysis (same function for all 100 seed processes AND any new one)
    result = analyze_process_with_llm(
        name=process.name,
        description=process.description or "",
        category=process.category,
        evidence_text=evidence_text,
    )

    # 3. Persist structured analysis
    analysis = db.query(models.ProcessAnalysis).filter_by(process_id=process.id).first()
    if not analysis:
        analysis = models.ProcessAnalysis(process_id=process.id)
        db.add(analysis)

    analysis.business_purpose = result["business_purpose"]
    analysis.key_activities = result["key_activities"]
    analysis.current_challenges = result["current_challenges"]
    analysis.ai_opportunity = result["ai_opportunity"]
    analysis.automation_potential = result["automation_potential"]
    analysis.human_involvement = result["human_involvement"]
    analysis.technologies = result["technologies"]
    analysis.business_benefit = result["business_benefit"]
    analysis.risks = result["risks"]
    analysis.rationale = result["rationale"]
    analysis.confidence = result["confidence"]

    # 4. Persist evidence (traceability)
    db.query(models.Evidence).filter_by(process_id=process.id).delete()
    for e in evidence:
        db.add(models.Evidence(
            process_id=process.id,
            source_title=e.get("title", ""),
            source_url=e.get("url", ""),
            snippet=e.get("snippet", ""),
        ))

    process.status = "analyzed"
    db.commit()
    db.refresh(process)
    return process
