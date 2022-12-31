### Pyrubi

> Pyrubi is a powerful library for building self robots in Rubika

<p align='center'>
    <a href='github.address'>
        <img src='https://iili.io/HIjPRS9.jpg' alt='Pyrubi' width='256'>
    </a>
    <a href='https://github.com/AliGanji1/pyrubi'>
        GitHub
    </a>
</p>

**Example:**
``` python
from pyrubi import Bot, Tools

bot = Bot('TOKEN')

for msg in bot.on_message():
    m = Tools.message(msg)
    if m.text() == 'Hello':
        bot.reply(msg, 'Hello from Pyrubi library')
```

**Async Example:**
``` python
from pyrubi import Bot_async, Tools

bot = Bot_async('TOKEN')

@bot.on_message
async def update(msg):
    m = Tools.message(msg)
    if m.text() == 'Hello':
        await bot.reply(msg, 'Hello from Pyrubi library')
```

### Features

**Fast**, **Easy**, **Async**, **Powerful**

### Installing

``` bash
python -m pip install pyrubi
```