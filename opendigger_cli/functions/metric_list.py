from .base import Base
from .common import print_util, project_config


class MetricList(Base):
    def __init__(self):
        super().__init__()
        self.option = None
        self.metric_list = False

    def check_args(self, args):
        repo = args.repo
        user = args.user

        if repo and user:
            print_util.error('Only one of repo and user can be chosen')
            exit(1)

        if not repo and not user:
            print_util.error('One of repo and user must be chosen')
            exit(1)

        if repo:
            if '/' not in repo:
                print_util.error(f'There is an error in the input of repo: {repo}')
                exit(1)
            repo = repo.split('/')[0] + '/' + repo.split('/')[1]

        self.option = repo if repo else user

        self.metric_list = True if args.metric_list else False

    def cal(self):
        if self.metric_list:
            if '/' in self.option:
                print_util.info('The optional metric for the repo is')
                for item in project_config.REPO_METRIC_LIST:
                    print(item)
            else:
                print_util.info('The optional metric for the user is')
                for item in project_config.USER_METRIC_LIST:
                    print(item)
            print()
            exit(0)

    def run(self, args):
        self.check_args(args)
        self.cal()



