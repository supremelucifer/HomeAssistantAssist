# Modelo de Skill Alexa para integrar o Home assistant via Assist Pipeline API
Use o Home Assistant Assist na Alexa 😊  

# Instruções
- Crie/Ative uma API Home assistant para seu usuário

- Crie uma Skill Alexa-hosted (Python) na Alexa: https://developer.amazon.com/alexa/console/ask/create-new-skill
  - Name your Skill: Escolha um nome de sua preferência (Ex: HomeAssist)
  - Choose a primary locale: Portuguese (BR)  
  - Em tipo de experiência selecione: Other > Custom > Alexa-hosted (Python)  
  - Hosting region: Pode deixar o padrão (US East (N. Virginia))
  - Templates: Clique em Import Skill
  - Insira o endereço: https://github.com/rodrigoscoelho/skill-alexa-chatgpt4-assistpipeline-HomeAssistant.git

- Vá na aba "Code"
- Insira suas informações no código: lambda > lambda_function.py:
  ```python
  home_assistant_url = "wss://YOUR-HOME-ASSISTANT-URL/api/websocket"
  home_assistant_token = "YOUR-HOME-ASSISTANT-TOKEN"
  ```
- Salve as alterações

- Faça Build do Modelo e Deploy do Código.

- Seja feliz!