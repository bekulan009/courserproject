from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from mysite.config import OLLAMA_URL, OLLAMA_MODEL
from mysite.database.schemas import AISearchOutputSchema
from mysite.base_knowledge import COURSES_BASE_KNOWLEDGE

ai_search_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Ты умный консультант образовательной платформы курсов. "
            "Твоя задача — помочь пользователю подобрать наиболее подходящий курс на русском языке на основе его запроса. "
            "Используй базу знаний платформы:\n{base_knowledge}\n\n"
            "Правила подбора: "
            "1. В поле reply напиши вежливый, понятный и структурированный ответ в 2-4 предложениях. "
            "2. В списке recommendations укажи подходящие курсы со следующими полями: "
            "   - title: точное название курса; "
            "   - category: категория (например, Программирование, Data Science, Дизайн, Frontend); "
            "   - level: уровень сложности (beginner, intermediate, advanced); "
            "   - price: стоимость курса (0 для бесплатных); "
            "   - status: free (бесплатный) или plus (платный с расширенным доступом); "
            "   - reason: краткое объяснение, почему этот курс подходит пользователю. "
            "3. Не придумывай несуществующие факты, опирайся на запрос пользователя и уровень его подготовки."
        ),
        (
            "human",
            "{text}"
        ),
    ]
)

ai_search_model = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_URL,
    temperature=0,
    num_predict=400,
)

structured_ai_search = ai_search_model.with_structured_output(
    AISearchOutputSchema,
    method="json_schema",
)

ai_search_chain = ai_search_prompt | structured_ai_search
