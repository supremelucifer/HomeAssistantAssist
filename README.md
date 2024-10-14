# Alexa Skill that integrates Home Assistant Assist or your preferred Generative AI via the conversation API and also allows you to open your favorite dashboard on Echo Show
* Use Home Assistant Assist or Generative AI on Alexa 😊
* Open your favorite dashboard on Echo Show!

## How it works

The skill accesses your Home Assistant instance through your public address (yes, you need an external address) ``https://your-homeassistant.com`` and uses the Home Assistant API/conversation/process:

```txt
https://your-external-homeassistant-url.com/api/conversation/process
```

As for the dashboard, it only works on devices with a screen, using the integrated Silk browser, Echo Show, and similar devices. You will need the identifier of the desired dashboard, as in the example below: "mushroom-mobile"

```txt
https://your-external-homeassistant-url.com/mushroom-mobile/0
```

When the skill is started on Echo Show, it opens a screen with a button to open, or depending on how you close the skill, it may also automatically open the dashboard on the screen.

***Note: Unfortunately, Amazon Silk does not support full screen at the moment, but if you have kiosk mode installed, what is below the address bar will display in "full screen."***

## Installation

For instructions how to set this skill up refer to the [installation](doc/en_INSTALLATION.md) page.

---------------------------------------------------------------------------------

# Skill Alexa que integra o Home Assistant Assist ou a sua IA Generativa de preferência através da API de conversação e também permite abrir seu dashboard preferido na echoshow
* Use o Home Assistant Assist ou a IA generativa na Alexa 😊
* Abra seu dashboard preferido na echoshow!

## Como a skill funciona

A skill acessa sua instância do Home Assistant através do seu endereço público (sim, você precisa de um endereço externo) ``https://seu-homeassistant.com`` e utiliza a API/conversation/process do Home Assistant:

```txt
https://sua-url-externa-homeassistant.com/api/conversation/process
```

Já o dashboard, só funciona em dispositivos com tela, utilizando o navegador Silk integrado, echoshow e derivados e você precisa do identificador do dashboard desejado, no exemplo abaixo, é o: "mushroom-mobile"

```txt
https://sua-url-externa-homeassistant.com/mushroom-mobile/0
```

Quando a skill é iniciada na echoshow abre uma tela com um botão para abrir, ou dependendo de como encerrar o uso da skill, ela também abre automaticamente o dashboard na tela. 

***Nota: Infelizmente o Amazon Silk não suporta tela cheia no momento, mas se você tiver o kioskmode instalado, o que está abaixo da barra de endereços exibirá em "tela cheia".***

## Instalação

Siga as instruções em como criar a skill na página de documentação de [instalação](doc/pt_INSTALLATION.md).