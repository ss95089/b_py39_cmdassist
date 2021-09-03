import ast
import sys
import os
import configparser
import datetime
import logging
from pytimedinput import timedInput
from termcolor import colored
from optparse import OptionParser
import colorama
colorama.init()

from my_modules.SshExpect import SshExpect
if os.name == 'posix':
    from my_modules.LinuxExpect import LinuxExpect
elif os.name == 'nt':
    from my_modules.WinExpect import WinExpect


def main():

    usage = 'usage: %prog [Options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-c', '--config', action='store', type='string', dest='config', help='Config File Name.(default:config.ini)')
    parser.set_defaults(config='config.ini')
    parser.add_option('-s', '--section', action='store', type='string', dest='section', help='Section Name.(default:default)')
    parser.set_defaults(section='default')
    options, args = parser.parse_args()


    config = configparser.ConfigParser()
    section = options.section
    config.read(options.config, encoding='utf-8')
    CONNECT_TYPE = config[section]['connect_type']
    AUTORUN = config[section]['autorun']
    AUTORUN_TIMEOUT = int(config[section]['autorun_timeout'])
    REPLACE_CHR = config[section]['replace_chr']
    REPLACE_CHR = ast.literal_eval(REPLACE_CHR)

    formatter = '\n[%(asctime)s][%(levelname)s]\n%(message)s'
    logging.basicConfig(filename='logs/{}_{}.log'.format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'), section), encoding='utf-8', level=logging.INFO, format=formatter)

    if CONNECT_TYPE == 'remote':
        HOSTNAME = config[section]['host']
        USERNAME = config[section]['username']
        PASSWORD = config[section]['password']
        PROMPT = config[section]['prompt']
        TIMEOUT = int(config[section]['prompt_timeout'])
        CMD_FILE_NAME = config[section]['command_file']
        timedOut = False

        remote_connect(PROMPT, TIMEOUT, HOSTNAME, USERNAME, PASSWORD, AUTORUN, AUTORUN_TIMEOUT, CMD_FILE_NAME, timedOut, REPLACE_CHR)

    elif CONNECT_TYPE == 'local':
        PROMPT = config[section]['prompt']
        TIMEOUT = int(config[section]['prompt_timeout'])
        CMD_FILE_NAME = config[section]['command_file']
        timedOut = False

        if os.name == 'nt':
            nt_local_connect(PROMPT, TIMEOUT, AUTORUN, AUTORUN_TIMEOUT, CMD_FILE_NAME, timedOut, REPLACE_CHR)
        elif os.name == 'posix':
            posix_local_connect(PROMPT, TIMEOUT, AUTORUN, AUTORUN_TIMEOUT, CMD_FILE_NAME, timedOut, REPLACE_CHR)


def remote_connect(PROMPT, TIMEOUT, HOSTNAME, USERNAME, PASSWORD, AUTORUN, AUTORUN_TIMEOUT, CMD_FILE_NAME, timedOut, REPLACE_CHR):
    proc = SshExpect(PROMPT, TIMEOUT, HOSTNAME, USERNAME, PASSWORD)
    comment_flg = False
    with open(CMD_FILE_NAME, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\n', '')
            if line == '':
                comment_flg = False
                pass
            elif line[0] == '#' or line[0] == "'":
                if not comment_flg:
                    print(colored('\n--- Comment Message ---', 'green', attrs=['bold']))
                print(colored(line, 'green'))
                comment_flg = True
            else:
                comment_flg = False
                t_cmd01, t_prompt01, t_timeout01 = cmdline_parser(line, PROMPT, TIMEOUT, REPLACE_CHR)
                while True:
                    print(colored('\n\n------------------------', 'red', attrs=['bold']))
                    print('[EXE CMD]:', colored(t_cmd01, 'red', attrs=['bold']))
                    print('[CHECK PROMP]:{}   [PROMPT TIMEOUT]:{}s   [AUTORUN]:{}   [AUTORUN TIME]:{}s'.format(t_prompt01, t_timeout01, AUTORUN, AUTORUN_TIMEOUT))
                    if AUTORUN == "yes":
                        cmd_key, timedOut = timedInput(prompt='\n -> [E]xeCmd/[S]kipCmd/[I]nputCmd/[G]etFile(SCP)/[Put]File(SCP)/[Q]uit: ', timeOut=AUTORUN_TIMEOUT, forcedTimeout=False, maxLength=0)
                    else:
                        cmd_key = input('\n -> [E]xeCmd/[S]kipCmd/[I]nputCmd/[G]etFile(SCP)/[Put]File(SCP)/[Q]uit: ').upper()
                    if timedOut:
                        cmd_key = 'E'
                        break
                    elif cmd_key.upper() == 'I':
                        input_cmd = input('Input Command: ')
                        t_cmd02, t_prompt02, t_timeout02 = cmdline_parser(input_cmd, PROMPT, TIMEOUT, REPLACE_CHR)
                        proc.cmd_sendline(t_cmd02, t_prompt02, t_timeout02)
                    elif cmd_key.upper() == 'G':
                        filename = input('Input the GetFileName with FullPath: ')
                        proc.cmd_scp(filename, 'get')
                    elif cmd_key.upper() == 'P':
                        filename = input('Input the PutFileName: ')
                        proc.cmd_scp(filename, 'put')
                    elif cmd_key.upper() == 'E' or cmd_key.upper() == 'S' or cmd_key.upper() == 'Q':
                        break

                if cmd_key.upper() == 'E':
                    proc.cmd_sendline(t_cmd01, t_prompt01, t_timeout01)
                elif cmd_key.upper() == 'S':
                    pass
                elif cmd_key.upper() == 'Q':
                    proc.cmd_close()
                    sys.exit()
    proc.cmd_close()


def nt_local_connect(PROMPT, TIMEOUT, AUTORUN, AUTORUN_TIMEOUT, CMD_FILE_NAME, timedOut, REPLACE_CHR):
    proc = WinExpect(PROMPT, TIMEOUT)
    comment_flg = False
    with open(CMD_FILE_NAME, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\n', '')
            if line == '':
                comment_flg = False
                pass
            elif line[0] == '#' or line[0] == "'":
                if not comment_flg:
                    print(colored('\n--- Comment Message ---', 'green', attrs=['bold']))
                print(colored(line, 'green'))
                comment_flg = True
            else:
                comment_flg = False
                t_cmd01, t_prompt01, t_timeout01 = cmdline_parser(line, PROMPT, TIMEOUT, REPLACE_CHR)
                while True:
                    print(colored('\n\n------------------------', 'red', attrs=['bold']))
                    print('[EXE CMD]:', colored(t_cmd01, 'red', attrs=['bold']))
                    print('[CHECK PROMP]:{}   [PROMPT TIMEOUT]:{}s   [AUTORUN]:{}   [AUTORUN TIME]:{}s'.format(t_prompt01, t_timeout01, AUTORUN, AUTORUN_TIMEOUT))
                    if AUTORUN == 'yes':
                        cmd_key, timedOut = timedInput(prompt='\n -> [E]xeCmd/[S]kipCmd/[I]nputCmd/[Q]uit: ', timeOut=AUTORUN_TIMEOUT, forcedTimeout=False, maxLength=0)
                    else:
                        cmd_key = input('\n -> [E]xeCmd/[S]kipCmd/[I]nputCmd/[Q]uit: ').upper()
                    if timedOut:
                        cmd_key = 'E'
                        break
                    elif cmd_key.upper() == 'I':
                        input_cmd = input('Input Command: ')
                        t_cmd02, t_prompt02, t_timeout02 = cmdline_parser(input_cmd, PROMPT, TIMEOUT, REPLACE_CHR)
                        proc.cmd_sendline(t_cmd02, t_prompt02, t_timeout02)
                    elif cmd_key.upper() == 'E' or cmd_key.upper() == 'S' or cmd_key.upper() == 'Q':
                        break

                if cmd_key.upper() == 'E':
                    proc.cmd_sendline(t_cmd01, t_prompt01, t_timeout01)
                elif cmd_key.upper() == 'S':
                    pass
                elif cmd_key.upper() == 'Q':
                    sys.exit()


def posix_local_connect(PROMPT, TIMEOUT, AUTORUN, AUTORUN_TIMEOUT, CMD_FILE_NAME, timedOut, REPLACE_CHR):
    proc = LinuxExpect(PROMPT, TIMEOUT)
    comment_flg = False
    with open(CMD_FILE_NAME, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\n', '')
            if line == '':
                comment_flg = False
                pass
            elif line[0] == '#' or line[0] == "'":
                if not comment_flg:
                    print(colored('\n--- Comment Message ---', 'green', attrs=['bold']))
                print(colored(line, 'green'))
                comment_flg = True
            else:
                comment_flg = False
                t_cmd01, t_prompt01, t_timeout01 = cmdline_parser(line, PROMPT, TIMEOUT, REPLACE_CHR)
                while True:
                    print(colored('\n\n------------------------', 'red', attrs=['bold']))
                    print('[EXE CMD]:', colored(t_cmd01, 'red', attrs=['bold']))
                    print('[CHECK PROMP]:{}   [PROMPT TIMEOUT]:{}s   [AUTORUN]:{}   [AUTORUN TIME]:{}s'.format(t_prompt01, t_timeout01, AUTORUN, AUTORUN_TIMEOUT))
                    if AUTORUN == 'yes':
                        cmd_key, timedOut = timedInput(prompt='\n -> [E]xeCmd/[S]kipCmd/[I]nputCmd/[Q]uit: ', timeOut=AUTORUN_TIMEOUT, forcedTimeout=False, maxLength=0)
                    else:
                        cmd_key = input('\n -> [E]xeCmd/[S]kipCmd/[I]nputCmd/[Q]uit: ').upper()
                    if timedOut:
                        cmd_key = 'E'
                        break
                    elif cmd_key.upper() == 'I':
                        input_cmd = input('Input Command: ')
                        t_cmd02, t_prompt02, t_timeout02 = cmdline_parser(input_cmd, PROMPT, TIMEOUT, REPLACE_CHR)
                        proc.cmd_sendline(t_cmd02, t_prompt02, t_timeout02)
                    elif cmd_key.upper() == 'E' or cmd_key.upper() == 'S' or cmd_key.upper() == 'Q':
                        break

                if cmd_key.upper() == 'E':
                    proc.cmd_sendline(t_cmd01, t_prompt01, t_timeout01)
                elif cmd_key.upper() == 'S':
                    pass
                elif cmd_key.upper() == 'Q':
                    sys.exit()


def cmdline_parser(cmdline, prompt, timeout, replace_chr):
    tmp01 = cmdline.split('@@@')
    if len(tmp01) == 1:
        t_cmd = replace_charactor(cmdline, replace_chr)
        t_prompt = prompt
        t_timeout = timeout
    elif len(tmp01) == 2:
        t_cmd = replace_charactor(tmp01[0], replace_chr)
        if tmp01[1] == '':
            t_prompt = prompt
        else:
            t_prompt = tmp01[1]
        t_timeout = timeout
    elif len(tmp01) == 3:
        t_cmd = replace_charactor(tmp01[0], replace_chr)
        if tmp01[1] == '':
            t_prompt = prompt
        else:
            t_prompt = tmp01[1]
        if tmp01[2] == '':
            t_timeout = timeout
        else:
            t_timeout = tmp01[2]
    return t_cmd, t_prompt, t_timeout


def replace_charactor(cmd, replace_chr):
    for k, v in replace_chr.items():
        cmd = cmd.replace(k, v)
    return cmd

if __name__ == '__main__':
    main()
