Para que você consiga rodar um servidor para que dispositivos de outras redes possam escutar basta seguir o passo a passo

1. Vá no roteador que está na mesma rede que o computador executando o script Python, configure o redirecionamento de portas (port forwarding) para o endereço IP local do computador e a porta em que o servidor Flask está sendo executado (por padrão, a porta 5000).

- LOCAL
    - Endereço de ip: 192.168.0.70 (Você consegue essa informação executando "ipconfig" no seu terminal e acando essa linha "Endereço IPv4. . . . . . . .  . . . . . . . : 192.168.0.70")
    - Porta inicial: 5000 (porta onde o servidor Flask está sendo executado.)
    - Porta final: não coloque nada

- Externo
    - Porta inicial: 8080
    - Porta final: 8081
    - Protocolo: TCP

2. Descubra o endereço IP público da sua rede. Você pode usar serviços como "WhatIsMyIP", é com ele onde você vai conseguir acessar o servidor

3. Pronto, agora você já deve acessar o servidor de outra rede: http://endereco_ip_publico:5000 
