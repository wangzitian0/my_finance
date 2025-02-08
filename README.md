# my_finance
try use script to get stock data

# how to run
## init
```bash
ansible-playbook init/install_neo4j.yml
ansible-playbook init/set_env.yml

```
## run
```bash
pipenv shell
./run.sh
```

## dev
```bash
# use this to keep env
pipenv install xxx

```
## data
```bash
datasette data/yfinance_data.db
```
