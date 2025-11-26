from .languages import PythonLanguage
import queue

class Code:
    def __init__(self):
        self.python = PythonLanguage()
        # self.cmd = CMDLanguage()
        # self.bash = BashLanguage()
        # self.powershell = PowerShellLanguage()
        self.current_language = None
        self.language_map = {
            "python": self.python,
            # "cmd": self.cmd,
            # "powershell": self.powershell,
            # "pwsh": self.powershell,  # PowerShell Core别名
            # "bash": self.bash,
            # "sh": self.bash,  # Shell别名
        }
        self.language_list = []
        for lang, lang_obj in self.language_map.items():
            if hasattr(lang_obj, 'is_available'):
                if lang_obj.is_available():
                    self.language_list.append(lang)
            else:
                # Python总是可用的
                self.language_list.append(lang)

    # def language_list(self):
    #     available = []

    def run(self, lang: str, code: str):
        lang = lang.lower()
        if lang in self.language_list:
            self.current_language = self.language_map[lang]
            return self.current_language.run(code)
        else:
            message = queue.Queue()
            message.put({"type": "error", "content": f"[Code]Unsupported language:{lang}"})
            return message

    def interrupt(self,):
        message = queue.Queue()
        if self.current_language and self.current_language.is_running:
            self.current_language.interrupt()
            message.put({"type": "text", "content": "Code execution interrupted"})
        else:
            message.put({"type": "text", "content": "No code is running"})
        return message

    def get_elapsed_time(self):
        if self.current_language:
            return self.current_language.get_elapsed_time()

    def is_running(self):
        return self.current_language and self.current_language.is_running