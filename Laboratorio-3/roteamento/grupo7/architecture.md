# Arquitetura da Rede - Grupo 7 (Topologia Tree)

```mermaid
graph TD
    R1[("R1<br/>127.0.0.1:5001<br/>10.0.1.0/24")]
    R2[("R2<br/>127.0.0.1:5002<br/>10.0.2.0/24")]
    R3[("R3<br/>127.0.0.1:5003<br/>10.0.3.0/24")]
    R4[("R4<br/>127.0.0.1:5004<br/>10.0.4.0/24")]
    R5[("R5<br/>127.0.0.1:5005<br/>10.0.5.0/24")]
    R6[("R6<br/>127.0.0.1:5006<br/>10.0.6.0/24")]
    R7[("R7<br/>127.0.0.1:5007<br/>10.0.7.0/24")]
    R8[("R8<br/>127.0.0.1:5008<br/>10.0.8.0/24")]
    R9[("R9<br/>127.0.0.1:5009<br/>10.0.9.0/24")]
    R10[("R10<br/>127.0.0.1:5010<br/>10.0.10.0/24")]
    R11[("R11<br/>127.0.0.1:5011<br/>10.0.11.0/24")]
    R12[("R12<br/>127.0.0.1:5012<br/>10.0.12.0/24")]

    %% Conexões da árvore
    R1 ---|Custo 1| R2
    R1 ---|Custo 2| R3
    
    R2 ---|Custo 1| R4
    R2 ---|Custo 2| R5
    
    R3 ---|Custo 1| R6
    R3 ---|Custo 2| R7
    
    R4 ---|Custo 1| R8
    R4 ---|Custo 2| R9
    
    R5 ---|Custo 1| R10
    R5 ---|Custo 2| R11
    
    R6 ---|Custo 1| R12

    %% Estilo para destacar a raiz
    classDef root fill:#ff9999
    classDef leaf fill:#99ff99
    classDef internal fill:#9999ff
    
    class R1 root
    class R7,R8,R9,R10,R11,R12 leaf
    class R2,R3,R4,R5,R6 internal
```

## Descrição da Topologia

Esta é uma topologia de **árvore** com 12 roteadores organizados em 4 níveis:

### Nível 1 (Raiz)
- **R1**: roteador raiz da árvore

### Nível 2 (Primeiro nível de filhos)
- **R2**: filho de R1 (custo 1)
- **R3**: filho de R1 (custo 2)

### Nível 3 (Segundo nível de filhos)
- **R4**: filho de R2 (custo 1)
- **R5**: filho de R2 (custo 2)
- **R6**: filho de R3 (custo 1)
- **R7**: filho de R3 (custo 2)

### Nível 4 (Terceiro nível de filhos - Folhas)
- **R8**: filho de R4 (custo 1)
- **R9**: filho de R4 (custo 2)
- **R10**: filho de R5 (custo 1)
- **R11**: filho de R5 (custo 2)
- **R12**: filho de R6 (custo 1)

## Características da Topologia

1. **Estrutura Hierárquica**: cada roteador tem no máximo um pai.
2. **Custos**: links com custos 1 e 2 para testar convergência.
3. **Sumarização**: toda estrutura para demonstrar.
4. **Convergência**: rápida, esperada em poucos ciclos.

## Comandos para Executar

Para testar esta topologia, execute os seguintes comandos em terminais separados:

```bash
# Terminal 1 - R1 (Raiz)
python roteador.py -p 5000 -f grupo7/R1.csv --network 10.0.1.0/24

# Terminal 2 - R2
python roteador.py -p 5000 -f grupo7/R2.csv --network 10.0.2.0/24

# Terminal 3 - R3
python roteador.py -p 5000 -f grupo7/R3.csv --network 10.0.3.0/24

# Terminal 4 - R4
python roteador.py -p 5000 -f grupo7/R4.csv --network 10.0.4.0/24

# Terminal 5 - R5
python roteador.py -p 5000 -f grupo7/R5.csv --network 10.0.5.0/24

# Terminal 6 - R6
python roteador.py -p 5000 -f grupo7/R6.csv --network 10.0.6.0/24

# Terminal 7 - R7
python roteador.py -p 5000 -f grupo7/R7.csv --network 10.0.7.0/24

# Terminal 8 - R8
python roteador.py -p 5000 -f grupo7/R8.csv --network 10.0.8.0/24

# Terminal 9 - R9
python roteador.py -p 5000 -f grupo7/R9.csv --network 10.0.9.0/24

# Terminal 10 - R10
python roteador.py -p 5000 -f grupo7/R10.csv --network 10.0.10.0/24

# Terminal 11 - R11
python roteador.py -p 5000 -f grupo7/R11.csv --network 10.0.11.0/24

# Terminal 12 - R12
python roteador.py -p 5000 -f grupo7/R12.csv --network 10.0.12.0/24
```
