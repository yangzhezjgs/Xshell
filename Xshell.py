import os
import sys
import shlex
import getpass
import socket
import signal
import subprocess
import platform
from func import *

class Shell:
    def __init__(self):
        self.built_in_cmds = {}
        self.status = SHELL_STATUS_RUN

    def register_command(self,name,func):
        self.built_in_cmds[name] = func

    def init_command(self):
        self.register_command("cd", cd)
        self.register_command("exit", exit)
        self.register_command("getenv", getenv)
        self.register_command("history", history)

    def run(self):
        while self.status == SHELL_STATUS_RUN:
            self.display_cmd_prompt()
            self.ignore_signals()
            try:
                cmd = sys.stdin.readline()
                cmd_tokens = self.tokenize(cmd)
                cmd_tokens = self.preprocess(cmd_tokens)
                self.status = self.execute(cmd_tokens)
            except:
                _, err, _ = sys.exc_info()
                print(err)

    def display_cmd_prompt(self):
        user = getpass.getuser()
        hostname = socket.gethostname()
        cwd = os.getcwd()
        base_dir = os.path.basename(cwd)
        home_dir = os.path.expanduser('~')
        if cwd == home_dir:
            base_dir = '~'
        if platform.system() != 'Windows':
            sys.stdout.write("[\033[1;33m%s\033[0;0m@%s \033[1;36m%s\033[0;0m] $ " % (user,hostname, base_dir))
        else:
            sys.stdout.write("[%s@%s %s]$ " % (user, hostname, base_dir))
        sys.stdout.flush()

    def ignore_signals(self):
        if platform.system() != "Windows":
            signal.signal(signal.SIGTSTP, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def tokenize(self,string):
        return shlex.split(string)

    def preprocess(self,tokens):
        processed_token = []
        for token in tokens:
            if token.startswith('$'):
                processed_token.append(os.getenv(token[1:]))
            else:
                processed_token.append(token)
        return processed_token

    def handler_kill(self,signum,frame):
        raise OSError("Killed!")

    def execute(self,cmd_tokens):
        with open(HISTORY_PATH, 'a') as history_file:
            history_file.write(' '.join(cmd_tokens) + os.linesep)
        if cmd_tokens:
            cmd_name = cmd_tokens[0]
            cmd_args = cmd_tokens[1:]
            if cmd_name in self.built_in_cmds:
                return self.built_in_cmds[cmd_name](cmd_args)
            signal.signal(signal.SIGINT, self.handler_kill)
            if platform.system() != "Windows":
                p = subprocess.Popen(cmd_tokens)
                p.communicate()
            else:
                command = ""
                command = ' '.join(cmd_tokens)
                os.system(command)
        return SHELL_STATUS_RUN


if __name__ == "__main__":
    shell = Shell()
    shell.init_command()
    shell.run()
