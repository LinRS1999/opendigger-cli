from .base import Base
from .common import print_util, project_config, request_json_data
from fuzzywuzzy import process


class QueryNetwork(Base):
    def __init__(self):
        super().__init__()
        self.option = None

        self.metric_list = None
        self.node_list = None
        self.edge_list = None

        self.network_metric_list = ['developer_network', 'repo_network', 'project_openrank']

        self.result_dict = dict()


    def check_args(self, args):
        repo = args.repo
        user = args.user
        metric = args.metric
        node = args.node
        edge = args.edge

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

        temp_metric_list = metric.split(',') if metric else []
        corrected_metric_list = []
        if repo:
            for temp_metric in temp_metric_list:
                match_res = process.extractOne(temp_metric, project_config.REPO_METRIC_LIST)

                if match_res[1] != 100:
                    print_util.warn(f'The metric of the query: {temp_metric} does not exist in all computable metrics.'
                                    f' You may be referring to {match_res[0]}. Next, {match_res[0]} will be used to '
                                    f'calculate the metric')
                if match_res[0] in self.network_metric_list:
                    corrected_metric_list.append(match_res[0])

        if user:
            for temp_metric in temp_metric_list:
                match_res = process.extractOne(temp_metric, project_config.USER_METRIC_LIST)

                if match_res[1] != 100:
                    print_util.warn(f'The metric of the query: {temp_metric} does not exist in all computable metrics.'
                                    f' You may be referring to {match_res[0]}. Next, {match_res[0]} will be used to '
                                    f'calculate the metric')
                if match_res[0] in self.network_metric_list:
                    corrected_metric_list.append(match_res[0])
        self.metric_list = corrected_metric_list

        node_list = node.split(',') if node else list()
        self.node_list = node_list

        temp_edge_list = edge.split(',') if edge else list()
        corrected_edge_list = []
        for temp_edge in temp_edge_list:
            if '+' not in temp_edge:
                print_util.warn(f'Two nodes should be connected with +, please check: {temp_edge}')
            else:
                corrected_edge_list.append(temp_edge)
        self.edge_list = corrected_edge_list

    def cal(self):
        """
        查询网络相关的数据
        :param metric_list: 待查询的指标数组
        :param node_list: 待查询的节点数组
        :param edge_list: 待查询的边数组
        :param option: org/repo 或 owner
        :return:
        """
        for metric in self.metric_list:
            self.result_dict[metric] = dict()
            self.result_dict[metric]['node'] = dict()
            self.result_dict[metric]['edge'] = dict()

            response_content = request_json_data(metric, self.option)

            preprocess_node_dict = dict()
            preprocess_edge_dict = dict()
            # 预处理
            for node in response_content['nodes']:
                preprocess_node_dict[node[0]] = node[1]
                preprocess_edge_dict[node[0]] = dict()

            for edge in response_content['edges']:
                node1, node2, weight = edge
                preprocess_edge_dict[node1][node2] = weight
                preprocess_edge_dict[node2][node1] = weight

            for node in self.node_list:
                if node == 'all':
                    for item in response_content['nodes']:
                        self.result_dict[metric]['node'][item[0]] = dict()
                        self.result_dict[metric]['node'][item[0]]['weight'] = item[1]
                        self.result_dict[metric]['node'][item[0]]['neighbor'] = list(
                            preprocess_edge_dict[item[0]].keys())
                    break
                else:
                    self.result_dict[metric]['node'][node] = dict()
                    try:
                        self.result_dict[metric]['node'][node]['weight'] = preprocess_node_dict[node]
                    except Exception:
                        self.result_dict[metric]['node'][node]['weight'] = 'none'

                    try:
                        self.result_dict[metric]['node'][node]['neighbor'] = list(preprocess_edge_dict[node].keys())
                    except Exception:
                        self.result_dict[metric]['node'][node]['neighbor'] = 'none'

            for edge in self.edge_list:
                if edge == 'all':
                    for node1, node2_list in preprocess_edge_dict.items():
                        for node2 in node2_list:
                            k = node1 + '+' + node2
                            try:
                                self.result_dict[metric]['edge'][k] = preprocess_edge_dict[node1][node2]
                            except Exception:
                                self.result_dict[metric]['edge'][k] = 'none'
                else:
                    # 要求格式为node1+node2
                    (node1, node2) = edge.split('+')
                    try:
                        self.result_dict[metric]['edge'][edge] = preprocess_edge_dict[node1][node2]
                    except Exception:
                        self.result_dict[metric]['edge'][edge] = 'none'

    def print_result(self):
        if '/' in self.option:
            print_util.info(f'repo name: {self.option}')
            print_util.info(f'repo url: https://github.com/{self.option}')
        else:
            print_util.info(f'user name: {self.option}')
            print_util.info(f'user url: https://github.com/{self.option}')

        for key, value in self.result_dict.items():
            print_util.info(f'metric: {key}')
            print_util.info(f'result: {str(value)}')

        print()

    def run(self, args):
        self.check_args(args)
        self.cal()
        if len(self.result_dict):
            self.print_result()
            exit(0)
