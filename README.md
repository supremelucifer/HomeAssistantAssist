# Alexa Skill that integrates Home Assistant Assist or your preferred Generative AI via the conversation API and also allows you to open your favorite dashboard on Echo Show
* Use Home Assistant Assist or Generative AI on Alexa 😊
* Open your favorite dashboard on Echo Show!

## How it works

The skill accesses your Home Assistant instance through your public address (yes, you need an external address) https://your-homeassistant.com and uses the Home Assistant conversation/process API. So, whatever you can do via Assist (the configured voice agent), you can also do through the skill, but using Alexa as the voice input and output. Cool, right?

```txt
https://your-external-homeassistant-url.com/api/conversation/process
```

Here’s the translation to en-US:

Additionally, screen devices like Echo Show and similar allow you to open your preferred Home Assistant dashboard on the screen, either by clicking the **Open Home Assistant** button on the screen or when you end the use of the skill. In the example of the URL below, you need to configure the identifier: `mushroom-mobile` in the skill’s configuration file:

```txt
https://your-external-homeassistant-url.com/mushroom-mobile/0
```

***Note: Unfortunately, Amazon Silk does not support full screen at the moment, but if you have kiosk mode installed, what is below the address bar will display in "full screen."***

## Installation

For instructions how to set this skill up refer to the [installation](doc/en_INSTALLATION.md) page.

---------------------------------------------------------------------------------

# Skill Alexa que integra o Home Assistant Assist ou a sua IA Generativa de preferência através da API de conversação e também permite abrir seu dashboard preferido na echoshow
* Use o Home Assistant Assist ou a IA generativa na Alexa 😊
* Abra seu dashboard preferido na echoshow!

## Como a skill funciona

A skill acessa sua instância do Home Assistant através do seu endereço público (sim, você precisa de um endereço externo) ``https://seu-homeassistant.com`` e utiliza a API `conversation/process` do HA, então que você fazer via Assist (o agente de voz configurado) você consegue fazer pela skill, porém utilizando a Alexa como entrada e saída de voz, lega né?

```txt
https://sua-url-externa-homeassistant.com/api/conversation/process
```

Além disso, dispositivos como tela, como echoshow e derivados permitem abrir o seu dashboard preferido do Home Assistant na tela, seja clicando no botão **Abrir Home Assistant** na tela ou na hora que você encerra o uso da skill. No exemplo da URL abaixo, é necessário configurar o identificador: `mushroom-mobile` no arquivo de configurações da skill:

```txt
https://sua-url-externa-homeassistant.com/mushroom-mobile/0
```

***Nota: Infelizmente o Amazon Silk não suporta tela cheia no momento, mas se você tiver o kioskmode instalado, o que está abaixo da barra de endereços exibirá em "tela cheia".***

## Instalação

Siga as instruções em como criar a skill na página de documentação de [instalação](doc/pt_INSTALLATION.md).