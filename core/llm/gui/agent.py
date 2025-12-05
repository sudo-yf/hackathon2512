import logging
import os
import queue
import threading
from queue import Queue

from litellm import completion

from core.computer.mouse import click, double_click, right_click
from core.computer.screen import Screen

from .default_prompt import get_default_prompt

class GUIAgent:
    def __init__(self):
        self.default_prompt = get_default_prompt()
        self.model = os.getenv("GUIAgent_MODEL")
        self.api_base = os.getenv("GUIAgent_API_BASE")
        self.api_key = os.getenv("GUIAgent_API_KEY")
        self.stop_agent = False

    def _listener(self, message_from_client: Queue):
        """
        监听来自客户端的信息
        :param message_from_client:
        :return:
        """
        while True:
            try:
                message = message_from_client.get(timeout=0.5)
            except queue.Empty:
                continue
            print("get client message")
            # 不是发给GUIAgent的信息，放回
            if message["name"] != "GUIAgent":
                message_from_client.put(message)
                continue
            if message["type"] == "request":
                # 停止相关
                if message["content"] == "stop_agent":
                    self.stop_agent = True
                    logging.info("[GUIAgent]User stopped agent")

    def task(self, description: str, message_from_client: Queue, message_to_client: Queue):

        logging.info("[GUIAgent]Prompt: %s", self.default_prompt.format(instruction=description))
        messages = [{"role": "system", "content": self.default_prompt.format(instruction=description)}]
        listener_thread = threading.Thread(target=self._listener, args=(message_from_client,))
        listener_thread.daemon = True
        listener_thread.start()
        logging.info("[GUIAgent][START]")
        message_to_client.put({"name": "GUIAgent", "type": "status", "content": "[START]"})

        while True:
            Screen.screenshot()
            response = completion(
                model=self.model,
                api_base=self.api_base,
                api_key=self.api_key,
                messages=messages,
                stream=True,
                thinking="enabled",
            )
            message_to_client.put({"name": "GUIAgent", "type": "status", "content": "[BEGIN]"})
            ai_content = ""
            for chunk in response:                # 检查是否需要停止
                if self.stop_agent:
                    logging.info("[GUIAgent][STOP]: User stop")
                    message_to_client.put({"name": "GUIAgent", "type": "status", "content": "[STOP]"})
                    return
                if chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content
                    message_to_client.put({"name": "GUIAgent", "type": "ai_content", "content": delta})
                    ai_content += delta
            message_to_client.put({"name": "GUIAgent", "type": "status", "content": "[END]"})
            messages.append({"role": "assistant", "content": ai_content})

