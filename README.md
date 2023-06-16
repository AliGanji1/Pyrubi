> # Pyrubi 1.8.0

<h2 align="center">Pyrubi is a powerful and easy library for building self bots in Rubika</h2>

<p align='center'>
    <img src='https://iili.io/HIjPRS9.jpg' alt='Pyrubi Library 1.8.0' width='356'>
</p>


### => Install or Update:

``` bash
pip install -U pyrubi
```

<h2>=> Example:</h2>

``` python
from pyrubi import Bot, Message

bot = Bot('TOKEN OR AUTH')

for msg in bot.on_message():
    m = Message(msg)
    if m.text() == 'Hello':
        bot.send_text(m.chat_id(), 'Hello from Pyrubi Library', m.message_id())
```

### Features:
    
- *Fast* : **The minimum request time is 0.07 seconds and the maximum request time is 0.3 seconds**
- *Easy* : **All methods and features are designed as easy and optimal as possible**
- *Powerful* : **While the library is simple, it has high speed and features that make your work easier and faster**
- *Learn Methods* : **To learn the methods, refer to the issue section**

# Social Media
## <a href="https://rubika.ir/pyrubika">Rubika</a>
