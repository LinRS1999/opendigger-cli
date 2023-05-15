from argparse import ArgumentParser
from .func import Func

def setup_parser():
    parser = ArgumentParser()
    parser.add_argument('--repo', required=True, type=str, help='input repo')
    parser.add_argument('--metric', type=str, help='input metric')
    parser.add_argument('--month', type=str, help='input month')
    parser.set_defaults(func=Func.executive_request)

    return parser

if __name__ == '__main__':
    parser = setup_parser()
    args = parser.parse_args()
    args.func(args)