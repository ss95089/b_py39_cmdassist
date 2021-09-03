import logging
import sys
import time

import paramiko
from paramiko_expect import SSHClientInteraction
import scp
from termcolor import colored
import colorama
colorama.init()


class SshExpect(object):
    def __init__(self, prompt, timeout, hostname, username, password):
        self.logger = logging.getLogger()
        self.prompt = prompt
        self.timeout = timeout
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=hostname, username=username, password=password)
        self.interact = SSHClientInteraction(self.client, timeout=timeout, display=False)
        self.interact.expect(prompt)
        print(self.interact.current_output)
        self.logger.info(self.interact.current_output)

    def cmd_readline(self):
        print(colored('\n--- Execution Result ---', 'blue', attrs=['bold']))
        print(self.interact.current_output)
        self.logger.info(self.interact.current_output)

    def cmd_sendline(self, cmd, prompt='', timeout=''):
        if prompt == '':
            prompt = self.prompt
        if timeout == '':
            timeout = self.timeout
        self.interact.send(cmd)
        while True:
            res = self.interact.expect(prompt, int(timeout))
            self.cmd_readline()
            if res == 0:
                return
            elif res == -1:
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
                    self.interact.send(chr(3))
                    time.sleep(3)
                    self.interact.send('')
                    time.sleep(3)
                    self.cmd_sendline('')
                elif input_yn.upper() == 'I':
                    input_cmd = input('Input Command: ')
                    self.interact.send(input_cmd)
                    return

    def cmd_scp(self, filename, scptype):
        with scp.SCPClient(self.client.get_transport(),buff_size=16384*20, socket_timeout=10.0*6, progress=self.progress) as gscp:
            if scptype == 'get':
                try:
                    gscp.get(filename)
                    # print(colored('\n--- Execution Result ---', 'blue', attrs=['bold']))
                except Exception as ex:
                    print(ex)
                    self.logger.info(ex)
                else:
                    print('file: {} has been received.'.format(filename))
                    self.logger.info('file: {} has been received.'.format(filename))
            elif scptype == 'put':
                try:
                    gscp.put(filename)
                    # print(colored('\n--- Execution Result ---', 'blue', attrs=['bold']))
                except Exception as ex:
                    print(ex)
                    self.logger.info(ex)
                else:
                    print('file: {} has been sent.'.format(filename))
                    self.logger.info('file: {} has been sent.'.format(filename))

    def progress(self, filename, size, sent):
        sys.stdout.write("%s\'s progress: %.2f%% \r" % (filename, float(sent) / float(size) * 100))

    def cmd_close(self):
        self.interact.send('exit')
        self.client.close()
        return
