import colorama
import ast

import requests
from fuzzywuzzy import process


class PrintUtil:
    def __init__(self):
        colorama.init()

    def red(self, text: str) -> str:
        return colorama.Fore.RED + text + colorama.Style.RESET_ALL

    def yellow(self, text: str) -> str:
        return colorama.Fore.YELLOW + text + colorama.Style.RESET_ALL

    def warn(self, text: str) -> str:
        print(self.yellow('[WARN] ' + text))

    def info(self, text: str) -> str:
        print('[INFO] ' + text)

    def error(self, text: str) -> str:
        print(self.red('[ERROR] ' + text))


print_util = PrintUtil()


class ConfigKeyError(Exception):
    pass


class Config:
    def __init__(self):
        self.REQUEST_PREFIX = 'https://oss.x-lab.info/open_digger/github/'
        self.REQUEST_SUFFIX = '.json'

        self.REPO_METRIC_LIST = ['openrank', 'activity', 'attention', 'active_dates_and_times',
                                 'stars', 'technical_fork', 'participants', 'new_contributors',
                                 'inactive_contributors', 'bus_factor', 'issues_new', 'issues_closed',
                                 'issue_comments', 'issue_response_time', 'issue_resolution_duration',
                                 'issue_age', 'code_change_lines_add', 'code_change_lines_remove',
                                 'code_change_lines_sum', 'change_requests', 'change_requests_accepted',
                                 'change_requests_reviews', 'change_request_response_time',
                                 'change_request_resolution_duration', 'change_request_age',
                                 'developer_network', 'repo_network']

        self.USER_METRIC_LIST = ['openrank', 'activity', 'developer_network', 'repo_network']

        self.NETWORK_METRIC_LIST = ['developer_network', 'repo_network', 'project_openrank']


project_config = Config()


def request_json_data(metric: str, option: str) -> dict:
    """
    以HTTPS URL的形式获取json数据
    :param metric: 指标名
    :param option: org/repo 或 owner
    :return: 转化为dict的数据
    """

    url = project_config.REQUEST_PREFIX + option + '/'

    if '/' in option:
        match_res = process.extractOne(metric, project_config.REPO_METRIC_LIST)
    else:
        match_res = process.extractOne(metric, project_config.USER_METRIC_LIST)

    if match_res[1] != 100:
        print_util.warn(f'The metric of the query: {metric} does not exist in all computable metrics.'
                        f' You may be referring to {match_res[0]}. Next, {match_res[0]} will be used to calculate the '
                        f'metric')

    url += metric + project_config.REQUEST_SUFFIX

    try:
        response = requests.get(url)
        if response.status_code == 200:
            response_content = ast.literal_eval(response.content.decode())
            print_util.info(f'Requesting: {url}')
        else:
            print_util.error('URL request error, please check whether the URL is accessible in the browser: '
                             f'{url}')
            exit(1)
    except Exception:
        print_util.error('URL request error, please check whether the URL is accessible in the browser: '
                         f'{url}')
        exit(1)

    return response_content

















