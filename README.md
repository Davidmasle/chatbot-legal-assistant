# Legal Chatbot Assistant

Локальный RAG-сервис для анализа юридических документов с использованием [Ollama](https://ollama.com/), [SentenceTransformers](https://www.sbert.net/) и [FastAPI](https://fastapi.tiangolo.com/).  
Позволяет загружать документы (PDF, DOCX), индексировать их локально и взаимодействовать с чат-ботом, который ищет ответы в контексте документов.

---

## Функции

- Загрузка и индексация **PDF/DOCX** документов  
- Генерация **эмбеддингов** с помощью **SentenceTransformers**
- **RAG** (Retrieval Augmented Generation)  
- Ответы из локальной LLM **Ollama**  
- Потоковая генерация ответов через **WebSocket** 
- **Bootstrap** интерфейс для взаимодействия с системой  
- **PostgreSQL** для хранения документов и чанков 

---

## Технологии

| Компонент | Описание |
|------------|-----------|
| **FastAPI** | Backend API и WebSocket-сервер |
| **Uvicorn** | ASGI сервер для FastAPI |
| **SQLAlchemy (Async)** | ORM для PostgreSQL |
| **PostgreSQL** | Хранилище документов и эмбеддингов |
| **SentenceTransformers** | Генерация векторных представлений текста |
| **Ollama (llama3)** | Локальная LLM для генерации ответов |
| **aiohttp** | Асинхронная работа с Ollama API |
| **Bootstrap 5** | Веб-интерфейс |
| **pdfplumber / python-docx** | Извлечение текста из документов |


---

### 1. Установка

```bash
git clone https://github.com/yourusername/legal-assistant-mvp.git
cd legal-assistant-mvp
```

```bash
python -m venv venv
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```
### 2. Подготовка моделей
```bash
ollama pull llama3
```


```bash
mkdir -p models
cd models
```
```bash
git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
```
### 3. Настройка БД

```bash
docker run --name legaldb -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=legaldb -p 5432:5432 -d postgres
```
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/legaldb
```
### 4. Запуск сервера
```bash
uvicorn app.main:app --reload --port 8005
```

## Взаимодействие
- Осуществляется через веб-интерфейс, доступен на http://127.0.0.1:8005
- Напрямую через curl
### Загрузка документа
```bash
curl -X POST "http://localhost:8005/upload" \
  -F "title=Договор аренды" \
  -F "file=@./docs/arenda.pdf"
```
Ответ:
```bash
{
  "message": "Документ 'Договор аренды' успешно загружен",
  "document_id": 1,
  "chunks": 18
}
```

![Основной интерфейс приложения](assets/main_page.png)
