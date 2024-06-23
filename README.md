# Gerenciamento de Comunidade

Este é um bot para Discord desenvolvido em Python utilizando a biblioteca `discord.py`. O bot é focado no gerenciamento de comunidade para um servidor de Project Zomboid. Futuramente, o bot terá funcionalidades exclusivas para aplicações no servidor dedicado do jogo, além de ser focado no gerenciamento administrativo do servidor Discord e na manutenção do servidor dedicado do jogo.

## Funcionalidades

- **Gerenciamento de Tempo de Voz**: O bot rastreia o tempo que os usuários passam em canais de voz e permite verificar esses dados.
- **Sistema de Votação**: Os usuários podem iniciar e participar de votações, com resultados mostrados no chat.
- **Futuras Funcionalidades**: Integrações exclusivas com o servidor dedicado do Project Zomboid para gerenciamento e manutenção.

## Pré-requisitos

Antes de começar, você precisará ter o seguinte instalado:

- Python 3.8 ou superior
- Pip (gerenciador de pacotes do Python)
- Biblioteca `discord.py`

## Instalação

1. Clone o repositório:

    ```sh
    git clone https://github.com/asafeamancio/discordpy.git
    cd discordpy
    ```

2. Crie e ative um ambiente virtual:

    ```sh
    python -m venv bot-env
    source bot-env/bin/activate  # No Windows use `bot-env\Scripts\activate`
    ```

3. Instale as dependências:

    ```sh
    pip install -r requirements.txt
    ```

4. Configure o arquivo `apikeys.py` com seu token do bot do Discord:

    ```python
    # apikeys.py
    BOTTOKEN = 'SeuTokenDoBotAqui'
    ```

## Uso

Para iniciar o bot, execute o seguinte comando:

```sh
python main.py
```
## Comandos Disponíveis
- `!check_time [user]`: Verifica o tempo de voz de um usuário.
- `!check_all_times`: Verifica o tempo de voz de todos os usuários.
- `!reset_voice_time`: Reseta todos os dados de tempo de voz (somente administradores).
- `!start_voting [users]`: Inicia uma nova sessão de votação com os usuários mencionados (somente administradores).
- `!end_voting`: Encerra a sessão de votação atual e exibe os resultados (somente administradores).
- `!pause_voting`: Pausa ou retoma a sessão de votação atual (somente administradores).
- `!vote [user]`: Vota em um usuário participante da votação.

## Estrutura do Projeto
```bash
discordpy/
│
├── apikeys.py             # Arquivo com o token do bot
├── bot.log                # Arquivo de log do bot
├── main.py                # Arquivo principal do bot
├── my_cog.py              # Cog com sistema de votação
├── requirements.txt       # Dependências do projeto
├── voice_time.db          # Banco de dados SQLite para tempo de voz
├── voting_data.db         # Banco de dados SQLite para sistema de votação
└── .gitignore             # Arquivos e pastas ignorados pelo Git
```
## Contribuição
1. Faça um fork do projeto.
2. Crie uma branch para sua feature (git checkout -b feature/nova-feature).
3. Commit suas mudanças (git commit -m 'Adiciona nova feature').
4. Push para a branch (git push origin feature/nova-feature).
5. Abra um Pull Request.

## Licença
Este projeto está licenciado sob a Licença AGPL v3.0. Veja o arquivo LICENSE para mais detalhes.

## Contato
Qualquer dúvida ou sugestão, sinta-se à vontade para entrar em contato!
```commandline
discord: asafeam
```