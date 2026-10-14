import os
from fastapi import FastAPI, Request
from gradio_client import Client

app = FastAPI()

# 1. Подключаемся к стабильному облачному ИИ-зеркалу на Hugging Face
HF_SPACE_URL = "JymNils/Voice-Cloning-XTTS-v2"
hf_client = Client(HF_SPACE_URL)

# 2. Прямой адрес вашего донорского файла с голосом Быстрова в репозитории
BENDER_VOICE_SAMPLE_URL = "https://raw.githubusercontent.com/bender_futurama.mp3"

@app.get("/")
def read_root():
    """Корневой маршрут, чтобы Vercel не выдавал ошибку 404"""
    return {"status": "Bender Bridge is Online"}

@app.post("/webhook/alisa")
async def alisa_webhook(request: Request):
    req_data = await request.json()
    user_command = req_data['request']['command']
    is_new_session = req_data['session']['new']
    
    # Обработка стартового приветствия при первом запуске навыка
    if is_new_session:
        return {
            "response": {
                "text": "Ну привет, мешок с костями! Робот Бендер на связи. Чего тебе?",
                "tts": "Ну приверт, меш+ок с кост+ями! Р+обот Б+ендер на св+язи. Ч+его теб+е?",
                "end_session": False
            },
            "version": "1.0"
        }
    
    # Формируем базовый текстовый ответ в характере персонажа
    ai_text_response = f"Слышь, кожаный, ты сказал: '{user_command}'. Мне лень думать, но мой блестящий зад подсказывает, что всё работает!"

    try:
        # 3. Отправляем текст ответа на озвучку в Hugging Face через Gradio API
        result = hf_client.predict(
            text=ai_text_response,
            language="ru",
            speaker_wav=BENDER_VOICE_SAMPLE_URL,
            api_name="/predict"
        )
        generated_audio_url = result
    except Exception:
        # Если ИИ-сервер перегружен, сбрасываем ссылку в None для мягкого отката
        generated_audio_url = None

    # 4. Проверяем, создался ли аудиофайл голоса Быстрова
    if generated_audio_url:
        return {
            "response": {
                "text": ai_text_response,
                "tts": f"<speaker audio='{generated_audio_url}'>", # Транслируем каноничный голос Бендера
                "end_session": False
            },
            "version": "1.0"
        }
    else:
        # Резервный сценарий: если ИИ занят, Алиса зачитает текст голосом Эрмила
        return {
            "response": {
                "text": f"[Резервный голос] {ai_text_response}",
                "tts": ai_text_response,
                "end_session": False
            },
            "version": "1.0"
        }
