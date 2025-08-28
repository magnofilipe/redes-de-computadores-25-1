# Implementando o Protocolo de Roteamento Vetor de Distância

Nesta atividade, vocês implementarão um dos algoritmos que movem a internet: o **Vetor de Distância (Distance Vector)**. Este é o algoritmo que serviu de base para protocolos reais como o **RIP (Routing Information Protocol)**.

Nosso objetivo é construir um "roteador" em Python que seja capaz de descobrir a topologia de uma rede e tomar decisões inteligentes sobre o melhor caminho para encaminhar dados, tudo isso através da troca de mensagens com seus vizinhos. Para tornar o desafio ainda mais interessante e realista, vocês também implementarão uma técnica de otimização: a **sumarização de rotas**.

Cada grupo irá trabalhar em no seu roteador, utilizando o código base em Python. Este roteador é, na verdade, um servidor web implementado com a biblioteca Flask.

*   **Comunicação:** Em vez de pacotes em nível de bits, nossos roteadores se comunicarão trocando informações de rota através de uma API REST simples (usando requisições HTTP).
*   **Topologia:** A configuração da rede (quem são os vizinhos de cada roteador e o "custo" do link para alcançá-los) será definida em arquivos de configuração `.csv` e `json` externos. Isso nos permite simular qualquer topologia de rede que quisermos.
*   **Algoritmos:**  Utilizaremos algoritmo de Bellman-Ford para atualizar as rotas e a lógica de sumarização para otimizar os anúncios.


**Toc**:
> 1. [A Estrutura do Roteador](#a-estrutura-do-roteador)
>    - [O Formato da Mensagem](#o-formato-da-mensagem-de-atualização)
> 1. [Roteiro de Implementação](#seu-roteiro-de-implementação)
> 1. [Cenário de Exemplo](#cenário-de-exemplo)
> 1. [Desafios de Implementação](#desafios-de-implementação)
> 1. [Avaliação](#avaliação)
>    - ⚠️ [Datas dos entregaveis](#resumo-entregaveis)


## A Estrutura do Roteador

Vocês receberão um código Python base com parte de inicialização do servidor e leitura dos arquivos. O seu roteador terá dois *endpoints* (rotas) para troca de informação com o mundo externor:

*   `POST /receive_update` (**Metodos de atualização**): Esta é a rota que escuta as mensagens de atualização dos roteadores vizinhos. A maior parte da lógica do Vetor de Distância será implementada aqui.
*   `GET /routes`: Vocês implementarão esta rota. Ela serve como uma "janela" para o estado interno do seu roteador, exibindo a tabela de roteamento atual em formato JSON. Servindo como uma ferramenta de depuração.

Em suma, o metodo `/receive_update`, recebera a notificação sempre que um roteador vizinho tiver a sua tabela de roteamento atualizada.

> ⚠️ Lembrando que esses metodos serão utilizados utilizados por outros grupos e devem ser implementados com as assinaturas padrões. 

### O Formato da Mensagem de Atualização

Para que a comunicação funcione entre todos os grupos, é **importante** que as mensagens de atualização trocadas sigam um formato padrão. Qualquer desvio fará com que seu roteador não seja compatível com os outros.

Toda requisição `POST` enviada para `/receive_update` deve ter um corpo em JSON com a seguinte estrutura:

```json
{
  "sender_address": "127.0.0.1:5001",
  "routing_table": {
    "10.0.2.0/24": { "cost": 0, "next_hop": "10.0.2.0/24" },
    "10.0.1.0/24": { "cost": 1, "next_hop": "127.0.0.1:5000" },
    "10.0.3.0/24": { "cost": 2, "next_hop": "127.0.0.1:5002" }
  }
}
```

*   `sender_address` (string): O endereço e a porta do roteador que enviou a mensagem. Você usará isso para saber de qual vizinho a atualização veio e qual o custo do link direto para ele.
*   `routing_table` (objeto): Um objeto que representa a tabela de roteamento do remetente.
    *   As **chaves** são as redes de destino (strings no formato "ip/prefixo").
    *   Os **valores** são outro objeto com duas chaves: `cost` (um número) e `next_hop` (uma string).


> Repare que o curso zero ("cost": 0) indica que a rede esta diretamente conectada ao roteador!


Para testar que sua menssagem esta funcionando vocês podem utilizar o comnado curl abaixo (testado no linux).

```bash
curl -X POST http://localhost:5001/receive_update \
  -H "Content-Type: application/json" \
  -d '{
    "sender_address": "127.0.0.21:5021",
    "routing_table": {
      "10.0.2.0/24": { "cost": 0, "next_hop": "10.0.2.0/24" },
      "10.0.1.0/24": { "cost": 1, "next_hop": "127.0.0.1:5000" },
      "10.0.3.0/24": { "cost": 2, "next_hop": "127.0.0.1:5002" }
    }
  }'
```


## Roteiro de Implementação

O código-base fornecido contém comentários `TODO:` onde vocês podem adicionar sua lógica, lembrando que o local do comentario é um sugestão vocês podem alterar o codigo como desejarem. Segue a recomendação de passos de implementação:

**Passo 1: Inicialize sua Tabela de Roteamento**

No método `__init__` da classe `Router`, sua primeira tarefa é criar e popular a tabela de roteamento. Ela deve conter:
1.  A rota para a rede que seu roteador administra diretamente (vinda do argumento `--network`). O custo para uma rede diretamente conectada é **0**.
2.  As rotas para seus vizinhos diretos (vindos do arquivo `.csv`). O custo é o custo do link, e o `next_hop` é o próprio endereço do vizinho.

**Passo 2: Receba e Processe Atualizações (Lógica de Bellman-Ford)**
No método `receive_update`, você implementará o coração do algoritmo.
1.  Extraia a `sender_address` e a `routing_table` do JSON recebido.
2.  Para cada rota na tabela recebida, calcule o novo custo para chegar àquele destino passando pelo remetente, por exemplo: `novo_custo = custo_do_link_direto + custo_reportado_pelo_vizinho`.
    - Para mais detalhes vejam os livros da disciplina
3.  Compare o `novo_custo` com o custo que você já tem (se tiver) para o mesmo destino. Se o novo caminho for mais barato (ou se for um destino que você não conhecia), atualize ou adicione a rota à sua tabela.

**Passo 3: Envie Atualizações com Sumarização de Rotas (O Grande Desafio)**
No método `send_updates_to_neighbors`, você não apenas enviará sua tabela, mas a enviará de forma otimizada.
1.  **Crie uma cópia** da sua tabela de roteamento para não modificar a original. Receomendo aplicar a lógica de sumarização nesta cópia.
2.  **Lógica de Sumarização (sem bibliotecas!):** O objetivo é encontrar rotas na sua tabela que possam ser agregadas.
    *   **Condição Principal:** Duas redes só podem ser sumarizadas se tiverem o **mesmo `next_hop`**.
    *   **Implementação:** Vocês precisarão criar uma função auxiliar que recebe duas redes (ex: '192.168.20.0/24' e '192.168.21.0/24') e determina se são agregáveis. Vocês não podem utilizar bibliotecas, vocês devem implentar utilizando ferramentas basicas do python.Sugestão:
        - a.  Converter a parte do IP de cada rede em um número inteiro de 32 bits. <!-- utilizar IPv6 no futuro -->
        - b.  Verificar se os prefixos de rede são adjacentes e do mesmo tamanho.
        - c.  Calcular a nova super-rede e seu prefixo (ex: '192.168.20.0/23') usando operações de bits (AND, OR, XOR).
    *   Se encontrar rotas sumarizáveis, remova as entradas específicas da **cópia** da tabela e adicione a nova rota sumarizada. O custo da rota agregada deve ser o **maior** custo entre as rotas originais.
3.  **Envio:** Itere sobre seus vizinhos e envie a tabela **copiada e sumarizada** em uma requisição `POST`, ja disponvel do no codigo exemplo.

**Passo 4: Crie o endpoint de visualização**

Implemente a rota `GET /routes` para que ela simplesmente retorne a `self.routing_table` atual do seu roteador em formato JSON. Use `curl http://127.0.0.1:5000/routes` para testar.

> O código base tem um exemplo, mas deve ser alterado pra exibir a tabela de roteamento! Verifique o comentario com os campos que devem ser mantigos obrigatoriamente!


## Cenário de exemplo

Para desenvolver e testar seu roteador, usaremos uma topologia clássica de triângulo com três roteadores (A, B e C). Configuramos os custos dos links de forma assimétrica para forçar o algoritmo a trabalhar e encontrar o melhor caminho, que nem sempre é o mais óbvio.

```mermaid
graph 
    subgraph Topologia de Teste
        A((Roteador A <br> 10.0.0.0/24))
        A ---|Custo 1| B((Roteador B <br> 10.0.1.0/24))
        B ---|Custo 2| C((Roteador C <br> 10.0.2.0/24))
        C ---|Custo 10| A
    end
```

A rota direta entre A e C tem um custo alto (10). A rota alternativa, passando por B (A -> B -> C), tem um custo total de 3 (1 + 2). Seu roteador deverá ser capaz de descobrir que este segundo caminho é o melhor.

O exemplo esta na pasta [exemplo](./exemplo/), nela você encontra arquivo `csv` com os vizinhos de cada roteador. Por exemplo, o arquivo [config_A.csv](./exemplo/config_A.csv) tem os vizinhos de A. Nesse arquivo csv você tem dois campos o $vizinho$ e $custo$. Repare que o vizinho tem o par IP/porta para comunicação.

```csv
vizinho,custo
127.0.0.1:5001,1
127.0.0.1:5002,10
```

Na pasta [exemplo](./exemplo/), vocês encontraram um arquiov [topologia.json](./exemplo/topologia.json), que descreve a topologia em um json, o formato desse arquivo é explicado na secção [abaixo](#parte-2-teste-de-interoperabilidade-em-laboratório).

Para iniciar o cenario teste vocês devem executar o seguinte comando em seu computdaor.

**Para iniciar este cenário, abra três terminais separados e execute os seguintes comandos:**

*   **Terminal 1 (Roteador A):**
    ```bash
    python roteador.py -p 5000 -f exemplo/config_A.csv --network 10.0.0.0/24
    ```
*   **Terminal 2 (Roteador B):**
    ```bash
    python roteador.py -p 5001 -f exemplo/config_B.csv --network 10.0.1.0/24
    ```
*   **Terminal 3 (Roteador C):**
    ```bash
    python roteador.py -p 5002 -f exemplo/config_C.csv --network 10.0.2.0/23
    ```

No trecho acima, que simula o exemplo, o parâmetro `--network` define a sub-rede de hosts que cada roteador anuncia e para a qual encaminha pacotes, que tambem esta definido no arquivo `topologia.json`. Em outras palavras, é a faixa de IPs dos dispositivos finais sob sua responsabilidade de roteamento.

No exemplo abaixo, os três roteadores trocam informações de controle em uma rede dedicada (por exemplo `192.168.112.0/24`), enquanto anunciam e encaminham datagramas IP para as sub-redes de usuários (`10.0.0.0/8` e `172.16.0.0/16`):

```mermaid
graph LR
    subgraph RedeDeRoteadores["Rede de Roteadores – 192.168.112.0/24"]
        rede
        A((Roteador A <br> 192.168.112.1))
        B((Roteador B <br> 192.168.112.10))
        C((Roteador C <br> 192.168.112.13))

        A ---|Custo 1| B
        B ---|Custo 2| C
        C ---|Custo 10| A
    end

    subgraph RedesEncaminhadas1["Redes Encaminhadas"]
        HA["10.0.0.0/24"]
    end
    subgraph RedesEncaminhadas2["Redes Encaminhadas"]
        HB["10.0.1.0/24"]
    end
    subgraph RedesEncaminhadas3["Redes Encaminhadas"]
        HC["10.0.2.0/24"]
        HD["10.0.3.0/24"]
        HE["172.16.2.0/24"]
    end

    A -.-> HA
    B -.-> HB
    C -.-> HC
    C -.-> HD
```

No exemplo temos:

- A rede 192.168.112.0/24 destina-se exclusivamente à troca de mensagens de roteamento entre os roteadores, como as menssagens que vocês enviaram no laboratorio.
  - Cada roteador recebe um IP nessa sub-rede que serve apenas ao tráfego de controle (updates, etc.).
- Essa é uma prática comum em redes reais: separar a rede de roteamento da rede dos usuários para garantir maior organização e segurança.
- As redes anunciadas (`10.0.X.0/Y` e `172.16.X.0/Y`) correspondem às sub-redes de hosts finais. Cada roteador sabe como direcionar pacotes até esses destinos.



## Desafios de Implementação

Durante a avaliação, você terão dois desafios adicionais:

**a. Sumarização para redes não contíguas** (`Obrigatorio`)

No laboratório, você sumariza apenas redes adjacentes e do mesmo prefixo.  

Observe que no exemplo do laboratorio foi adicionado o `Roteador X`, que deve receber as rodas sumárizadas de A.

```mermaid
graph 
    subgraph Exemplo de sumarização
        X((Roteador X <br> 192.168.1.0/24))
        A((Roteador A <br> 10.0.0.0/24))
        X === | x | A
        A ---|Custo 1| B((Roteador B <br> 10.0.1.0/24))
        B ---|Custo 2| C((Roteador C <br> 10.0.2.0/23))
        C ---|Custo 10| A
    end
```
- **DESAFIO:** Implemente uma estratégia para identificar e resolver casos de sumarização possíveis.
    - Repare que a sumarização é feita **por destino** (ou por host), pois o roteador `A` envia uma rota sumarizada para o roteador `X`. Isso reduz o número de anúncios e simplifica o entendimento global da topologia.
        - Para os roteadores `B` e `C`, não é necessário aplicar a sumarização, já que estão diretamente conectados a `A`, e o detalhamento das rotas ajuda a manter a precisão na decisão de encaminhamento.
    - Nessa implementação, não se preocupe com a **otimização da sumarização**, ou seja, você pode utilizar uma máscara **maior do que o necessário**, contanto que ainda inclua as redes desejadas. 
        - Por exemplo: se os roteadores `A`, `B` e `C` estão conectados às redes `10.0.1.0/24`, `10.0.2.0/24` e `10.0.3.0/24`, seria possível criar uma sumarização utilizando a máscara `/22`, gerando o prefixo `10.0.0.0/22`.
        - No entanto, caso você utilize uma máscara ainda maior — como `/21` (`10.0.0.0/21`) — essa sumarização incluiria também os intervalos `10.0.4.0/24` até `10.0.7.255`, que **não pertencem à rede atual**, tornando a sumarização imprecisa e perigosa para o roteamento.
        - **Contudo vocês não podem considerar redes superdimencionadas (/8)**, apenas para casos quando a não for possivel (em razão da potencia de 2), ter uma quebra exata.
    - Portanto, é importante identificar o **maior prefixo comum possível** que não incorra em sobreposição indevida com redes que não existem ou não devem estar incluídas.

> 📌 Sugestão implementem o cenario a cima - criem arquivos de configurações e executem os roteadores - para testar a sumarização das rotas! 


<!-- **b. Implementando Split Horizon ou Poisoned Reverse** (`Extra`)

Essas são técnicas clássicas para mitigar o problema de contagem ao infinito.  
- **TAREFA:** Pesquise na literatura sobre "split horizon" e/ou "poisoned reverse".
- **DESAFIO:** Implemente uma dessas técnicas no seu roteador.  
    - Ao enviar suas atualizações para um vizinho, evite anunciar para ele rotas que utiliza ele próprio como próximo salto.
- **EXPERIMENTE:** Repita o teste do desafio anterior e compare os resultados! -->



<!-- ### 4. **Visualização Gráfica da Tabela de Roteamento**
- **TAREFA:** Utilize alguma biblioteca de visualização (por exemplo, Matplotlib, Plotly ou Graphviz) para criar um pequeno script que gere um diagrama (grafo) da tabela de roteamento do seu roteador em tempo real.
- **DESAFIO:** Gere snapshots após cada ciclo de atualização e veja como a convergência acontece visualmente! -->

<!-- ### 5. **Simulação de Rede Maior**
- **TAREFA:** Crie arquivos de configuração simulando uma rede com 5 ou mais roteadores, formando uma malha, anel ou topologia de sua escolha.
- **DESAFIO:** Verifique quanto tempo (número de ciclos) a rede leva para convergir. Compare os resultados performando sumarização versus sem sumarização. -->



## Avaliação

A avaliação será dividida em duas partes, testando diferentes aspectos do seu projeto.

### Parte 1: Demonstração com uma captura de tráfego

Nesta etapa, seu grupo deverá responder duas questões:

**Questão 1**: Configurar um cenário com três roteadores operando na rede local do laboratório. Substituam o IP de loopback padrão (`127.0.0.1`) pelos endereços IP reais das máquinas de cada integrante do grupo (por exemplo: `192.168.10.23`).

📌 **Objetivos a serem demonstrados**:

- Validar que a rede está **convergindo corretamente**, com todos os roteadores alcançando estabilidade nas informações de roteamento.
- Comprovar que as **tabelas de roteamento** estão atualizadas e compatíveis com a topologia definida.
- Utilizar o [**Wireshark**](./wireshark_tutorial.md) para **capturar o tráfego** de troca de informações entre os roteadores, gerando um arquivo `.pcap` contendo:
  - Requisições HTTP `POST` transmitidas entre os dispositivos.
  - Atualizações de rota representadas em formato JSON no corpo das mensagens.

📄 **Entrega obrigatória**:

No formulário da tarefa (disponível no Google Sala de Aula), cada grupo deverá anexar:

1. O **arquivo de captura** gerado pelo Wireshark (`.pcap`), contendo os pacotes relevantes.
2. Um **PDF com evidências**, incluindo capturas de tela do Wireshark acompanhadas de **legendas explicativas**, identificando:

   - 🟩 **Estado inicial** da tabela de roteamento de um dos roteadores.
   - 🟨 **Mensagem de atualização** (requisição HTTP POST com JSON).
   - 🟥 **Estado final** da tabela após o recebimento e processamento da atualização, do roteador que você exibiu o estado inicial.


**Questão 2**: Simulação de falha e análise da convergência, nesta questão, seu grupo deverá realizar um experimento provocando a falha de um dos roteadores em uma topologia triangular, simulando o cenário clássico de contagem ao infinito.

📌 **Procedimentos**:
- Encerre abruptamente o processo do `roteador` de um dos nós do triângulo para simular a falha.
    - dica coloque um sleep de alguns segundos antes de enviar a atualização dos vizinhos
- Observe o comportamento dos dois roteadores restantes após essa interrupção.

📎 **Objetivos a serem demonstrados**:
- Analisar o que ocorre nas tabelas de roteamento dos roteadores ativos quando o destino se torna inacessível.
- Verificar **quantos ciclos** de atualização são necessários até que a rede reconheça e remova o destino perdido.
- Identificar se o protocolo implementado possui mecanismos para evitar o crescimento indefinido das métricas - por exemplo, limite de hop count.

📄 **Entrega obrigatória**:
No formulário da tarefa (no Google Sala de Aula), cada grupo deve incluir:

1. O **arquivo de captura Wireshark (.pcap)** contendo os pacotes trocados durante o experimento, limitado a 1MB.
1. Explique por que o problema de contagem ao infinito ocorre no algoritmo de **distância-vetor**, relacionando com o experimento realizado.  
    - Discuta possíveis técnicas de mitigação como *Split Horizon*, *Route Poisoning*, *Hold-down Timers*, mesmo que não estejam implementadas.  
    - Avalie como essas técnicas poderiam evitar a demora na convergência.
    - A entrega deve ser um arquivo `.pdf`.

## Parte 2: Teste de Interoperabilidade em Laboratório

Para a etapa final da avaliação, faremos um teste ao vivo em sala de aula. Para tal, 

> a.  Cada equipe receberá um novo arquivo de configuração que conectará seu roteador aos roteadores de outras equipes, formando uma grande rede.
> b.  Seu roteador deverá ser capaz de trocar rotas com sucesso com implementações de outros colegas, aprender sobre toda a topologia da sala e convergir para as rotas corretas.

Contudo, esses cenários serem criados por vocês, cada grupo deve **elaborar e documentar** um projeto de rede com **12 roteadores**.  A ideia é criar redes variadas — por exemplo, malha completa, anel duplo, estrela, árvore ou topologias híbridas — de modo que possamos testar cenários realistas de escalabilidade, convergência e sumarização. As topologias propostas devem ser relevantes para laboratório e podem incluir, mas não se limitam a:  
  - Malha , ao menos 50% do reoteadores devem estar conectados entre si
  - Anel duplo (Dual Ring), no minimo 2 aneis (podem ter mais)
  - Estrela (Star), no minimo duas estrelas 
  - Árvore (Tree), utilizar roteadores em arvores
  - Híbrida (no minimo, duas redes em malha ligada anel)  

Abaixo segue uma planilha sugerida para distribuir as topologias entre os 12 grupos. Sintam-se livres para reordenar ou repetir topologias conforme a dinâmica da turma.

| Grupo   | Topologia          |
|---------|--------------------|
| Grupo 1 | Malha          |
| Grupo 2 | Malha          |
| Grupo 3 | Dual Ring          |
| Grupo 4 | Dual Ring          |
| Grupo 5 | Star               |
| Grupo 6 | Star               |
| Grupo 7 | Tree               |
| Grupo 8 | Tree               |
| Grupo 9 | Malha               |
| Grupo 10| Dual Ring          |
| Grupo 11| Híbrida             |
| Grupo 12| Híbrida             |


### Entrega do Cenário

Cada grupo deverá montar **um cenário com 12 roteadores**, no google sala de aula, utilizando uma das topologias indicadas. O resultado será entregue em um único arquivo `.zip`, com a seguinte estrutura:

```
GrupoX.zip
├── architecture.png        # Diagrama da rede
├── topologia.json          # Descrição da topologia em json  
├── R1.csv                  # Configuração do roteador 1
├── R2.csv
├── ...
├── R12.csv                 # Configuração do roteador 12
└── captura.pcap            # Captura Wireshark até a convergência
```

O que cada item deve conter:

- architecture.png
  - Diagrama da rede com os 12 roteadores nomeados (R1 a R12)
  - Mostrar quais roteadores estão conectados entre si e os custos de cada link
  - Pode ser feito com Mermaid, Graphviz, ou desenhado à mão (desde que legível)
-   `topologia.json` :  Este arquivo é o **manifesto da sua rede**. Ele descreve cada roteador, associando sua identidade (nome, endereço, rede) ao seu arquivo de configuração de vizinhos. Enquanto os arquivos `.csv` definem as conexões *de um roteador*, o `topologia.json` descreve a rede *completa*, permitindo a automação de testes e visualizações.
    - A estrutura é uma lista (um array `[]`) de objetos `{}`, onde cada objeto representa um roteador e contém os seguintes atributos:
    ```json
    [
        {
            "name": "Router A",
            "network": "10.0.0.0/24",
            "address": "127.0.0.1:5000",
            "config_file": "exemplo/config_A.csv"
        },
        {
            "name": "Router B",
            "network": "10.0.1.0/24",
            "address": "127.0.0.1:5001",
            "config_file": "exemplo/config_B.csv"
        }
    ]
    ```
    - Cada atributo tem a função:
      - `"name"`: Um nome amigável e legível para o roteador (ex: "RouterA", "R1"). É usado para identificação dos roteadores.
      - `"network"`: A sub-rede que este roteador administra diretamente, no formato "ip/prefixo". Esta é a informação que seu roteador usará para criar a primeira entrada em sua tabela de roteamento (com custo 0).
      - `"address"`: O endereço `ip:porta` onde o servidor Flask do roteador irá escutar por conexões. Utilizado para outros roteadores se conectarem.
      - `"config_file"`: O caminho para o arquivo `.csv` que contém a lista de vizinhos deste roteador. 
- R1.csv até R12.csv
  - Arquivo para cada roteador
  - Nome no formato `R<N>.csv` (ex: `R3.csv`)
  - Conteúdo: lista de vizinhos e custos
    ```
    neighbor_address,cost
    192.168.0.1:5000,1
    192.168.0.2:5000,2
    ```
  - **⚠️ Importante** utilizem o rede `192.168.0/24` para a no arquivo a ser entregue.
    - O ultimo octeto do ip tera o mesmo indice do roteador. 
        - Por exemplo o roteador `R1` terá o ip `192.168.0.1`, enquanto o `R12` tera o ip `192.168.0.12`
    - Utilize a porta padrão `5000`
  - Veja o exemplo da seção CSV no material da atividade
  - Os dados devem ser enviados serguindo essa regra o envio não conforme decresce em 2 pontos a nota do grupo.

- **convergence.pcap**  
  - `Teste o cenário antes de enviar`: execute os roteadores e capture o tráfego até a convergência
  - Captura de tráfego feita com Wireshark
  - Deve registrar a troca de mensagens entre os roteadores até que todas as rotas estejam estáveis

⚠️ Lembretes importantes

- Teste o cenário antes de enviar: execute os roteadores e capture o tráfego até a convergência
- Compacte os arquivos **sem subpastas**, todos diretamente na raiz do `.zip`
- Nome do arquivo ZIP deve ser `scenario_GrupoX.zip` (substitua X pelo número do seu grupo)
- Na pasta [exemplo](./exemplo/), você encontram exemplos com a [topologia.json](./exemplo/topologia.json) e a configuração da vizinhança dos roteadores (arquivos csv).

### Resumo Entregaveis

No dia __/08/2025 deverão ser entregues todos os arquivos no formulário do Google Classroom:  
https://classroom.google.com/  

**Parte 1**
- [ ] Entregavel 1:  
  - `.pcap` (captura Wireshark)  
  - PDF de evidências (tabelas de roteamento e POST/JSON)  
- [ ] Entregavel 2:  
  - `.pcap` (≤ 1 MB)  
  - PDF com a esplicação dacontagem ao infinito e técnicas de mitigação
- [ ] Entregavel 3 – `zip` com o cenário de 12 roteadores:  
  - `architecture.png`  
  - `topologia.json`  
  - `R1.csv` … `R12.csv`  
  - `captura.pcap`

**Parte 2**
Laboratorio no dia __/08/2025
