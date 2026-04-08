from __future__ import annotations


def compute_final_risk(eye_score: float, speech_score: float, mcq_score: float) -> dict:
    """Combine module scores into a final screening result.

    Scores are expected on a 0-100 scale where higher means lower concern in
    this starter version. Final score is mapped to a risk level.
    """

    final_score = round((eye_score * 0.40) + (speech_score * 0.30) + (mcq_score * 0.30), 2)

    if final_score >= 75:
        risk_level = "low"
        recommendation = "Continue routine developmental observation and re-screen if concerns persist."
    elif final_score >= 50:
        risk_level = "moderate"
        recommendation = "Consider a clinician-reviewed follow-up screening and closer observation."
    else:
        risk_level = "high"
        recommendation = "Recommend prompt professional follow-up for a detailed assessment."

    return {
        "final_score": final_score,
        "risk_level": risk_level,
        "recommendation": recommendation,
    }
