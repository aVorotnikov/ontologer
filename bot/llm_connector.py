#!/usr/bin/python3

from ollama import chat


class LlmConnector:
    def __init__(self):
        self.model = "qwen2:latest"


    def generate_response(self, message):
        response = chat(model=self.model, messages=[{
            "role": "user",
            "content": message
        }])
        return response.message.content


if __name__ == "__main__":
    connector = LlmConnector()
    print(connector.generate_response(
        'Ответь односложно: "Да" или "Нет". '
        'Эквиваленты ли 2 утверждения "Элемент множества - это часть множества" и "Множество состоит из элементов множества"?'))
