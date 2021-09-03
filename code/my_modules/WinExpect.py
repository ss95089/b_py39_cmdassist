import logging
import sys
import time
import pexpect.popen_spawn as psp
from termcolor import colored
import colorama
colorama.init()


class WinExpect(object):
    def __init__(self, prompt, timeout):
        self.logger = logging.getLogger()
        self.process = psp.PopenSpawn('cmd')
        self.prompt = prompt
        self.timeout = timeout
        # self.cmd_sendline('')
        self.process.expect(prompt, int(timeout))

        msg = '{}\n{}'.format(self.process.before.decode('shift-jis', errors='ignore').replace('\r\n', '\n'), self.process.after.decode('shift-jis', errors='ignore').replace('\r\n', '\n'))
        print(self.process.before.decode('shift-jis', errors='ignore').replace('\r\n', '\n'), end='')
        print(self.process.after.decode('shift-jis', errors='ignore').replace('\r\n', '\n'), end='')
        self.logger.info(msg)


    def cmd_readline(self, exp_err=False):
        print(colored('\n--- Execution Result ---', 'blue', attrs=['bold']))
        if (exp_err):
            # マッチした前の文字列
            print(self.process.before.decode('shift-jis', errors='ignore').replace('\r\n', '\n'), end='')
            msg = '{}'.format(self.process.before.decode('shift-jis', errors='ignore').replace('\r\n', '\n'))
            self.logger.info(msg)
        else:
            # マッチした前の文字列
            print(self.process.before.decode('shift-jis', errors='ignore').replace('\r\n', '\n'), end='')
            # マッチした文字
            print(colored(self.process.after.decode('shift-jis', errors='ignore').replace('\r\n', '\n'), 'green'))
            # マッチした後の文字列
            print(self.process.buffer.decode('shift-jis', errors='ignore').replace('\r\n', '\n'), end='')
            msg = '{}\n{}\n{}'.format(self.process.before.decode('shift-jis', errors='ignore').replace('\r\n', '\n'), self.process.after.decode('shift-jis', errors='ignore').replace('\r\n', '\n'), self.process.buffer.decode('shift-jis', errors='ignore').replace('\r\n', '\n'))
            self.logger.info(msg)

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
                #pass
                self.cmd_readline(True)
                print(colored('\n[TimeOutError] The prompt could not be detected.', 'red'))
                self.logger.error('The prompt could not be detected.')
                input_yn = input('[W]ait/[Q]uit: ').upper()
                if input_yn.upper() == 'Q':
                    sys.exit(1)
                elif input_yn.upper() == 'W':
                    print(colored('\nwait 10 seconds.', 'red'))
                    time.sleep(10)
            else:
                self.cmd_readline()
                break

