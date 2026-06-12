"""Report builders for the PyTorch skin model result."""
from typing import Any, Dict, List

from skin_analyzer import build_pytorch_product_recommendations, build_pytorch_routine, clamp_score, score_to_level


def confidence_to_level(confidence: float) -> str:
    """Convert model confidence to a simple qualitative display label."""
    if confidence >= 90:
        return "매우높음"
    if confidence >= 75:
        return "높음"
    if confidence >= 50:
        return "보통"
    if confidence >= 30:
        return "낮음"
    return "매우낮음"


def classify_skin_status(analysis: Dict[str, Any], skin_score: float) -> str:
    """Return a user-facing skin status instead of a numeric score."""
    prediction_route = analysis.get("prediction_route", "unknown")
    if prediction_route == "not_skin":
        return "재촬영 권장"
    if prediction_route == "healthy" and skin_score >= 60:
        return "정상 피부 경향"
    if prediction_route == "acne" or skin_score < 60:
        return "트러블 관리 필요"
    return "관찰 필요"


def build_pytorch_condition_cards(analysis: Dict[str, Any], skin_status: str) -> List[Dict[str, Any]]:
    """Turn PyTorch outputs into user-facing result cards."""
    skin_score = clamp_score(float(analysis.get("skin_score", analysis.get("pytorch_confidence", 0))))
    confidence = clamp_score(float(analysis.get("pytorch_confidence", 0)))
    confidence_level = confidence_to_level(confidence)

    return [
        {
            "key": "skin_status",
            "label": "피부 상태",
            "score": skin_status,
            "level": score_to_level(skin_score),
            "focus_area": "사진 분석 결과",
            "description": "AI가 사진에서 감지한 피부 상태를 사용자가 이해하기 쉬운 말로 정리했습니다.",
        },
        {
            "key": "ai_confidence",
            "label": "AI 판정 신뢰도",
            "score": confidence_level,
            "level": confidence_level,
            "focus_area": "모델 확신도 수준",
            "description": "AI가 현재 판정을 얼마나 강하게 선택했는지 매우낮음, 낮음, 보통, 높음, 매우높음으로 정리했습니다.",
        },
    ]


def build_pytorch_personalized_report(analysis: Dict[str, Any], skin_mbti: Dict[str, Any]) -> Dict[str, Any]:
    """Create a report payload driven by model confidence and CV care scoring."""
    predicted_class = analysis.get("pytorch_predicted_class", "unknown")
    confidence = clamp_score(float(analysis.get("pytorch_confidence", 0)))
    confidence_level = confidence_to_level(confidence)
    skin_score = clamp_score(float(analysis.get("skin_score", confidence)))
    skin_status = classify_skin_status(analysis, skin_score)
    cards = build_pytorch_condition_cards(analysis, skin_status)
    top_concerns = cards[:2]
    products = build_pytorch_product_recommendations(skin_mbti, analysis)

    if skin_score >= 85:
        overall_level = "안정"
    elif skin_score >= 60:
        overall_level = "관찰"
    else:
        overall_level = "집중 케어"

    summary = (
        f"AI가 이번 사진을 {predicted_class} 클래스로 분류했습니다. "
        f"현재 결과는 {skin_status}으로 정리되며, 판정 신뢰도는 {confidence_level} 수준입니다."
    )

    return {
        "overall_score": skin_score,
        "overall_status": skin_status,
        "overall_level": overall_level,
        "summary": summary,
        "top_concerns": top_concerns,
        "condition_cards": cards,
        "product_recommendations": products,
        "routine": build_pytorch_routine(products, analysis),
        "disclaimer": "이 결과는 사진 분석과 설문 응답을 바탕으로 한 스킨케어 참고용 안내입니다.",
    }
