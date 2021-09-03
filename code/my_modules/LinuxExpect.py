import logging
import sys
import re
import time
import pexpect
from termcolor import colored
import colorama
colorama.init()


class LinuxExpect(object):
    def __init__(self, prompt, timeout):
        self.logger = logging.getLogger()
        self.process = pexpect.spawn('/bin/sh')
        self.prompt = prompt
        self.timeout = timeout
        # self.cmd_sendline('')
        self.process.expect(prompt, int(timeout))

        msg = '{}\n{}'.format(self.process.before.decode('utf-8', errors='ignore').replace('\r\n', '\n'), self.process.after.decode('utf-8', errors='ignore').replace('\r\n', '\n'))
        print(self.process.before.decode('utf-8', errors='ignore').replace('\r\n', '\n'), end='')
        print(self.process.after.decode('utf-8', errors='ignore').replace('\r\n', '\n'), end='')
        self.logger.info(self.replace_str(msg))

    def cmd_readline(self, exp_err=False):
        print(colored('\n--- Execution Result ---', 'blue', attrs=['bold']))
        if (exp_err):
            # マッチした前の文字列
            print(self.process.before.decode('utf-8', errors='ignore').replace('\r\n', '\n'), end='')
            msg = '{}'.format(self.process.before.decode('utf-8', errors='ignore').replace('\r\n', '\n'))
            self.logger.info(self.replace_str(msg))
        else:
            # マッチした前の文字列
            print(self.process.before.decode('utf-8', errors='ignore').replace('\r\n', '\n'), end='')
            # マッチした文字
            print(self.process.after.decode('utf-8', errors='ignore').replace('\r\n', '\n'), end='')
            # マッチした後の文字列
            print(self.process.buffer.decode('utf-8', errors='ignore').replace('\r\n', '\n'), end='')
            msg = '{}\n{}\n{}'.format(self.process.before.decode('utf-8', errors='ignore').replace('\r\n', '\n'), self.process.after.decode('utf-8', errors='ignore').replace('\r\n', '\n'), self.process.buffer.decode('utf-8', errors='ignore').replace('\r\n', '\n'))
            self.logger.info(self.replace_str(msg))

    def cmd_sendline(self, cmd, prompt='', timeout=''):
        if prompt == '':
            prompt = self.prompt
        if timeout == '':
            timeout = self.timeout
        self.process.sendline(cmd)
        while True:
            try:
                self.process.expect(prompt, int(timeout))
            except Exception as ex:
                self.cmd_readline(True)
                print(colored('\n[TimeOutError] The prompt could not be detected.', 'red'))
                self.logger.error('The prompt could not be detected.')
                while True:
                    input_yn = input('[W]ait/[C]trl+C/[I]nputCmd/[Q]uit: ').upper()
                    if input_yn.upper() == 'W':
                        print(colored('\nwait 10 seconds.', 'red'))
                        time.sleep(10)
                        break
                    elif input_yn.upper() == 'C':
                        break
                    elif input_yn.upper() == 'I':
                        break
                    elif input_yn.upper() == 'Q':
                        sys.exit(1)
                if input_yn.upper() == 'C':
                    self.process.sendcontrol('c')
                    time.sleep(3)
                    self.cmd_sendline('')
                elif input_yn.upper() == 'I':
                    input_cmd = input('Input Command: ')
                    self.cmd_sendline(input_cmd)
                    return
            else:
                self.cmd_readline()
                return

    def replace_str(self, strtmp):
        ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
        return ansi_escape.sub('', strtmp)
