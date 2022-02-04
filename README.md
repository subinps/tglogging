# Telegram Logger 

> A simple python package to send your app logs to a telegram chat in realtime.

### Installing

``` bash
pip3 install tglogging
```

## Example Usage

Add ```TelegramLogHandler``` handler to your logging config.


```python
import logging
from tglogging import TelegramLogHandler

# TelegramLogHandler is a custom handler which is inherited from an existing handler. ie, StreamHandler.

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        TelegramLogHandler(
            token="12345678:AbCDEFGhiJklmNoPQRTSUVWxyZ", 
            log_chat_id=-10225533666, 
            update_interval=2, 
            minimum_lines=1, 
            pending_logs=200000),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

logger.info("live log streaming to telegram.")

```
## Parameters

```token``` : A telegram bot token to interact with telegram API.

```log_chat_id``` : Chat id of chat to which logs are to be send.

```update_interval```: Interval between two posting in seconds. Lower intervals will lead to floodwaits. Default to 5 seconds.

```minimum_lines```: Minimum number of new lines required to post / edit a message.

```pending_logs```: Maximum number of characters for pending logs to send as file.
default to 200000. this means if the app is producing a lot of logs within short span of time, if the pending logs exceeds 200000 characters it will be send as a file. change according to your app.


## LICENSE

- [MIT License](./LICENSE)