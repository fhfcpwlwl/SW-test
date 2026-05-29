"""Report builders for the PyTorch skin model result."""
from typing import Any, Dict, List

from skin_analyzer import build_pytorch_product_recommendations, build_pytorch_routine, clamp_score, score_to_level


def build_pytorch_condition_cards(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Turn PyTorch and CV outputs into explainable result cards."""
    skin_score = clamp_score(float(analysis.get("skin_score", analysis.get("pytorch_confidence", 0))))
    confidence = clamp_score(float(analysis.get("pytorch_confidence", 0)))
    acne_count = int(analysis.get("acne_count", 0) or 0)
    severity_ratio = float(analysis.get("severity_ratio", 0) or 0)

    return [
        {
            "key": "skin_score",
            "label": "피부 케어 점수",
            "score": skin_score,
            "level": score_to_level(skin_score),
            "focus_area": "종합 점수",
            "description": "AI 분류와 트러블 면적 분석을 함께 반영한 케어 점수입니다.",
        },
        {
            "key": "ai_confidence",
            "label": "AI 판정 신뢰도",
            "score": confidence,
            "level": score_to_level(confidence),
            "focus_area": "모델 확신도",
            "description": "AI가 현재 판정을 얼마나 강하게 선택했는지 보여줍니다.",
        },
        {
            "key": "acne_count",
            "label": "트러블 후보 개수",
            "score": acne_count,
            "level": "참고",
            "focus_area": "OpenCV 감점",
            "description": "피부 영역에서 붉은 트러블 후보로 감지된 작은 영역 수입니다.",
        },
        {
            "key": "severity_ratio",
            "label": "트러블 면적 비율",
            "score": round(severity_ratio, 2),
            "level": "참고",
            "focus_area": "OpenCV 감점",
            "description": "피부 영역 대비 붉은 트러블 후보 면적 비율입니다.",
        },
    ]


def build_pytorch_personalized_report(analysis: Dict[str, Any], skin_mbti: Dict[str, Any]) -> Dict[str, Any]:
    """Create a report payload driven by model confidence and CV care scoring."""
    predicted_class = analysis.get("pytorch_predicted_class", "unknown")
    confidence = clamp_score(float(analysis.get("pytorch_confidence", 0)))
    skin_score = clamp_score(float(analysis.get("skin_score", confidence)))
    cards = build_pytorch_condition_cards(analysis)
    top_concerns = cards[:3]
    products = build_pytorch_product_recommendations(skin_mbti, analysis)

    if skin_score >= 85:
        overall_level = "안정"
    elif skin_score >= 60:
        overall_level = "관찰"
    else:
        overall_level = "집중 케어"

    summary = (
        f"AI가 이번 사진을 {predicted_class} 클래스로 분류했습니다. "
        f"판정 신뢰도는 {confidence}%이고, 트러블 면적 분석을 반영한 피부 케어 점수는 {skin_score}점입니다."
    )

    return {
        "overall_score": skin_score,
        "overall_level": overall_level,
        "summary": summary,
        "top_concerns": top_concerns,
        "condition_cards": cards,
        "product_recommendations": products,
        "routine": build_pytorch_routine(products, analysis),
        "disclaimer": "이 결과는 사진 분석과 설문 응답을 바탕으로 한 스킨케어 참고용 안내입니다.",
    }
