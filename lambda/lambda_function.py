# -*- coding: utf-8 -*-
import os
import re
import logging
import json
import requests
import requests.exceptions
import random
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.attributes_manager import AttributesManager
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective, ExecuteCommandsDirective, OpenUrlCommand
from ask_sdk_model import Response
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Função para carregar configurações do arquivo
def load_config():
    config = {}
    try:
        with open("config.cfg", encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '=' not in line:
                    continue
                name, value = line.split('=', 1)
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
home_assistant_room_recognition = bool(config.get("home_assistant_room_recognition", False))
home_assistant_dashboard = config.get("home_assistant_dashboard")
home_assistant_kioskmode = bool(config.get("home_assistant_kioskmode", False))

# Função para carregar os arquivos de localização de cada idioma
def load_localization(locale):
    file_name = f"locale/{locale}.lang"
    if not os.path.exists(file_name):
        file_name = "locale/en-US.lang"
    
    try:
        with open(file_name, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '=' not in line:
                    continue
                name, value = line.split('=', 1)
                # Armazena diretamente nas variáveis globais
                globals()[name] = value
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo de localização: {str(e)}")

# Carrega o idioma padrão, que será alterado quando obter o idioma escolhido pelo usuário
load_localization("en-US")

# Verificação de configuração
if not home_assistant_url or not home_assistant_token or not home_assistant_agent_id or not home_assistant_language:
    raise ValueError("Alguma configuração não feita corretamente!")

# Variável global para armazenar o conversation_id
conversation_id = None
# Definir a variável global fora da função de handler
last_interaction_date = None

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # Obtém o idioma do usuário
        locale = handler_input.request_envelope.request.locale
        load_localization(locale)
        
        global conversation_id, last_interaction_date
        #conversation_id = None  # Redefine o conversation_id para uma nova sessão sempre que iniciar

        # Obter a data e hora atual com fuso horário atual
        now = datetime.now(timezone(timedelta(hours=-3)))

        # Carregar o arquivo de configuração
        current_date = now.strftime('%Y-%m-%d')

        speak_output = globals().get("alexa_speak_next_message")

        if last_interaction_date != current_date:
            # Primeira execução do dia
            speak_output = globals().get("alexa_speak_welcome_message")
            last_interaction_date = current_date
        
        # Device supported interfaces
        device = handler_input.request_envelope.context.system.device
        is_apl_supported = device.supported_interfaces.alexa_presentation_apl is not None
        
        logger.debug("device: " + repr(device))
        
        # Renderiza o documento APL com o botão para abrir o HA (se o dispositivo tiver tela)
        if is_apl_supported:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token=home_assistant_token,
                    document=load_template("apl_openha.json")
                )
            )

        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class GptQueryIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        # Adicionar o prefixo com o nome do dispositivo ao comando
        query = handler_input.request_envelope.request.intent.slots["query"].value
        logger.info(f"Query received: {query}")
        
        # Se o usuário der um comando para abrir o dashboard ou o home assistant, executa a ação
        keywords = globals().get("keywords_to_open_dashboard").split(";")
        if any(keyword.strip().lower() in query.lower() for keyword in keywords):
            logger.info("Abrindo o dashboard do Home Assistant")
            open_page(handler_input)
            return handler_input.response_builder.speak(globals().get("alexa_speak_open_dashboard")).response
        
        device_id = ""
        if home_assistant_room_recognition:
            # Obter o deviceId do dispositivo que executou a skill
            device_id = ". device_id: " + handler_input.request_envelope.context.system.device.device_id
        
        response = process_conversation(f"{query}{device_id}")
        
        logger.info(f"Response generated: {response}")
        return handler_input.response_builder.speak(response).ask(globals().get("alexa_speak_question")).response

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

        logger.debug(f"HA request data: {data}")
        
        response = requests.post(home_assistant_url, headers=headers, json=data, timeout=8)
        
        logger.debug(f"HA response status: {response.status_code}")
        logger.debug(f"HA response data: {response.text}")
        
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
                speech = globals().get("alexa_speak_error")
            return improve_response(speech)
        else:
            error_message = response_data.get("message", "Erro desconhecido")
            logger.error(f"Erro ao processar a solicitação: {error_message}")
            return globals().get("alexa_speak_error")
            
    except requests.exceptions.Timeout as te:
        # Tratamento para timeout
        logger.error(f"Timeout ao se comunicar com o Home Assistant: \n {str(te)}", exc_info=True)
        return globals().get("alexa_speak_timeout")

    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {str(e)}", exc_info=True)
        return globals().get("alexa_speak_error")

def replace_words(query):
    query = query.replace('4.º','quarto')
    return query

def improve_response(speech):
    # Substituições específicas
    speech = speech.replace(':\n\n', '')
    speech = speech.replace('\n\n', '. ')
    speech = speech.replace('\n', ',')
    speech = speech.replace('-', '')
    speech = speech.replace('_', ' ')
    
    # Substituir as vogais com trema
    replacements = str.maketrans('ïöüÏÖÜ', 'iouIOU')
    speech = speech.translate(replacements)

    # Remover restante dos caracteres especiais que engine não pronuncia corretamente
    speech = re.sub(r'[^A-Za-z0-9çÇáàâãéèêíóôõúñÁÀÂÃÉÈÊÍÓÔÕÚÑ\s.,!?]', '', speech)

    return speech

def load_template(filepath):
    # Carrega o template da interface gráfica
    with open(filepath, encoding='utf-8') as f:
        template = json.load(f)

    if filepath == 'apl_openha.json':
        # Substituindo os valores dinâmicos do APL
        template['mainTemplate']['items'][0]['items'][2]['text'] = globals().get("echo_screen_welcome_text")
        template['mainTemplate']['items'][0]['items'][3]['text'] = globals().get("echo_screen_click_text")
        template['mainTemplate']['items'][0]['items'][4]['onPress']['source'] = get_hadash_url()
        template['mainTemplate']['items'][0]['items'][4]['item']['text'] = globals().get("echo_screen_button_text")

    return template

def open_page(handler_input):
    # Device supported interfaces
    is_apl_supported = handler_input.request_envelope.context.system.device.supported_interfaces.alexa_presentation_apl is not None
        
    logger.debug(f"APL supported: {is_apl_supported}")
    
    if is_apl_supported:
        # Renderizar modelo vazio, necessário para o comando OpenURL
        # https://amazon.developer.forums.answerhub.com/questions/220506/alexa-open-a-browser.html
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token=home_assistant_token,
                document=load_template("apl_empty.json")
            )
        )

        # Open default page of dashboard
        handler_input.response_builder.add_directive(
            ExecuteCommandsDirective(
                token=home_assistant_token,
                commands=[OpenUrlCommand(source=get_hadash_url())]
            )
        ) 

def get_hadash_url():
    global home_assistant_dashboard
    if not home_assistant_dashboard:
        home_assistant_dashboard = "lovelace"
            
    source = home_assistant_url.replace('api/conversation/process', home_assistant_dashboard)    
    if home_assistant_kioskmode:
        source += '?kiosk'
        
    return source

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = globals().get("alexa_speak_help")
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        open_page(handler_input)
        speak_output = random.choice(globals().get("alexa_speak_exit").split(";"))
        return handler_input.response_builder.speak(globals().get("speak_output")).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        open_page(handler_input)
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speak_output = globals().get("alexa_speak_error")
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()