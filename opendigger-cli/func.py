import requests


class Func:
    url_start = 'https://oss.x-lab.info/open_digger/github/'
    url_end = '.json'

    repo_metric_list = ['openrank', 'activity', 'attention', 'active dates and times',
                   'stars', 'technical fork', 'participants', 'new contributors',
                   'new contributors detail', 'inactive contributors', 'bus factor',
                   'bus factor detail', 'issues new', 'issues closed', 'issue comments',
                   'issue response time', 'issue resolution duration', 'issue age',
                   'code change lines add', 'code change lines remove',
                   'code change lines sum', 'change requests', 'change requests accepted',
                   'change requests reviews', 'change request response time',
                   'change request resolution duration', 'change request age',
                   'activity details', 'developer network', 'repo network', 'project openrank detail']

    user_metric_list = ['openrank', 'activity', 'developer network', 'repo network']

    network_metric_list = ['developer network', 'repo network', 'project openrank']

    no_stat_list = []

    @staticmethod
    def get_data(metric: str, option: str):
        url = Func.url_start + option + '/'

        metric = metric.lower().replace(' ', '_')
        url = url + metric + Func.url_end

        response = requests.get(url)
        response_content = eval(response.content.decode())

        return response_content

    @staticmethod
    def query(option: str, simple_metric_list: list, network_metric_list: list, month_list: list,
              stat_list: list, node_list: list, edge_list: list):

        result_dict = dict()

        for metric in simple_metric_list:
            result_dict[metric] = dict()
            response_content = Func.get_data(metric, option)

            # todo 测试一下错误的url的返回值
            if not response_content:
                print('error, invaild url')

            for month in month_list:
                if month == 'all':
                    result_dict[metric] = response_content
                    break
                else:
                    try:
                        result_dict[metric][month] = response_content[month]
                    except Exception:
                        result_dict[metric][month] = 'none'

            data = result_dict[metric]

            sorted_data = None
            if len(stat_list):
                sorted_data = sorted(data.items(), key=lambda x: x[1])

            # todo 有些指标不支持计算stat，如active_dates_and_times
            for stat in stat_list:
                if stat == 'min':
                    minimum_value = sorted_data[0][1]
                    minimum_keys = [item[0] for item in sorted_data if item[1] == minimum_value]
                    result_dict[metric]['min'] = (minimum_value, minimum_keys)
                elif stat == 'max':
                    maximum_value = sorted_data[-1][1]
                    maximum_keys = [item[0] for item in sorted_data if item[1] == maximum_value]
                    result_dict[metric]['max'] = (maximum_value, maximum_keys)
                else:
                    middle_index = len(sorted_data) // 2
                    middle_value = sorted_data[middle_index][1]
                    middle_keys = [item[0] for item in sorted_data if item[1] == middle_value]
                    result_dict[metric]['avg'] = (middle_value, middle_keys)

        for metric in network_metric_list:
            result_dict[metric] = dict()
            response_content = Func.get_data(metric, option)

            # todo 测试一下错误的url的返回值
            if not response_content:
                print('error, invaild url')

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

            result_dict[metric]['node'] = dict()

            for node in node_list:
                if node == 'all':
                    for item in response_content['nodes']:
                        result_dict[metric]['node'][item[0]] = dict()
                        result_dict[metric]['node'][item[0]]['weight'] = item[1]
                        result_dict[metric]['node'][item[0]]['neighbor'] = preprocess_edge_dict[item[0]].keys()
                    break
                else:
                    result_dict[metric]['node'][node] = dict()
                    try:
                        result_dict[metric]['node'][node]['weight'] = preprocess_node_dict[node]
                    except Exception:
                        result_dict[metric]['node'][node]['weight'] = 'none'

                    try:
                        result_dict[metric]['node'][node]['neighbor'] = preprocess_edge_dict[node].keys()
                    except Exception:
                        result_dict[metric]['node'][node]['neighbor'] = 'none'

            for edge in edge_list:
                node1, node2 = edge
                try:
                    result_dict[metric]


            result_dict[metric]['node'] = dict()
            for node in node_list:
                if node == 'all':
                    for item in response_content['nodes']:
                        weight = item[1]

                        result_dict[metric]['node'][item[0]] = item[1]
                    break
                else:
                    flag = False
                    for item in response_content['nodes']:
                        if item[0] == node:
                            result_dict[metric]['node'][node] = item[1]
                            flag = True
                            break

                    if not flag:
                        result_dict[metric]['node'][node] = 'none'

            for edge in edge_list:
                if


            if find_flag:
                result_dict[metric]['nodes'] = response_content['nodes']

            for item in find_neighbor_list:
                connected_nodes = list()
                for edge in response_content['edges']:
                    node1, node2, weight = edge
                    if node1 == item:
                        connected_nodes.append((node2, weight))
                    elif node2 == item:
                        connected_nodes.append((node1, weight))

                result_dict[metric][item] = connected_nodes

        return result_dict

    @staticmethod
    def print_result(result_dict):
        pass

    @staticmethod
    def ouput_pdf(result_dict, save_path):
        pass

    @staticmethod
    def executive_request(args):
        repo = args.repo
        user = args.user
        metric = args.metric
        metric_list = args.metric_list
        month = args.month
        stat = args.stat
        download = args.download
        save_path = args.save_path
        node = args.node
        edge = args.egde

        if repo and user:
            print('error, you can only choose one')
            return
        if not repo and not user:
            print('error, you must choose one')
            return

        if metric_list:
            if repo:
                print(Func.repo_metric_list)
            else:
                print(Func.user_metric_list)
            return

        option = repo if repo else user

        temp_metric_list = metric.split(',') if metric else list()
        month_list = month.split(',') if month else list()
        stat_list = stat.split(',') if stat else list()
        node_list = node.split(',') if node else list()
        edge_list = edge.split(',') if edge else list()

        # 不能同时查询网络和非网络指标
        network_metric_list = list()
        simple_metric_list = list()

        for metric in temp_metric_list:
            if metric in Func.network_metric_list:
                network_metric_list.append(metric)
            else:
                simple_metric_list.append(metric)

        if len(network_metric_list) > 0 and len(network_metric_list) != len(simple_metric_list):
            print('error, 不能同时查询网络和非网络指标')
            return

        query_result_dict = Func.query(option=option, simple_metric_list=simple_metric_list,
                                       network_metric_list=network_metric_list, month_list=month_list,
                                       stat_list=stat_list, node_list=node_list, edge_list=edge_list)

        print(query_result_dict)

        if download:
            Func.ouput_pdf(query_result_dict, save_path)
            print('pdf save xxx')
        else:
            Func.print_result(query_result_dict)





