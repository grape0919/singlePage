var conversationData = [
    {
      name: 'YeCard',
      avatar: null,
      messages: [
        {
          message: 'Oi Gabi, aqui é a Fernanda da YeCard!',
          sender: false
        },
        {
          message: 'Venho informar que a sua solicitação foi aprovada e seu cartão esta pronto para ser enviado.',
          sender: false
        },
        {
          message: 'Peço que finalize o envio dos documentos solicitados no nosso site para darmos sequência no envio.',
          sender: false
        },
        {
          message: '👏',
          sender: true
        },
        {
          message: 'Pronto! Enviei os documentos que estavam faltando...',
          sender: true
        },
        {
          message: 'Verifiquei aqui e está tudo certo!',
          sender: false
        },
        {
          message: 'Dentro do prazo de 5 dias úteis você receberá seu novo cartão.',
          sender: false
        },
        {
          message: '👍',
          sender: true
        },
        {
          message: 'Obrigada!',
          sender: true
        }
      ]
    },
    {
      name: 'Liberdade Seguros',
      avatar: null,
      messages: [
        {
          message: 'Parabéns, o seguro do seu veículo foi pré-aprovado!',
          sender: false
        },
        {
          message: 'A última etapa para aprovação do seu seguro é a vistoria.',
          sender: false
        },
        {
          message: 'Temos disponíveis três datas para realizar a vistoria do seu veículo.<br><br>Digite o número da data que melhor se encaixa em sua agenda:<br><br>1 - 20/03/2020<br>2 - 21/03/2020<br>2 - 22/03/2020',
          sender: false
        },
        {
          message: '2',
          sender: true
        },
        {
          message: 'Qual o melhor horário para você?<br><br>1 - 10:00<br>2 - 11:00<br>3 - 14:00<br>4 - 16:00',
          sender: false
        },
        {
          message: '3',
          sender: true
        },
        {
          message: 'Ótimo! Te aguardamos então no dia <b>21/03/2020</b> às <b>14:00</b>.',
          sender: false
        },
        {
          message: 'Nosso endereço é: Rua das Palmas, 253',
          sender: false
        },
        {
          message: 'Qualquer problema sinta-se livre para nos enviar uma mensagem por aqui.',
          sender: false
        }
      ]
    }
  ];
  
  var currentConversation = 0;
  
  var keyPressDelay = 20,
      betweenConversationDelay = 6000;
  
  var bannerConversation = $('.banner-conversation'),
      conversationHead = bannerConversation.find('.conversation-head'),
      conversationName = conversationHead.find('.name'),
      conversationWriting = conversationHead.find('.writing'),
      conversationContainer = bannerConversation.find('.conversation-container'),
      messageTemplate = $('<div class="message hidden"></div>');
  
  function scrollConversationToBottom(){
    conversationContainer.animate({
      scrollTop: conversationContainer.outerHeight()
    }, 400);
  };
  
  function checkIfIsEmoji(string){
    if(!isNaN(string)) {
      return false;
    }
    
    return Array.from(string.split(/[\ufe00-\ufe0f]/).join("")).length === 1;
  }
  
  function hideConversationWriting() {
    conversationWriting.animate({
      opacity: 0
    }, 200, function() {
      $(this).slideUp(200);
    });
  }
  
  function showConversationWriting() {
    conversationWriting.slideDown(200, function(){
      $(this).animate({
        opacity: 1
      }, 200);
    });
  }
  
  function executeConversation() {
    var delayTime = 0;
  
    var conversation = conversationData[currentConversation];
  
    conversationName.text(conversation.name);
  
    $.each(conversation.messages, function(messageIndex, message) {
      var newMessage = messageTemplate.clone();
  
      newMessage.html(message.message);
  
      if(message.sender) {
        newMessage.addClass('sender');
      }
  
      if(checkIfIsEmoji(message.message)) {
        newMessage.addClass('emoji');
      }
  
      var messageWriteDelay = message.message.length * keyPressDelay,
          messageBetweenDelay = Math.floor(Math.random() * (3000 - 1000) + 1000);
  
      delayTime += messageWriteDelay + messageBetweenDelay;
  
      // Esconde/exibe a mensagem de que o usuário está escrevendo
      setTimeout(function(){
        if(message.sender) {
          hideConversationWriting();
        } else {
          showConversationWriting();
        }
      }, delayTime - messageBetweenDelay);
  
      setTimeout(function(){
        conversationContainer.append(newMessage);
  
        scrollConversationToBottom();
  
        setTimeout(function(){
          newMessage.removeClass('hidden');
        }, 100);
      }, delayTime);
  
      if(conversation.messages.length === messageIndex + 1) {
        setTimeout(function(){
          hideConversationWriting();
        }, delayTime);
  
        delayTime += betweenConversationDelay
  
        setTimeout(function(){
          var messages = conversationContainer.find('.message');
  
          messages.css({
            opacity: 0
          });
  
          setTimeout(function(){
            messages.remove();
          }, 400);
  
          currentConversation += 1;
  
          if(!conversationData[currentConversation]){
            currentConversation = 0;
          }
  
          executeConversation();
        }, delayTime);
      }
    });
  }
  
  executeConversation();