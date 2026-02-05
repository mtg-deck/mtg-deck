# **edhelper**

Uma ferramenta de linha de comando (CLI), Shell interativa e Editor Web para gerenciamento e análise de decks de *Magic: The Gathering* — focada no formato Commander (EDH).

O `edhelper` permite criar, modificar, validar, analisar e gerenciar seus decks diretamente do terminal ou através de uma interface web moderna.

---

## **📦 Instalação**

Como o projeto está em desenvolvimento, a instalação deve ser feita clonando o repositório e configurando o ambiente localmente.

### 1. Clonar o repositório
```bash
git clone https://github.com/mtg-deck/mtg-deck.git
cd mtg-deck
```

### 2. Configurar o Ambiente (Recomendado Python 3.12)
```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

---

## **🚀 Início Rápido**

Com o ambiente ativo, os comandos devem ser executados através do módulo principal do Python.

### Usando o Editor Web
Inicia o backend em FastAPI para suportar a interface React.
```bash
python -m edhelper.main start-editor
# O backend rodará em http://0.0.0.0:3839
```

### Usando a CLI
```bash
# Listar todos os decks salvos
python -m edhelper.main deck list

# Buscar cartas na API do Scryfall
python -m edhelper.main card search "Eriette"
```

### Usando a Shell Interativa (REPL)
```bash
python -m edhelper.main shell
```

---

## **🔧 Configuração**

### Autenticação
Antes de utilizar funcionalidades que dependem de chaves de API, você deve configurar suas credenciais:
```bash
python -m edhelper.main --set-key
```

### Informações do Sistema
```bash
# Verificar versão
python -m edhelper.main --version

# Ver metadados do projeto
python -m edhelper.main --info
```

---

## **📖 Funcionalidades**

### Gerenciamento de Decks
* Criar, deletar, renomear e clonar decks.
* Importação de listas via arquivos `.txt`.
* Exportação para formatos `.txt`, `.csv` ou `.json`.
* Definição automática de Comandantes.

### Operações de Cartas
* Busca inteligente via Scryfall API.
* Integração com EDHREC para análise de metagame e sugestões de cartas (synergy/inclusion).
* Visualização de estimativa de preços.

### Editor Web
* Interface intuitiva para construção de decks.
* Sincronização em tempo real com o banco de dados local.

---

## **🏗️ Arquitetura**

O projeto segue uma estrutura modular para facilitar a manutenção:
* `edhelper/` - Código fonte principal.
* `domain/` - Regras de negócio e entidades de Magic.
* `infra/` - Configurações de ambiente e persistência de dados.
* `external/` - Clientes de integração para APIs externas (Scryfall/EDHREC).

---

## **👥 Créditos**

* **Frontend**: Desenvolvido em React + Tailwind por [valentimdev](https://github.com/valentimdev).
* **Backend**: Desenvolvido por Joao utilizando FastAPI.
* **Assets**: Assets animados produzidos por Bianca Tavares.
