import os
import logging
import ask_sdk_core.utils as ask_utils
import asyncio
import json
import websockets
import uuid

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configurações do Home Assistant
home_assistant_url = "wss://YOUR-HOME-ASSISTANT-URL/api/websocket"
home_assistant_token = "YOUR-HOME-ASSISTANT-TOKEN"

# Variável global para armazenar o conversation_id
conversation_id = None

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        global conversation_id
        conversation_id = None  # Reseta o conversation_id para uma nova sessão
        speak_output = "Bem vindo ao assistente de voz do Home Assistant! Qual a sua pergunta?"
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class GptQueryIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        query = handler_input.request_envelope.request.intent.slots["query"].value
        response = asyncio.run(process_conversation(query))
        return handler_input.response_builder.speak(response).ask("Você pode fazer uma nova pergunta ou falar: sair.").response

async def process_conversation(query):
    global conversation_id
    try:
        async with websockets.connect(home_assistant_url) as websocket:
            # Autenticação
            auth_message = json.dumps({
                "type": "auth",
                "access_token": home_assistant_token
            })
            await websocket.send(auth_message)
            
            response = await websocket.recv()
            response_data = json.loads(response)
            if response_data.get("type") != "auth_ok":
                return "Erro ao autenticar no Home Assistant."

            # Envia a mensagem de processamento de conversação
            conversation_message = {
                "type": "conversation/process",
                "text": query,
                "language": "pt-BR"
            }
            if conversation_id:
                conversation_message["conversation_id"] = conversation_id

            await websocket.send(json.dumps(conversation_message))

            while True:
                response = await websocket.recv()
                response_data = json.loads(response)

                if response_data.get("type") == "result" and response_data.get("success", False):
                    conversation_response = response_data["result"]
                    conversation_id = conversation_response.get("conversation_id", conversation_id)
                    speech = conversation_response["response"]["speech"]["plain"]["speech"]
                    return speech

                if response_data.get("type") == "error":
                    return f"Erro ao processar a solicitação: {response_data.get('message')}"

    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Como posso te ajudar?"
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Até logo!"
        return handler_input.response_builder.speak(speak_output).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speak_output = "Desculpe, não consegui processar sua solicitação."
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
