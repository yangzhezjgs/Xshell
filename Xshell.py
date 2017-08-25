import os
import sys
import shlex
import getpass
import socket
import signal
from subprocess import call
import platform
from func import *
class Task:
    def __init__(self):
        self.args = []
        self.type = ''


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
                task = self.preprocess(cmd_tokens)
                self.status = self.execute(task)
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
            sys.stdout.write("[\033[1;34m%s\033[0;0m@%s \033[1;36m%s\033[0;0m] $ " % (user,hostname, base_dir))
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
        task = Task()
        for token in tokens:
            if token.startswith('$'):
                processed_token.append(os.getenv(token[1:]))
            else:
                processed_token.append(token)
        for x in processed_token:
            if x  == '|':
                task.type = 'PIPE'
                i = x.index('|')
                task.args.append(processed_token[0:i+1])
                task.args.append(processed_token[i+2:])
                break
            elif x in ['<','>','2<']:
                task.type = 'RE'
                break
            elif x == '&':
                task.type = 'BACK'
                break
            else:
                task.type = 'NORMAL'
        if task.type != 'PIPE':
                task.args = processed_token
        return task

    def handler_kill(self,signum,frame):
        raise OSError("Killed!")

    def execute(self,task):
        fout = sys.stdout
        fin = sys.stdin
        ferr = sys.stderr
        with open(HISTORY_PATH, 'a') as history_file:
            if task.type == 'PIPE':
                history_file.write(' '.join(str(task.args[0])+'|'+str(task.args[1])) + os.linesep)
            else:
                history_file.write(' '.join(task.args) + os.linesep)
        signal.signal(signal.SIGINT, self.handler_kill)
        if task.type == 'NORMAL':
            cmd_name = task.args[0]
            cmd_args = task.args[1:]
            if cmd_name in self.built_in_cmds:
                return self.built_in_cmds[cmd_name](cmd_args)
            else:
                call(task.args, stdout = fout, stdin = fin, stderr = ferr)
        elif task.type == 'RE':
            if '>' in task.args:
                fout = open(task.args[task.args.index('>') + 1], 'w')
                task.args.remove(task.args[task.args.index('>') + 1])
                task.args.remove('>')
            if '<' in task.args:
                fin = open(task.args[task.args.index('<') + 1], 'w')
                task.argss.remove(task.args[task.args.index('<') + 1])
                task.args.remove('<')
            if '2>' in task.args:
                fin = open(task.args[task.args.index('2>') + 1], 'w')
                task.args.remove(task.args[task.args.index('2>') + 1])
                task.args.remove('2>')
            call(task.args, stdout = fout, stdin = fin, stderr = ferr)
        elif task.type == 'BACK':
            try:
                pid = os.fork()
            except OSError:
                sys.exit(1)
            if pid == 0:
                task.args.remove(task.args[-1])
                call(task.args, stdout = fout, stdin = fin, stderr = ferr)
        elif task.type == 'PIPE':
            pi = os.pipe()
            pid = os.fork()
            if pid:
                os.close(pi[1])
                call(task.args[1],stdin =pi[0],stdout=fout,stderr=ferr)
                os.close(pi[0])
                os.waitpid(-1,os.WNOHANG)
            else:
                os.close(pi[0])
                call(task.args[0],stdout =pi[1],stdin=fin,stderr=ferr)
                os.close(pi[1])
        return SHELL_STATUS_RUN

if __name__ == "__main__":
    shell = Shell()
    shell.init_command()
    shell.run()
