import os
from fastapi import FastAPI, Request
from gradio_client import Client

app = FastAPI()

# Подключаемся к бесплатному генератору на Hugging Face (XTTS-v2)
HF_SPACE_URL = "JymNils/Voice-Cloning-XTTS-v2"
hf_client = Client(HF_SPACE_URL)

# ВСТАВЬ СЮДА СВОЮ ССЫЛКУ ИЗ ПУНКТА 2
BENDER_VOICE_SAMPLE_URL = "https://raw.githubusercontent.com/bender_futurama.mp3"

@app.post("/webhook/alisa")
async def alisa_webhook(request: Request):
    req_data = await request.json()
    user_command = req_data['request']['command']
    is_new_session = req_data['session']['new']
    
    if is_new_session:
        return {
            "response": {
                "text": "Ну привет, мешок с костями! Робот Бендер на связи. Чего тебе?",
                "tts": "Ну приверт, меш+ок с кост+ями! Р+обот Б+ендер на св+язи. Ч+его теб+е?",
                "end_session": False
            },
            "version": "1.0"
        }
    
    # Характерный ответ Бендера
    ai_text_response = f"Слышь, кожаный, ты сказал: '{user_command}'. Мне лень думать, но мой блестящий зад подсказывает, что всё работает!"

    try:
        # Отправляем в облачный генератор XTTS
        result = hf_client.predict(
            text=ai_text_response,
            language="ru",
            speaker_wav=BENDER_VOICE_SAMPLE_URL,
            api_name="/predict"
        )
        generated_audio_url = result
    except Exception:
        return {
            "response": {
                "text": f"[Ошибка озвучки] {ai_text_response}",
                "end_session": False
            },
            "version": "1.0"
        }

    return {
        "response": {
            "text": ai_text_response,
            "tts": f"<speaker audio='{generated_audio_url}'>",
            "end_session": False
        },
        "version": "1.0"
    }
