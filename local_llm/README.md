# Local LLM

## Ollama
### intro
https://github.com/ollama/ollama
### find the models
https://ollama.com/library
### .e.g
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run deepseek-coder-v2:16b 
```
## open-ui
```bash
# it would auto install https://github.com/open-webui/open-webui
pipenv install --dev
# you can access at http://localhost:8080
open-webui serve

```