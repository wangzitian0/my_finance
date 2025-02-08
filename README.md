# my_finance
try use script to get stock data

# how to build env
## init
```bash
# go to your workspace
git clone git@github.com:wangzitian0/my_finance.git
cd my_finance
pip install pipenv
pipenv shell
# might need sudo permission
ansible-playbook init/init_env.yml --ask-become-pass
```

## run
```bash
pipenv shell
ansible-playbook init/setup_env.yml
# exit the pipenv
exit
# if you need the interpreter like pycharm by
which python
```

## dev
```bash
# use this to keep env
pipenv install xxx
```

# how to run
## fetch the data
```bash
python run_job.py
```
