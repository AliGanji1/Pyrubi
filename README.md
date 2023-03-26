<h1>Pyrubi 1.8.0<h1/>

> Pyrubi is a powerful and easy library for building self robots in Rubika

<p align='center'>
    <img src='https://iili.io/HIjPRS9.jpg' alt='Pyrubi Library 1.8.0' width='356'>
    <a href='https://github.com/AliGanji1/pyrubi'>GitHub</a>
</p>

<hr>

**Example:**
``` python
from pyrubi import Bot, Message

bot = Bot('TOKEN')

for msg in bot.on_message():
    m = Message(msg)
    if m.text() == 'Hello':
        bot.send_text(m.chat_id(), 'Hello from Pyrubi Library', m.message_id())
```

<hr>

### Features:

**Fast : The minimum request time is 0.07 seconds and the maximum request time is 0.3 seconds**,
**Easy : All methods and features are designed as easy and optimal as possible**, 
**Powerful : While the library is simple, it has high speed and features that make your work easier and faster**

<hr>

# Rubika : @pyrubika

### Install or Update:

``` bash
python -m pip install -U pyrubi
```