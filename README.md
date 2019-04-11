# vaultify

Our greater purpose is to **never leave any secret file on a persisting
filesystem.**

`vaultify` allows to integrate various means of secret provision into
any runtime environment, may it be some `containerd`, virtualized box or
bare-metal. Currently, we provide three means of fetching secrets and three
means of consuming them.


>see the table in the feature section for more

## architecture

vaultify is an extensible program, which is driven by a notion of
providers and consumers. Providers are classes, that are meant to
fetch/generate/decrypt secrets and pass them as a dictionary to a
consumer. The consumer will then digest that dictionary in the way it
has been designed: writing it as a `.env` file, some `.json` or spawn
a new process within vaultify-enriched environment.


> You want to store secret environment keys in a gpg encrypted file
> and then provide to it to the environment: use
> the `GPGProvider`-provider and the `EnvRunner`-consumer, e.g.

vaultify will try to compile all secrets into one dictionary, and then
write those to either a volatile file system or just enrich the
current environment.

What will be done actually is configurable via the environment, that
executes vaultify.

## os dependencies

ubuntu:
```
apt-get install entr make
```

## usage

### first steps

1. either create a virtualenv and install requirements.txt or
2. run `docker build .`

Before using `vaultify` you need to export these into your environment:

```bash
export VAULTIFY_PROVIDER=<a-provider-of-your-choice>
export VAULTIFY_CONSUMER=<a-consumer-of-your-choice>
export VAULTIFY_LOGLEVEL=<critical|warning|info|debug>  # default is info
```

>**r**ead **t**he **f**riendly **m**anual for the chosen Provider & Consumer, too

Then just run:
```bash
./entry.py
```


## feature overview

In this table you find an info about which Provider/Consumer
pairs are supported:

```
               | GPG | OpenSSL | Vault |
|--------------|-----|---------|-------|
| DotEnvWriter |  y  |    y    |   y   |
| EnvRunner    |  y  |    y    |   y   |
| JsonWriter   |  y  |    y    |   y   |
```

Assuming the pattern holds, we expect always full compatibility
between any Provider/Consumer pair.

### providers

Providers are all classes, that create some `vaultify`-compliant dictionary,
which then is used by `vaultify` consumers.

#### GPGProvider

This Provider can decrypt symmetrically encrypted files, created with `gpg`.

Adhere to this format:
```bash
KEY1=VAL1
[...]
KEYN=VALN
```

To encrypt such a file, execute:
```bash
gpg --symmetric <secretfile>
```

Below are environment variables, that are needed by this provider:

```bash
# this will be used as the passphrase to gpg
export VAULTIFY_SECRET=<passphrase>
```

#### OpenSSLProvider

This provider can decrypt symmetrically encrypted files, created with `openssl`

Adhere to this format:
```bash
KEY1=VAL1
[...]
KEYN=VALN
```

To encrypt such a file, execute:
```bash
openssl enc -aes-256-cbc -salt -a -in <file> -out <file>.enc
```

> Do not use aes-256-cbc, if there is aes-256-gcm available in your openssl.
This prevents Padding Oracle attacks against the cipher text. Currently
setting the aes cipher is not possible in `vaultify` but will be made, when
the default openssl library ships with AEAD compiled. If your OpenSSL CLI
supports aes-256-gcm, please file a bug report against vaultify.

Below are environment variables, that are needed by this provider:

```bash
# this will be used as the passphrase to openssl
export VAULTIFY_SECRET=<passphrase>
```

#### VaultProvider

This provider fetches secrets from HashiCorp Vault API.


Below are environment variables, that are needed by this provider:

```bash
# set this to a reachable vault API
export VAULT_ADDR=<vault.org.tld>
# set this to nodes in vaults kv engine, where you do have perms for READ
export VAULT_PATHS=<comma-separated-list-of-paths-for-vaults-kv-engine>

# if you do not set $VAULTIFY_SECRET, then
export VAULT_TOKEN=<a-valid-vault-token>
```

`VaultProvider` will use `VAULTIFY_SECRET` or `VAULT_TOKEN` for authentication,
in that order.

### consumers

are all classes that operate on a `vaultify` compliant dictionary, to
**somehow** use the secrets in there for the greater good.

#### DotEnvWriter

This simplest form of vaultification just creates a plaintext file with
the form of

```bash
export Key1=Value1
[...]
export KeyN=ValueN
```

for all N keys in the provided dictionary.

Below are environment variables, that are needed by this consumer:

```bash
# this controls the location of the dotenv file
export VAULTIFY_DESTFILE=/a/path/to/where/secrets.env
```


#### JsonWriter

This consumer is very similar to the `DotEnvWriter`, but produces a
json file instead.

Below are environment variables, that are needed by this consumer:

```bash
# this controls the location of the dotenv file
export VAULTIFY_DESTFILE=/a/path/to/where/secrets.json
```

#### EnvRunner

If you want to just execute a process with some secrets, then
`EnvRunner` consumer will run a subprocess with an enriched
environment for you.

>In that sense `EnvRunner` doubles as an entry point for docker runtimes.

Choose this, if you want to prevent any kind of secret persistence.

> one might not like having docker `tmpfs` volumes swapped or
accidentally persist after a crash

Below are environment variables, that are needed by this consumer:

```bash
# this controls the invocation of the target process.
export VAULTIFY_TARGET='/a/path/where/a/secret/hungry/binary --with-some flag wants-execution'
```

Currently `EnvRunner` does not support interactive commands.
