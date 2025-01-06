# -*- coding: utf-8 -*-
import os
import re
import logging
import json
import random
import uuid
import requests
import requests.exceptions
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective, ExecuteCommandsDirective, OpenUrlCommand
from datetime import datetime, timezone, timedelta

# Carrega as configurações e localizações
def load_config(file_name):
    
    if str(file_name).endswith(".lang") and not os.path.exists(file_name):
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
        logger.error(f"Error loading file: {str(e)}")

load_config("config.cfg")

# Carrega o idioma padrão, que será alterado quando obter o idioma escolhido pelo usuário quando a skill for iniciada
load_config("locale/en-US.lang")

# Configuração de log
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Verificação de configuração
if not globals().get("home_assistant_url") or not globals().get("home_assistant_token"):
    raise ValueError("home_assistant_url or home_assistant_token configuration are not set!")

# Identificador da conversa
conversation_id = None
# Última sessão da skill
last_interaction_date = None
# APL Supported
is_apl_supported = False
# Document Token
apl_document_token = str(uuid.uuid4())

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        global conversation_id, last_interaction_date, is_apl_supported, account_linking_token
        
        # Carrega o idioma do usuário
        locale = handler_input.request_envelope.request.locale
        load_config(f"locale/{locale}.lang")
        
        #conversation_id = None # 'Descomente' se quiser que uma nova sessão de diálogo com a IA sempre que iniciar

        # Verifica se o dispositivo tem tela (APL support), se sim, carrega a interface
        device = handler_input.request_envelope.context.system.device
        is_apl_supported = device.supported_interfaces.alexa_presentation_apl is not None
        logger.debug("Device: " + repr(device))
        
        # Renderiza o documento APL com o botão para abrir o HA (se o dispositivo tiver tela)
        if is_apl_supported:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token=apl_document_token,
                    document=load_template("apl_openha.json")
                )
            )
            
        # Define o último acesso e define qual frase de boas vindas responder
        now = datetime.now(timezone(timedelta(hours=-3)))
        current_date = now.strftime('%Y-%m-%d')
        speak_output = globals().get("alexa_speak_next_message")
        if last_interaction_date != current_date:
            # Primeira execução do dia
            speak_output = globals().get("alexa_speak_welcome_message")
            last_interaction_date = current_date        

        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class GptQueryIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        # Captura a consulta do usuário
        query = handler_input.request_envelope.request.intent.slots["query"].value
        logger.info(f"Query received from Alexa: {query}")
        
        # Trata comandos/palavras chaves específicas
        response = keywords_exec(query, handler_input)
        if response:
            return response
        
        device_id = ""
        if bool(globals().get("home_assistant_room_recognition", "").lower() == "true"):
            # Obter o deviceId do dispositivo que executou a skill
            device_id = ". device_id: " + handler_input.request_envelope.context.system.device.device_id
        
        response = process_conversation(f"{query}{device_id}")
        logger.info(f"Response generated: {response}")
        return handler_input.response_builder.speak(response).ask(globals().get("alexa_speak_question")).response

# Trata palavras chaves para executar comandos específicos
def keywords_exec(query, handler_input):
    # Se o usuário der um comando para 'abrir dashboard' ou 'abrir home assistant', abre o dashboard e interrompe a skill
    keywords_top_open_dash = globals().get("keywords_to_open_dashboard").split(";")
    if any(ko.strip().lower() in query.lower() for ko in keywords_top_open_dash):
        logger.info("Opening Home Assistant dashboard")
        open_page(handler_input)
        return handler_input.response_builder.speak(globals().get("alexa_speak_open_dashboard")).response
    
    # Se o usuário der um comando de agradecimento o upara sair, interrompe a skill
    keywords_close_skill = globals().get("keywords_to_close_skill").split(";")
    if any(kc.strip().lower() in query.lower() for kc in keywords_close_skill):
        logger.info("Closing skill from keyword command")
        return CancelOrStopIntentHandler().handle(handler_input)
    
    # Se não for uma palavra-chave, continua o fluxo normalmente
    return None

# Chama a API do Home Assistant e trata a resposta
def process_conversation(query):
    global conversation_id
    
    home_assistant_agent_id = globals().get("home_assistant_agent_id", None)
    home_assistant_language = globals().get("home_assistant_language", None)
        
    try:
        headers = {
            "Authorization": "Bearer {}".format(globals().get("home_assistant_token")),
            "Content-Type": "application/json",
        }
        data = {
            "text": replace_words(query)
        }
        # Adding optional parameters to request
        if home_assistant_language:
            data["language"] = home_assistant_language
        if home_assistant_agent_id:
            data["agent_id"] = home_assistant_agent_id
        if conversation_id:
            data["conversation_id"] = conversation_id

        # Faz a requisição na API do Home Assistant
        ha_api_url = "{}/api/conversation/process".format(globals().get("home_assistant_url"))
        logger.debug(f"HA request url: {ha_api_url}")        
        logger.debug(f"HA request data: {data}")
        
        response = requests.post(ha_api_url, headers=headers, json=data, timeout=7)
        
        logger.debug(f"HA response status: {response.status_code}")
        logger.debug(f"HA response data: {response.text}")
        
        contenttype = response.headers.get('Content-Type', '')
        logger.debug(f"Content-Type: {contenttype}")
        
        if (contenttype == "application/json"):
            response_data = response.json()
            if response.status_code == 200 and "response" in response_data:
                conversation_id = response_data.get("conversation_id", conversation_id)
                response_type = response_data["response"]["response_type"]
                
                if response_type == "action_done" or response_type == "query_answer":
                    speech = response_data["response"]["speech"]["plain"]["speech"]
                    # Remover "device_id:" e o que vem depois
                    if "device_id:" in speech:
                        speech = speech.split("device_id:")[0].strip()
                elif response_type == "error":
                    speech = response_data["response"]["speech"]["plain"]["speech"]
                    logger.error(f"Error code: {response_data['response']['data']['code']}")
                else:
                    speech = globals().get("alexa_speak_error")
                
            return improve_response(speech)
        elif (contenttype == "text/html") and int(response.status_code, 0) >= 400:
            errorMatch = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
            
            if errorMatch:
                title = errorMatch.group(1)
                logger.error(f"HTTP error {response.status_code} ({title}): Unable to connect to your Home Assistant server")
            else:
                logger.error(f"HTTP error {response.status_code}: Unable to connect to your Home Assistant server. \n {response.text}")
                
            return globals().get("alexa_speak_error")
        elif  (contenttype == "text/plain") and int(response.status_code, 0) >= 400:
            logger.error(f"Error processing request: {response.text}")
            return globals().get("alexa_speak_error")
        else:
            logger.error(f"Error processing request: {response.text}")
            return globals().get("alexa_speak_error")
            
    except requests.exceptions.Timeout as te:
        # Tratamento para timeout
        logger.error(f"Timeout when communicating with Home Assistant: {str(te)}", exc_info=True)
        return globals().get("alexa_speak_timeout")

    except Exception as e:
        logger.error(f"Error processing response: {str(e)}", exc_info=True)
        return globals().get("alexa_speak_error")

# Substitui palavras geradas incorretamente pelo interpretador da Alexa na query
def replace_words(query):
    query = query.replace('4.º','quarto')
    return query

# Substitui palavras e caracteres especiais para falar a resposta da API
def improve_response(speech):
    # Função para melhorar a legibilidade da resposta
    speech = speech.replace(':\n\n', '').replace('\n\n', '. ').replace('\n', ',').replace('-', '').replace('_', ' ')
    
    #replacements = str.maketrans('ïöüÏÖÜ', 'iouIOU')
    #speech = speech.translate(replacements)
    
    speech = re.sub(r'[^A-Za-z0-9çÇáàâãéèêíïóôõöúüñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÜÑ\s.,!?]', '', speech)
    return speech

# Carrega o template do APL da tela inicial
def load_template(filepath):
    # Carrega o template da interface gráfica
    with open(filepath, encoding='utf-8') as f:
        template = json.load(f)

    if filepath == 'apl_openha.json':
        # Localiza os textos dinâmicos do APL 
        template['mainTemplate']['items'][0]['items'][2]['text'] = globals().get("echo_screen_welcome_text")
        template['mainTemplate']['items'][0]['items'][3]['text'] = globals().get("echo_screen_click_text")
        template['mainTemplate']['items'][0]['items'][4]['onPress']['source'] = get_hadash_url()
        template['mainTemplate']['items'][0]['items'][4]['item']['text'] = globals().get("echo_screen_button_text")

    return template

# Abre dashboard do Home Assistant no navegador Silk
def open_page(handler_input):
    if is_apl_supported:
        # Renderizar modelo vazio, necessário para o comando OpenURL
        # https://amazon.developer.forums.answerhub.com/questions/220506/alexa-open-a-browser.html
        
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token=apl_document_token,
                document=load_template("apl_empty.json")
            )
        )
        
        # Open default page of dashboard
        handler_input.response_builder.add_directive(
            ExecuteCommandsDirective(
                token=apl_document_token,
                commands=[OpenUrlCommand(source=get_hadash_url())]
            )
        )

# Monta a URL do dashboard do Home Assistant
def get_hadash_url():
    ha_dashboard_url = globals().get("home_assistant_url")
    ha_dashboard_url += "/{}".format(globals().get("home_assistant_dashboard", "lovelace"))
    
    # Adicionando o modo kioskmode, se estiver ativado
    home_assistant_kioskmode = bool(globals().get("home_assistant_kioskmode", False))
    if home_assistant_kioskmode:
        ha_dashboard_url += '?kiosk'
    
    logger.debug(f"ha_dashboard_url: {ha_dashboard_url}")
    return ha_dashboard_url

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
        speak_output = random.choice(globals().get("alexa_speak_exit").split(";"))
        return handler_input.response_builder.speak(speak_output).set_should_end_session(True).response

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