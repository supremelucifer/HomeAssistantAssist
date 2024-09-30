# -*- coding: utf-8 -*-
import os
import logging
import json
import requests
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_core.attributes_manager import AttributesManager
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Função para carregar configurações do arquivo
def load_config():
    config = {}
    try:
        with open("config.txt", encoding='utf-8') as f:
            for line in f:
                name, value = line.strip().split('=')
                config[name] = value
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo de configuração: {str(e)}")
    return config

config = load_config()

# Configurações do Home Assistant
home_assistant_url = config.get("home_assistant_url")
home_assistant_token = config.get("home_assistant_token")
home_assistant_agent_id = config.get("home_assistant_agent_id")
home_assistant_language = config.get("home_assistant_language")
alexa_speak_welcome_message = config.get("alexa_speak_welcome_message")
alexa_speak_next_message = config.get("alexa_speak_next_message")
alexa_speak_question = config.get("alexa_speak_question")
alexa_speak_help = config.get("alexa_speak_help")
alexa_speak_exit = config.get("alexa_speak_exit")
alexa_speak_error = config.get("alexa_speak_error")

# Verificação de configuração
if not home_assistant_url or not home_assistant_token or not home_assistant_agent_id or not home_assistant_language or not alexa_speak_welcome_message or not alexa_speak_next_message or not alexa_speak_question or not alexa_speak_help or not alexa_speak_exit or not alexa_speak_error:
    raise ValueError("Alguma configuração não feita corretamente!")

# Variável global para armazenar o conversation_id
conversation_id = None
# Definir a variável global fora da função de handler
last_interaction_date = None

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        global conversation_id, last_interaction_date
        conversation_id = None  # Reseta o conversation_id para uma nova sessão

        # Obter a data e hora atual com fuso horário UTC-3
        now = datetime.now(timezone(timedelta(hours=-3)))  # UTC-3 para o Brasil

        # Carregar o arquivo de configuração
        current_date = now.strftime('%Y-%m-%d')

        speak_output = alexa_speak_next_message

        if last_interaction_date != current_date:
            # Primeira execução do dia
            speak_output = alexa_speak_welcome_message
            last_interaction_date = current_date

        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class GptQueryIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        # Obter o deviceId do dispositivo que executou a skill
        device_id = handler_input.request_envelope.context.system.device.device_id
        
        # Adicionar o prefixo com o nome do dispositivo ao comando
        query = handler_input.request_envelope.request.intent.slots["query"].value
        logger.info(f"Query received from: {query}")
        logger.info(f"Device ID: {device_id}")
        response = process_conversation(f"{query}. device_id: {device_id}")
        
        logger.info(f"Response generated: {response}")
        return handler_input.response_builder.speak(response).ask(alexa_speak_question).response

def process_conversation(query):
    global conversation_id
    try:
        headers = {
            "Authorization": f"Bearer {home_assistant_token}",
            "Content-Type": "application/json",
        }
        data = {
            "text": replace_words(query),
            "language": home_assistant_language,
            "agent_id": home_assistant_agent_id
        }
        if conversation_id:
            data["conversation_id"] = conversation_id

        logger.debug(f"Requesting Home Assistant with data: {data}")
        response = requests.post(home_assistant_url, headers=headers, json=data)
        logger.debug(f"Home Assistant response status: {response.status_code}")
        logger.debug(f"Home Assistant response data: {response.text}")
        
        response_data = response.json()

        if response.status_code == 200 and "response" in response_data:
            conversation_id = response_data.get("conversation_id", conversation_id)
            response_type = response_data["response"]["response_type"]
            if response_type == "action_done" or response_type == "query_answer":
                speech = response_data["response"]["speech"]["plain"]["speech"]
            elif response_type == "error":
                speech = response_data["response"]["speech"]["plain"]["speech"]
                logger.error(f"Error code: {response_data['response']['data']['code']}")
            else:
                speech = alexa_speak_error
            return speech
        else:
            error_message = response_data.get("message", "Erro desconhecido")
            logger.error(f"Erro ao processar a solicitação: {error_message}")
            return alexa_speak_error

    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {str(e)}", exc_info=True)
        return f"Erro ao gerar resposta: {str(e)}"

def replace_words(query):
    query = query.replace('4.º','quarto')
    return query

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = alexa_speak_help
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = alexa_speak_exit
        return handler_input.response_builder.speak(speak_output).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class CloseSkillIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CloseSkillIntent")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.speak(alexa_speak_exit).set_should_end_session(True).response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speak_output = alexa_speak_error
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(CloseSkillIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()