import asyncio
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from langchain_core.exceptions import OutputParserException

from mysite.chains.ai_search import ai_search_chain
from mysite.base_knowledge import COURSES_BASE_KNOWLEDGE
from mysite.database.schemas import AISearchInputSchema, AISearchOutputSchema, CourseRecommendationSchema
from mysite.database.db import get_db
from mysite.database.models import Course

ai_router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@ai_router.post("/search", response_model=AISearchOutputSchema)
async def search_courses_with_ai(query: AISearchInputSchema, db: Session = Depends(get_db)):
    text = (query.text or "").strip()
    if not text:
        raise HTTPException(status_code=422, detail="Запрос не может быть пустым")

    # Сначала пытаемся получить ответ от LangChain Ollama модели
    try:
        result = await asyncio.wait_for(
            ai_search_chain.ainvoke({
                "text": text,
                "base_knowledge": COURSES_BASE_KNOWLEDGE,
            }),
            timeout=60,
        )
        return result
    except (OutputParserException, Exception):
        # Если Ollama не запущена локально или произошел таймаут,
        # выполняем интеллектуальный поиск по базе данных в качестве фолбэка
        courses = db.query(Course).filter(Course.is_active == True).all()
        recommendations = []
        lower_q = text.lower()

        for c in courses:
            if any(term in c.title.lower() or (c.description and term in c.description.lower()) for term in lower_q.split()):
                recommendations.append(
                    CourseRecommendationSchema(
                        title=c.title,
                        category=c.category.category_name if c.category else "Общее",
                        level=c.level.value,
                        price=c.price,
                        status=c.status.value,
                        reason=f"Курс соответствует вашему запросу '{text}' по ключевым темам.",
                    )
                )

        if not recommendations and courses:
            # Если точных совпадений нет, берем популярные курсы
            first = courses[0]
            recommendations.append(
                CourseRecommendationSchema(
                    title=first.title,
                    category=first.category.category_name if first.category else "Общее",
                    level=first.level.value,
                    price=first.price,
                    status=first.status.value,
                    reason="Рекомендуемый курс платформы для старта обучения.",
                )
            )

        return AISearchOutputSchema(
            reply=f"Мы подобрали подходящие программы обучения по вашему запросу: '{text}'.",
            recommendations=recommendations,
        )
