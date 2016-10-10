COLORED_LOGS_LEVEL	:= DEBUG
PYTHONPATH		:= $(shell pwd):$(echo $$PYTHONPATH)
AWS_ACCESS_KEY_ID	:= WrBawPM5tsVH6WeM3rFh
AWS_SECRET_ACCESS_KEY	:= BLXMIIEeXb1zaT5RqrHHkP_w09L3Shol2jv5rBk_
export COLORED_LOGS_LEVEL
export PYTHONPATH

.PHONY: migrations static

all: quick-deploy

prepare-environment: deps

python-deps:
	pip install -r development.txt
	python setup.py develop

js-deps:
	cd caffeine/static && npm install

deps: python-deps js-deps

deploy-everything:
	ansible-playbook --vault-password-file=$(HOME)/.ansible-vault.caffeine -i provisioning/inventory provisioning/site.yml

quick-deploy:
	ansible-playbook --vault-password-file=$(HOME)/.ansible-vault.caffeine -i provisioning/inventory provisioning/site.yml -t web
	#say -v "Samantha" 'Heads up, a new version of tune tank is online'

static: js-deps
	cd caffeine/static && webpack --progress --colors

watch:
	cd caffeine/static && webpack --progress --colors --watch

run:
	caffeine web --port=5000 --host=127.0.0.1

edit-vault:
	ansible-vault --vault-password-file=~/.ansible-vault.caffeine edit provisioning/caffeine-vault.yml

migrations: cleaninbox
	echo "drop database if exists caffeine;" | mysql -uroot
	echo "create database caffeine;" | mysql -uroot
	alembic upgrade head

unit:
	nosetests -x --with-coverage --cover-erase --cover-package=caffeine --verbosity=2 -s --rednose tests/unit

functional: migrations
	nosetests -x --with-coverage --cover-erase --cover-package=caffeine --verbosity=2 -s --rednose tests/functional

supervisor:
	supervisord -c supervisor.conf

workers:
	caffeine workers --pull-bind-address=tcp://0.0.0.0:4200 id3-extractor

scan:
	caffeine scan inbox


cleaninbox:
	rm -rf inbox
	mkdir -p inbox
