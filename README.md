<div align='center'>
    <img style='border-radius: 10px' src='https://iili.io/HIjPRS9.jpg' alt='pyrubi image' width='320' height='140'>
    <br>
    <br>
    <b>Fast & powerfull Rubika API library</b>
    <br>
    <a href='https://github.com/AliGanji1/pyrubi'>GitHub</a>
    •
    <a href='https://rubika.ir/pyrubi_documents'>Documents</a>
</div>


# Pyrubi 3.6.0
[![Downloads](https://static.pepy.tech/badge/pyrubi)](https://pepy.tech/project/pyrubi)
> Fast and powerfull Rubika API library for building self bots.


<hr>

### Install or Update:

``` bash
pip install -U pyrubi
```

<hr>

### Quick start:

``` python
from pyrubi import Client
from pyrubi.types import Message

client = Client("mySelf")

@client.on_message(regexp="hello")
def send_hello(message: Message):
    message.reply("**hello** __from__ ##pyrubi##")

client.run()
```

also you can enter your session data manually:
```python
from pyrubi import Client
from pyrubi.types import Message

auth_key = "abcdefghijklnopkrstuvwxyzazxcqwe"
private_key = "-----BEGIN RSA PRIVATE KEY-----\n..."

client = Client(auth=auth_key, private=private_key)

@client.on_message(regexp="hello")
def send_hello(message: Message):
    message.reply("**hello** __from__ ##pyrubi##")

client.run()
```

<hr>

### Features:
    
- **Fast** : *The requests are very fast and optimize.*

- **Powerful** : *While the library is simple, it has high speed and features that make your work easier and faster*

- **Easy** : *All methods and features are designed as easy and optimal as possible*


<hr>

### Social Media:
### <a href='https://rubika.ir/pyrubika'>Rubika</a>

<hr>

### 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AliGanji1/Pyrubi&type=Date)](https://star-history.com/#AliGanji1/Pyrubi&Date)