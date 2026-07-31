"""Recommendation engine service for LearnTwin AI."""

import json
import logging
from typing import Any, Dict, List, Optional, TypedDict

from app.services.digital_twin_service import DigitalTwinService
from app.services.ollama_client import OllamaClient
from app.services.vector_store import VectorStore


class RecommendationResult(TypedDict):
    summary: str
    recommended_next_topic: str
    revision_advice: str
    difficulty_level: str
    study_duration: str
    motivation_message: str


class RecommendationService:
    """Generate personalized study recommendations for a learner."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        ollama_client: Optional[OllamaClient] = None,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.vector_store = vector_store or VectorStore()
        self.ollama_client = ollama_client or OllamaClient()

    async def generate_recommendation(self, user_id: str, db: Any) -> RecommendationResult:
        """Generate a recommendation for the specified learner.

        Args:
            user_id: Identifier for the learner.
            db: Database session used by DigitalTwinService.

        Returns:
            A structured recommendation result.
        """
        twin = DigitalTwinService(db).get_twin(user_id)
        if twin is None:
            self.logger.warning("Digital twin not found for user_id=%s", user_id)
            return self._default_result(
                summary="Learner profile not found.",
                recommended_next_topic="",
                revision_advice="",
                difficulty_level="",
                study_duration="",
                motivation_message="Please create a learner profile before requesting recommendations.",
            )

        materials = self._retrieve_relevant_materials(twin)
        prompt = self._build_prompt(twin, materials)
        completion = await self.ollama_client.generate(prompt)
        return self._parse_recommendation_response(completion)

    def _retrieve_relevant_materials(self, twin: Any) -> List[Dict[str, Any]]:
        query_text = self._build_retrieval_query(twin)
        results = self.vector_store.query(query_text, top_k=5)
        if not results:
            self.logger.info("No relevant study materials found for query: %s", query_text)
        return results

    def _build_retrieval_query(self, twin: Any) -> str:
        parts = [twin.current_topic or "general learning"]
        if twin.strengths:
            parts.append("strengths: " + ", ".join(twin.strengths))
        if twin.weaknesses:
            parts.append("weaknesses: " + ", ".join(twin.weaknesses))
        return " | ".join(parts)

    def _build_prompt(self, twin: Any, materials: List[Dict[str, Any]]) -> str:
        return (
            "You are a study planning assistant. "
            "Review the learner's current profile and recommend the next study steps. "
            "Return a JSON object with keys: summary, recommended_next_topic, revision_advice, difficulty_level, study_duration, motivation_message. "
            "Use concise, helpful language and avoid extra fields.\n\n"
            f"Current topic: {twin.current_topic or 'unspecified'}\n"
            f"Knowledge score: {twin.knowledge_score}\n"
            f"Confidence: {twin.confidence}\n"
            f"Engagement: {twin.engagement}\n"
            f"Strengths: {', '.join(twin.strengths) if twin.strengths else 'none'}\n"
            f"Weaknesses: {', '.join(twin.weaknesses) if twin.weaknesses else 'none'}\n"
            f"Recent learning history:\n{self._format_learning_history(twin.learning_history)}\n"
            f"Relevant documents:\n{self._format_materials(materials)}\n"
            "Provide the recommendation in valid JSON only."
        )

    def _format_learning_history(self, history: Any) -> str:
        if not history:
            return "No recent history available."
        lines = []
        for entry in history[-5:]:
            topic = getattr(entry, "topic", "unknown topic")
            duration = getattr(entry, "duration_minutes", None)
            score = entry.metadata.get("score") if getattr(entry, "metadata", None) else None
            lines.append(
                f"- {topic} (duration: {duration or 'unknown'} min, score: {score if score is not None else 'n/a'})"
            )
        return "\n".join(lines)

    def _format_materials(self, materials: List[Dict[str, Any]]) -> str:
        if not materials:
            return "No matched study materials found."
        lines = []
        for item in materials:
            title = item.get("metadata", {}).get("title") or item.get("document_id")
            snippet = item.get("text", "").strip().replace("\n", " ")
            if len(snippet) > 160:
                snippet = snippet[:157].rstrip() + "..."
            lines.append(f"- {title}: {snippet}")
        return "\n".join(lines)

    def _parse_recommendation_response(self, response_text: str) -> RecommendationResult:
        if not response_text:
            self.logger.error("Empty response from Ollama recommendation generation")
            return self._default_result(
                summary="Unable to generate recommendations at this time.",
                recommended_next_topic="",
                revision_advice="",
                difficulty_level="",
                study_duration="",
                motivation_message="Please try again later.",
            )

        try:
            parsed = json.loads(response_text)
            if not isinstance(parsed, dict):
                raise ValueError("Parsed response is not a dict")
            return {
                "summary": str(parsed.get("summary", "")),
                "recommended_next_topic": str(parsed.get("recommended_next_topic", "")),
                "revision_advice": str(parsed.get("revision_advice", "")),
                "difficulty_level": str(parsed.get("difficulty_level", "")),
                "study_duration": str(parsed.get("study_duration", "")),
                "motivation_message": str(parsed.get("motivation_message", "")),
            }
        except (json.JSONDecodeError, ValueError) as exc:
            self.logger.warning("Failed to parse Ollama recommendation response: %s", exc)
            return {
                "summary": response_text.strip(),
                "recommended_next_topic": "",
                "revision_advice": "",
                "difficulty_level": "",
                "study_duration": "",
                "motivation_message": "",
            }

    def _default_result(
        self,
        summary: str,
        recommended_next_topic: str,
        revision_advice: str,
        difficulty_level: str,
        study_duration: str,
        motivation_message: str,
    ) -> RecommendationResult:
        return {
            "summary": summary,
            "recommended_next_topic": recommended_next_topic,
            "revision_advice": revision_advice,
            "difficulty_level": difficulty_level,
            "study_duration": study_duration,
            "motivation_message": motivation_message,
        }
