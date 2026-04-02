# Discord Bot

Bot de Discord con inteligencia artificial integrada y comandos de moderación.

**Bot desplegado en:** <https://discord-bot-rh78.onrender.com/>

## Características

- Inteligencia artificial con memoria conversacional por usuario
- Comandos de moderación (kick, ban, mute/unmute)
- Comandos de diversión (chistes, dados)
- Sistema de logs con base de datos
- Respuesta automática al mencionar al bot

## Instalación

### Requisitos

- Python 3.13.2+
- Base de datos PostgreSQL o MySQL

### Pasos

1. Clonar el repositorio:

```bash
git clone https://github.com/IsmelGabriel/discord-bot.git
cd discord-bot
```

1. Crear un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
```

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

1. Configurar variables de entorno:

```bash
DISCORD_TOKEN=tu_token_de_discord
OPENAI_API_KEY=tu_api_key_de_openai
# Configura también los detalles de la base de datos en el archivo `.env`
dbname=tu_nombre_de_base_de_datos
user=tu_usuario
password=tu_contraseña
host=tu_host
port=tu_puerto
```

1. Ejecutar el bot:

```bash
python bot.py
```

## Comandos

### Generales

- `=ping` - Muestra la latencia del bot

### IA

- `=ask <pregunta>` - Hace una pregunta al bot
- `=reset` - Borra la memoria de conversación
- `@<@bot_id> <mensaje>` - Menciona al bot para hablar con él

### Diversión

- `=chiste` - Cuenta un chiste aleatorio
- `=roll` - Lanza un dado de 6 caras

### Administración (requiere permisos)

- `=mute <usuario>` - Silencia a un usuario
- `=unmute <usuario>` - Quita el silencio a un usuario
- `=kick <usuario> [razón]` - Expulsa a un usuario
- `=ban <usuario> [razón]` - Banea a un usuario
- `=setprompt <prompt>` - Configura el prompt de IA del servidor

## Uso

Invita al bot a tu servidor y usa el prefijo `=` seguido del comando. Para hablar con la IA, menciona al bot o usa el comando `=ask`.

## Tecnologías

- discord.py
- OpenAI API
- Flask (webserver)
- PostgreSQL/MySQL
- Python 3
