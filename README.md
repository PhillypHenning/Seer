# Seer
Seer is a Dungeon Master tool to help DMs and players quickly find information about rules, stats, adventure details and information on hosted games.

Big thanks to 5e.tools, you guys absolutely rock!

# Setup
At minimum you will need an [OpenAI api key](https://platform.openai.com/api-keys).
If you want traceability you'll want to set up a [LangSmith account](https://smith.langchain.com/) and generate an api key

Keeps things clean with a virtual environment
```bash
python -m venv local
```

## Install
```bash
python -m pip install -r requirements.txt`
```

## Configure
Configuration is loaded from a `local_config.yml` file. Make a copy of the `config.yml` file and update the configuration as required. 



# Usage
```bash
source local/bin/activate
./_scripts/start.sh
```