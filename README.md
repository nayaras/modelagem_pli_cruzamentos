# TCC - Modelagem de otimização semafórica utilizando Programação Linear Inteira

Este projeto realiza a modelagem de um PLI para otimização da configuração semaórica utilizando o CPLEX. Para execução, a IBM disponibiliza uma API para Python através da biblioteca [Docplex](https://www.ibm.com/docs/en/icos/12.9.0?topic=docplex-python-modeling-api) disponível no [Pypi](https://pypi.org/project/docplex/). A documentação da biblioteca pode ser encontrada [aqui](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html).

## Pré-requisitos

1. Ter o Python 3.9 instalado
2. Ter o [Poetry](https://python-poetry.org/) instalado


## Como rodar

1. Clonar o projeto

2. Instalar as dependências através do comando:

```bash
poetry install
```

3. Executar o código:

```bash
poetry run tcc --linear-programming --caso-entrada <caso>
```

Note que o `<caso>` deve ser o nome da pasta dentro `entradas/` na raiz do projeto, por exemplo, um comando válido seria:

```bash
poetry run tcc --linear-programming --caso-entrada caso_1
```

