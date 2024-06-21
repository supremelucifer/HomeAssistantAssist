# Modelo de Skill Alexa para integrar o Home Assistant via Assist Conversation API
Use o Home Assistant Assist Conversation na Alexa 😊

## Instruções

### Configuração do Home Assistant
- Crie/Ative uma API Home Assistant para seu usuário e obtenha um token de acesso de longa duração.

### Criação da Skill Alexa
1. Crie uma Skill Alexa-hosted (Python) na Alexa Developer Console:
   - **Name your Skill**: Escolha um nome de sua preferência (Ex: HomeAssist)
   - **Choose a primary locale**: Portuguese (BR)
   - **Tipo de experiência**: Other > Custom > Alexa-hosted (Python)
   - **Hosting region**: Pode deixar o padrão (US East (N. Virginia))
   - **Templates**: Clique em Import Skill
   - **Insira o endereço**: [https://github.com/rodrigoscoelho/skill-alexa-chatgpt4-assistpipeline-HomeAssistant.git](https://github.com/rodrigoscoelho/skill-alexa-chatgpt4-assistpipeline-HomeAssistant.git)

2. Vá na aba "Code"
3. Insira suas informações no arquivo `config.txt`:
   - Abra o arquivo `config.txt` no diretório raiz do projeto (/Skill Code/lambda/).
   - Insira as seguintes informações:
     ```txt
     home_assistant_url=https://YOUR-HOME-ASSISTANT-URL:8123/api/conversation/process
     home_assistant_token=YOUR-HOME-ASSISTANT-TOKEN
     home_assistant_agent_id=YOUR-AGENT-ID
     ```
   - **home_assistant_url**: URL da API de conversação do seu Home Assistant (incluindo a porta padrão 8123).
   - **home_assistant_token**: Token de acesso de longa duração do seu Home Assistant.
   - **home_assistant_agent_id**: ID do agente de conversação configurado no seu Home Assistant.

4. Salve as alterações.

### Configurando o Invocation Name
- O nome de invocação padrão configurado no código é "modo casa".
- Para alterar o nome de invocação:
  1. Vá para a aba "Build" no Alexa Developer Console.
  2. Clique em "Invocations" e depois em "Skill Invocation Name".
  3. Insira o novo nome de invocação desejado e salve as alterações.
  4. Rebuild o modelo (Build skill).

### Obtendo o `home_assistant_agent_id`
- O `agent_id` pode ser encontrado no assistente de debug para o seu agente de conversação alvo: 
  1. Acesse **Settings** > **Voice assistants** > **OpenAI** (ou o nome que você deu ao assistente OpenAI) > menu de três pontos > **Debug**.
  2. O `agent_id` será exibido na seção de debug.
  - Veja a imagem a seguir para referência:
    ![Debug Assistant](https://community-assets.home-assistant.io/original/4X/5/9/c/59cad339a22cb65c63996f58e28d412f73a6d40f.png)

### Deploy da Skill
1. Faça Build do Modelo e Deploy do Código na aba "Deploy".
2. Teste a Skill no console da Alexa Developer para garantir que está funcionando corretamente.

### Boa sorte!
Agora você pode usar sua Skill Alexa para integrar e interagir com o Home Assistant via Assist Conversation API.
Se gostou, lembre-se de mandar um ""Obrigado"" para o desenvolvedor.
