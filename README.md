# Alexa Skill thats integrate Home Assistant Assist or Generative AI through Conversation Process API
Use Home Assistant Assist or IA generative conversation in Alexa 😊

## INSTRUCTIONS

### Setting up Home Assistant
- Create/Activate a Home Assistant API for your user and obtain a long-term access token.

### Creating the Alexa Skill
1. Create an Alexa-hosted (Python) Skill in the Alexa Developer Console:
   - **Name your Skill**: Choose a name of your preference (e.g., HomeAssist)
   - **Choose a primary locale**: Portuguese (BR)
   - **Type of experience**: Other > Custom > Alexa-hosted (Python)
   - **Hosting region**: You can leave the default (US East (N. Virginia))
   - **Templates**: Click on Import Skill
   - **Insert the address**: [https://github.com/fabianosan/skill-alexa-chatgpt4-assistpipeline-HomeAssistant.git](https://github.com/fabianosan/skill-alexa-chatgpt4-assistpipeline-HomeAssistant.git)
2. Go to the "Code" tab
3. Enter your information in the `config.txt` file:
   - Open the `config.txt` file in the root directory of the project (/Skill Code/lambda/).
   - Insert the following information:
     ```txt
     home_assistant_url=https://YOUR-EXTERNAL-HOME-ASSISTANT-URL/api/conversation/process
     home_assistant_token=YOUR-HOME-ASSISTANT-TOKEN
     home_assistant_agent_id=YOUR-AGENT-ID
     home_assistant_language=pt-BR
     ```
   - **home_assistant_url**: Your Home Assistant conversation API URL.
   - **home_assistant_token**: Your Home Assistant's long-term access token.
   - **home_assistant_agent_id**: The conversation agent ID configured in your Home Assistant.
   - **home_assistant_language**: Language to call the conversation API in Home Assistant (example: en-US).
4. Still in the configuration file, change the phrases as you wish.
5. Save the changes.
6. Deploy.

### Configuring the Invocation Name
- The default invocation name configured in the code is "home mode".
- To change the invocation name:
  1. Go to the "Build" tab in the Alexa Developer Console.
  2. Click on "Invocations" and then on "Skill Invocation Name".
  3. Enter the new desired invocation name and save the changes (test if this activation word can be used in the test tab).
  4. Rebuild the model (Build skill).

### Getting the `home_assistant_agent_id` of the ``voice conversational agent`` such as Home Assistant Assist, follow the instructions below:
- The `agent_id` can be found in the debug assistant for your target conversation agent:
  1. Go to **Settings** > **Voice assistants** > **OpenAI** (or the name you gave to the OpenAI assistant) > three dots menu > **Debug**.
  2. The `agent_id` will be displayed in the debug section.
  - See the following image for reference:
    ![Debug Assistant](https://community-assets.home-assistant.io/original/4X/5/9/c/59cad339a22cb65c63996f58e28d412f73a6d40f.png)

### To get the `home_assistant_agent_id` from your AI integration (if you are using one, such as Google AI or Open AI), follow the steps below::
- The `agent_id` is the ID of the generative AI entity:
  1. Go to **Settings** > **Devices & Services** > **Integrations** > **OpenAI Conversation** or **Google Generative AI** and you will see "1 service and 1 entity", click on the entity and the entity will be displayed in the **Entity ID** column.

### Publishing the Skill
1. After deploying the code in the **Code** tab, go back to the **Build** tab and click **Build skill**.
2. Test the Skill in the **Test** tab to ensure that the activation word and the skill are working correctly.

### Enabling automatic area recognition by AI
- The skill sends the device id (which is running the skill) in the Home Assistant conversational API call, then with a command instruction to the AI ​​and a label on the device, the AI ​​can associate the received device identifier with the device and locate which area it is in, to do this, follow the steps below:
  1. Enable Conversation API debug logging by adding the following setting to Home Assistant's `configuration.yaml`:
  - Enter the following information:
     ```txt
     logger:
       logs:
         homeassistant.components.conversation: debug
     ```
  2. Restart Home Assistant, start the skill from the desired echo device and give any command, the log will appear as below:
    ```txt
    2024-10-10 11:04:56.798 DEBUG (MainThread) [homeassistant.components.conversation.agent_manager] Processing in pt-BR: ligue a luz da sala. device_id: amzn1.ask.device.AMA***
     ```
  3. I took all the identifier that is after the device_id: `amzn1.ask.device.AMA***` and added a new label in the **echo device** through the `Alexa Media` Integration:
    ![Label on the echo device with the device ID received from the skill](images/echo_device_label.jpg)
  4. Update your preferred **AI command prompt** with the command below:
     ```txt
     If asked to perform an action and the area was not provided, use the label received in the command after the string "device_id:" to find the entity associated with the label and use the entity area to execute the command.
     ```

### Good luck!
Now you can use your Alexa Skill to integrate and interact with Home Assistant via the Assist Conversation API.
If you liked it, remember to send a **Thank you** to the developers.

<details><summary> 𝐂𝐫e𝐝𝐢𝐭s </summary>
<p>
   
To the [rodrigoscoelho](https://github.com/rodrigoscoelho), original developer of this skill.

</p>
</details>

# Skill Alexa que integra o Home Assistant Assist ou a sua IA Generativa de preferência através da API de conversação
Use o Home Assistant Assist ou a IA generativa na Alexa 😊

## INSTRUÇÕES

### Configurando o Home Assistant
- Crie/Ative uma API Home Assistant para seu usuário e obtenha um token de acesso de longa duração.

### Criando a Skill Alexa
1. Crie uma Skill Alexa-hosted (Python) na Alexa Developer Console:
   - **Name your Skill**: Escolha um nome de sua preferência (Ex: HomeAssist)
   - **Choose a primary locale**: Portuguese (BR)
   - **Tipo de experiência**: Other > Custom > Alexa-hosted (Python)
   - **Hosting region**: Pode deixar o padrão (US East (N. Virginia))
   - **Templates**: Clique em Import Skill
   - **Insira o endereço**: [https://github.com/fabianosan/skill-alexa-chatgpt4-assistpipeline-HomeAssistant.git](https://github.com/fabianosan/skill-alexa-chatgpt4-assistpipeline-HomeAssistant.git)
2. Vá na aba "Code"
3. Insira suas informações no arquivo `config.txt`:
   - Abra o arquivo `config.txt` no diretório raiz do projeto (/Skill Code/lambda/).
   - Insira as seguintes informações:
     ```txt
     home_assistant_url=https://SUA-URL-EXTERNA-DO-HOME-ASSISTANT/api/conversation/process
     home_assistant_token=SEU-TOKEN-DO-HOME-ASSISTANT
     home_assistant_agent_id=SEU-AGENT-ID
     home_assistant_language=pt-BR
     ```
   - **home_assistant_url**: URL externa da API de conversação do seu Home Assistant.
   - **home_assistant_token**: Token de acesso de longa duração do seu Home Assistant.
   - **home_assistant_agent_id**: ID do agente de conversação configurado no seu Home Assistant.
   - **home_assistant_language**: Idioma para chamar a API de conversação do Home Assistant.
4. Ainda no arquivo de configurações, altere as frases conforme sua vontade.
5. Salve as alterações.
6. Clique em Deploy.

### Configurando o ``Invocation Name``
- O nome de invocação padrão configurado no código é "casa inteligente".
- Para alterar o nome de invocação:
  1. Vá para a aba "Build" no Alexa Developer Console.
  2. Clique em "Invocations" e depois em "Skill Invocation Name".
  3. Insira o novo nome de invocação desejado e salve as alterações (teste se essa palavra de ativação pode ser usada na ABA de testes).
  4. Rebuild o modelo (Build skill).

### Obtendo o `home_assistant_agent_id` do assistente de voz, como o Assist do Home Assistant, siga as instruções abaixo:
- O `agent_id` pode ser encontrado no assistente de debug para o seu agente de conversação alvo: 
  1. Acesse **Settings** > **Voice assistants** > **OpenAI** (ou o nome que você deu ao assistente OpenAI) > menu de três pontos > **Debug**.
  2. O `agent_id` será exibido na seção de debug.
  - Veja a imagem a seguir para referência:
    ![Debug Assistant](https://community-assets.home-assistant.io/original/4X/5/9/c/59cad339a22cb65c63996f58e28d412f73a6d40f.png)

### Para obter o `home_assistant_agent_id` da IA generativa (se estiver utilizando uma, como Google AI ou Open AI), siga os passos abaixo:
- O `agent_id` é o ID da entidade de IA generativa: 
  1. Acesse **Configurações** > **Dispositivos & Serviços** > **Integrações** > **OpenAI Conversation** ou **Google Generative AI** e você verá "1 serviço e 1 enmtidade", clique na entidade e a entidade será exibida na coluna **ID da entidade**.
  
### Publicando a Skill
1. Após fazer o deploy do código na aba **Code**, volte para aba **Build** e clique em **Build skill**.
2. Teste a Skill na aba **Test** para garantir que a palavra de ativação e a skill estão funcionando corretamente.

### Ativando o reconhecimento de área automático pela IA
- A skill envia o device id (que está executando a skill) na chamada da API de conversação do Home Assistant, então com uma instrução de comando para a IA e um rótulo no dispositivo, a IA consegue associar o identificador dos dispositivo recebido ao dispositivo e localizar em qual área ele está, para isso, siga os passos abaixo:
  1. Ative o log de debug da API de conversação adicionando a seguinte configuração no `configuration.yaml` do Home Assistant:
  - Insira a seguinte informação:
     ```txt
     logger:
       logs:
         homeassistant.components.conversation: debug
     ```
  2. Reinicie o Home Assistant, inicie a skill pelo dispositivo echo desejado e dê qualquer comando, o log irá aparecer como abaixo:
    ```txt
    2024-10-10 11:04:56.798 DEBUG (MainThread) [homeassistant.components.conversation.agent_manager] Processing in pt-BR: ligue a luz da sala. device_id: amzn1.ask.device.AMA***
     ```
  3. Peguei todo o identificador que estiver após o device_id: `amzn1.ask.device.AMA***` e adicione um novo rótulo no **dispositivo echo** pela Integração `Alexa Media`:
    ![Rótulo no dispositivo echo com o device ID recebido da skill](images/echo_device_label.jpg)
  4. Atualize o **prompt de comando da IA** de sua preferência com o comando abaixo:
     ```txt
     Se solicitado para executar alguma ação e não informar a área do dispositivo, use o rótulo recebido no comando após a string "device_id:" para encontrar a entidade associada ao rotulo e use a área dessa entididade para executar o comando.
     ```

### Boa sorte!
Agora você pode usar sua Skill Alexa para integrar e interagir com o Home Assistant via Assist Conversation API.
Se gostou, lembre-se de mandar um **Obrigado** para o desenvolvedor.

<details><summary> 𝐂𝐫é𝐝𝐢𝐭os </summary>
<p>
   
Para o [rodrigoscoelho](https://github.com/rodrigoscoelho), quem iniciou o desenvolvimento desta skill.

</p>
</details>