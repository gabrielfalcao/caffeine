# caffeine

## Table of contents

* [Infrastructure](#Infrastructure)
* [Backend](#Backend)

## Infrastructure:

### DNS

```
@	    A   	45.55.107.216 3600
mail	MX 37	caffeine.co   60
```

### Stack

* free tls certs from starcom :P
* nginx
* postfix
* redis
* mysql
* prosody
* restund
* gunicorn

### Deploying

```
ansible-playbook --vault-password-file=$(HOME)/.ansible-vault.caffeine -i provisioning/inventory provisioning/site.yml
```

## Backend

* Python app under `./caffeine`
* Routes:
 * `https://caffeine.co/login`


## SSL:

```
caffeine.co
mail.caffeine.co
files.caffeine.co
api.wavamanda.la
io.caffeine.co
```
