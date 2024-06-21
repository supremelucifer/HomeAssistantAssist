import os
import logging
import ask_sdk_core.utils as ask_utils
import json
import requests

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Função para carregar configurações do arquivo
def load_config():
    config = {}
    try:
        with open("/mnt/data/config.txt") as f:  # Usar o caminho absoluto para garantir que o arquivo seja encontrado
            for line in f:
                name, value = line.strip().split('=')
                config[name] = value
    except Exception as e:
        log_to_file(f"Erro ao carregar o arquivo de configuração: {str(e)}")
    return config

# Função para salvar logs em um arquivo
def log_to_file(message):
    with open("lambda_logs.txt", "a") as log_file:
        log_file.write(message + "\n")

config = load_config()

# Configurações do Home Assistant
home_assistant_url = config.get("home_assistant_url")
home_assistant_token = config.get("home_assistant_token")

# Verificação de configuração
if not home_assistant_url or not home_assistant_token:
    raise ValueError("home_assistant_url ou home_assistant_token não configurados corretamente")

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
        log_to_file(f"Query received: {query}")
        response = process_conversation(query)
        log_to_file(f"Response generated: {response}")
        return handler_input.response_builder.speak(response).ask("Você pode fazer uma nova pergunta ou falar: sair.").response

def process_conversation(query):
    global conversation_id
    try:
        headers = {
            "Authorization": f"Bearer {home_assistant_token}",
            "Content-Type": "application/json",
        }
        data = {
            "text": query,
            "language": "pt-BR"
        }
        if conversation_id:
            data["conversation_id"] = conversation_id

        log_to_file(f"Requesting Home Assistant with data: {data}")
        response = requests.post(home_assistant_url, headers=headers, json=data)
        log_to_file(f"Home Assistant response status: {response.status_code}")
        log_to_file(f"Home Assistant response data: {response.text}")
        
        response_data = response.json()

        if response.status_code == 200 and "response" in response_data:
            conversation_id = response_data.get("conversation_id", conversation_id)
            response_type = response_data["response"]["response_type"]
            if response_type == "action_done" or response_type == "query_answer":
                speech = response_data["response"]["speech"]["plain"]["speech"]
            elif response_type == "error":
                speech = response_data["response"]["speech"]["plain"]["speech"]
            else:
                speech = "Não consegui processar sua solicitação."
            return speech
        else:
            error_message = response_data.get("message", "Erro desconhecido")
            log_to_file(f"Erro ao processar a solicitação: {error_message}")
            return "Desculpe, não consegui entender seu pedido."

    except Exception as e:
        log_to_file(f"Erro ao gerar resposta: {str(e)}")
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
        log_to_file(f"Exception: {exception}")
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
