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
ansible-playbook ansible/init_env.yml --ask-become-pass
```

## run
```bash
pipenv shell
# it would pull lastest data and code for two repo
ansible-playbook ansible/setup_env.yml
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
# get the Magnificent 7 data
python run_job.py

# or param of file name inside the data/config/yfinance_nasdaq100.yml
python run_job.py yfinance_nasdaq100.yml
```
