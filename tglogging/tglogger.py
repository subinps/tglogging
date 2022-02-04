import io
import time
import asyncio
import nest_asyncio
from logging import StreamHandler
from aiohttp import ClientSession

nest_asyncio.apply()

DEFAULT_PAYLOAD = {
    "disable_web_page_preview": True,
    'parse_mode': "Markdown"
}


class TelegramLogHandler(StreamHandler):
    """
    Handler to send logs to telegram chats.

    Parameters:
        token: a telegram bot token to interact with telegram API.
        log_chat_id: chat id of chat to which logs are to be send.
        update_interval: interval between two posting in seconds.
                            lower intervals will lead to floodwaits.
                            recommended to use greater than 5 sec
        minimum_lines: minimum number of new lines required to post / edit a message.
        pending_logs: maximum number of letters for pending logs to send as file.
                        default to 200000. usefull for apps producing lengthy logs withing few minutes.

    """

    def __init__(
        self,
        token: str,
        log_chat_id: int,
        update_interval: int = 5,
        minimum_lines: int = 1,
        pending_logs: int = 200000
    ):
        StreamHandler.__init__(self)
        self.loop = asyncio.get_event_loop()
        self.token = token
        self.log_chat_id = log_chat_id
        self.wait_time = update_interval
        self.minimum = minimum_lines
        self.pending = pending_logs
        self.messages = ''
        self.current_msg = ''
        self.floodwait = 0
        self.message_id = 0
        self.lines = 0
        self.last_update = 0
        self.base_url = f"https://api.telegram.org/bot{token}"
        DEFAULT_PAYLOAD.update({'chat_id': log_chat_id})

    def emit(self, record):
        msg = self.format(record)
        self.lines += 1
        self.messages += f"{msg}\n"
        diff = time.time() - self.last_update
        if diff >= max(
                self.wait_time,
                self.floodwait) and self.lines >= self.minimum:
            if self.floodwait:
                self.floodwait = 0
            self.loop.run_until_complete(self.handle_logs())
            self.lines = 0
            self.last_update = time.time()

    async def handle_logs(self):
        if len(self.messages) > self.pending:
            _msg = self.messages
            msg = _msg.rsplit('\n', 1)[0]
            if not msg:
                msg = _msg
            self.current_msg = ''
            self.message_id = 0
            self.messages = self.messages[len(msg):]
            await self.send_as_file(msg)  # sending as document
            return
        _message = self.messages[:4050]  # taking first 4050 characters
        msg = _message.rsplit('\n', 1)[0]
        if not msg:
            msg = _message
        letter_count = len(msg)
        # removing these messages from the list
        self.messages = self.messages[letter_count:]
        if not self.message_id:
            await self.initialise()  # Initializing by sending a message
        computed_message = self.current_msg + msg
        if len(computed_message) > 4050:
            _to_edit = computed_message[:4050]
            to_edit = _to_edit.rsplit('\n', 1)[0]
            if not to_edit:
                to_edit = _to_edit  # incase of lengthy lines
            to_new = computed_message[len(to_edit):]
            await self.edit_message(to_edit)
            self.current_msg = to_new
            await self.send_message(to_new)
        else:
            await self.edit_message(computed_message)
            self.current_msg = computed_message

    async def send_request(self, url, payload):
        async with ClientSession() as session:
            async with session.request(
                "POST", url, json=payload
            ) as response:
                e = await response.json()
                return e

    async def initialise(self):
        payload = DEFAULT_PAYLOAD
        payload['text'] = "Initializing"
        url = self.base_url + "/sendMessage"
        res = await self.send_request(url, payload)
        if res.get('ok'):
            result = res.get('result')
            self.message_id = result.get('message_id')
        else:
            await self.handle_error(res)

    async def send_message(self, message):
        payload = DEFAULT_PAYLOAD
        payload['text'] = f"```{message}```"
        url = self.base_url + "/sendMessage"
        res = await self.send_request(url, payload)
        if res.get('ok'):
            result = res.get('result')
            self.message_id = result.get('message_id')
        else:
            await self.handle_error(res)

    async def edit_message(self, message):
        payload = DEFAULT_PAYLOAD
        payload['message_id'] = self.message_id
        payload['text'] = f"```{message}```"
        url = self.base_url + "/editMessageText"
        res = await self.send_request(url, payload)
        if not res.get('ok'):
            await self.handle_error(res)

    async def send_as_file(self, logs):
        file = io.BytesIO(logs.encode())
        file.name = "tglogging.logs"
        url = self.base_url + "/sendDocument"
        payload = DEFAULT_PAYLOAD
        payload['caption'] = "Too much logs to send and hence sending as file."
        files = {'document': file}
        try:
            del payload['disable_web_page_preview']
        except BaseException:
            pass

        async with ClientSession() as session:
            async with session.request(
                "POST", url, params=payload, data=files
            ) as response:
                res = await response.json()
        if res.get('ok'):
            print("Logs send as a file since there were too much lines to print.")
        else:
            await self.handle_error(res)

    async def handle_error(self, resp: dict):
        error = resp.get('parameters', {})
        if not error:
            print(f"Errors while updating TG logs {resp}")
            return
        if error.get('retry_after'):
            self.floodwait = error.get('retry_after')
            print(f'Floodwait of {error.get("retry_after")} and sleeping')
