from argparse import ArgumentParser
from .func import OpenDiggerCLI

def setup_parser():
    parser = ArgumentParser()

    parser.add_argument('--repo', type=str, help='input repo')
    parser.add_argument('--user', type=str, help='input user')

    parser.add_argument('--metric', type=str, help='input metric')
    parser.add_argument('--metric_list', action='store_true', help='input metric_list')

    parser.add_argument('--month', type=str, default='all', help='input month')

    parser.add_argument('--stat', type=str, help='min, max, avg')

    parser.add_argument('--download', action='store_true', help='')
    parser.add_argument('--save_path', type=str, default='./', help='')

    parser.add_argument('--node', type=str, default='', help='')
    parser.add_argument('--edge', type=str, default='', help='')

    return parser


if __name__ == '__main__':
    parser = setup_parser()
    args = parser.parse_args()
    openDiggerCLI = OpenDiggerCLI()
    openDiggerCLI.executive_request(args)