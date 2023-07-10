import os
import fpdf
import json
import requests
import matplotlib.pyplot as plt


class OpenDiggerCLI:
    def __init__(self):
        self.url_start = 'https://oss.x-lab.info/open_digger/github/'
        self.url_end = '.json'
        self.response_contents = []

        # repo支持的指标
        self.repo_metric_list = ['openrank', 'activity', 'attention', 'active_dates_and_times',
                            'stars', 'technical_fork', 'participants', 'new_contributors',
                            'new_contributors_detail', 'inactive_contributors', 'bus_factor',
                            'bus_factor_detail', 'issues_new', 'issues_closed', 'issue_comments',
                            'issue_response_time', 'issue_resolution_duration', 'issue_age',
                            'code_change_lines_add', 'code_change_lines_remove',
                            'code_change_lines_sum', 'change_requests', 'change_requests_accepted',
                            'change_requests_reviews', 'change_request_response_time',
                            'change_request_resolution_duration', 'change_request_age',
                            'activity_details', 'developer_network', 'repo_network', 'project_openrank_detail']

        # user支持的指标
        self.user_metric_list = ['openrank', 'activity', 'developer_network', 'repo_network']

        # 网络指标
        self.network_metric_list = ['developer_network', 'repo_network', 'project_openrank']

        # 不支持进行统计计算的指标
        self.no_stat_metric_list = ['active_dates_and_times', 'new_contributors_detail', 'bus_factor_detail',
                               'issue_response_time', 'issue_resolution_duration', 'issues_new',
                               'change_request_response_time', 'change_request_resolution_duration',
                               'change_request_age', 'activity_details']

        # 特殊指标
        self.quantile_list_metric_list = ['issue_response_time', 'issue_resolution_duration', 'issues_new',
                                     'change_request_response_time', 'change_request_resolution_duration',
                                     'change_request_age']
        self.quantile_query_list = ['avg', 'levels', 'quantile_0', 'quantile_1', 'quantile_2', 'quantile_3', 'quantile_4']

        # 中间结果
        self.result_dict = dict()


    def get_data(self, metric: str, option: str) -> dict:
        """
        以HTTPS URL的形式获取json数据
        :param metric: 指标名
        :param option: org/repo 或 owner
        :return: 转化为dict的数据
        """
        url = self.url_start + option + '/'
        metric = metric.lower().replace(' ', '_')
        url = url + metric + self.url_end

        response = requests.get(url)
        response_content = eval(response.content.decode())

        return response_content


    def query_month(self, metric_list: list, month_list: list, stat_list: list, option: str):
        """
        查询月份相关的数据
        :param metric_list: 待查询的指标数组
        :param month_list: 待查询的月份数组
        :param stat_list: 待统计的指标
        :param option: org/repo 或 owner
        :return:
        """
        for i, metric in enumerate(metric_list):
            self.result_dict[metric] = dict()
            self.result_dict[metric]['month'] = dict()
            self.result_dict[metric]['stat'] = dict()

            try:
                response_content = self.get_data(metric, option)
                self.response_contents.append(response_content)
            except Exception:
                print('[ERROR] request data failed, please check if the input is correct')
                return

            for month in month_list:
                if month == 'all':
                    self.result_dict[metric]['month'] = response_content
                    break
                else:
                    if metric in self.quantile_list_metric_list:
                        self.result_dict[metric]['month'][month] = dict()
                        for item in self.quantile_query_list:
                            try:
                                self.result_dict[metric]['month'][month][item] = response_content[item][month]
                            except Exception:
                                self.result_dict[metric]['month'][month][item] = 'none'
                    else:
                        try:
                            self.result_dict[metric]['month'][month] = response_content[month]
                        except Exception:
                            self.result_dict[metric]['month'][month] = 'none'

            temp_data = self.result_dict[metric]['month']
            data = dict()
            for k, v in temp_data.items():
                if v != 'none':
                    data[k] = v

            if len(stat_list) and len(data.keys()):
                sorted_data = sorted(data.items(), key=lambda x: x[1])

                for stat in stat_list:
                    if stat == 'min':
                        minimum_value = sorted_data[0][1]
                        minimum_keys = [item[0] for item in sorted_data if item[1] == minimum_value]
                        self.result_dict[metric]['stat']['min'] = (minimum_value, minimum_keys)
                    elif stat == 'max':
                        maximum_value = sorted_data[-1][1]
                        maximum_keys = [item[0] for item in sorted_data if item[1] == maximum_value]
                        self.result_dict[metric]['stat']['max'] = (maximum_value, maximum_keys)
                    else:
                        middle_index = len(sorted_data) // 2
                        middle_value = sorted_data[middle_index][1]
                        middle_keys = [item[0] for item in sorted_data if item[1] == middle_value]
                        self.result_dict[metric]['stat']['avg'] = (middle_value, middle_keys)

    def query_network(self, metric_list: list, node_list: list, edge_list: list, option: str):
        """
        查询网络相关的数据
        :param metric_list: 待查询的指标数组
        :param node_list: 待查询的节点数组
        :param edge_list: 待查询的边数组
        :param option: org/repo 或 owner
        :return:
        """
        for metric in metric_list:
            self.result_dict[metric] = dict()
            self.result_dict[metric]['node'] = dict()
            self.result_dict[metric]['edge'] = dict()

            try:
                response_content = self.get_data(metric, option)
            except Exception:
                print('[ERROR] request data failed, please check if the input is correct')
                return

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

            for node in node_list:
                if node == 'all':
                    for item in response_content['nodes']:
                        self.result_dict[metric]['node'][item[0]] = dict()
                        self.result_dict[metric]['node'][item[0]]['weight'] = item[1]
                        self.result_dict[metric]['node'][item[0]]['neighbor'] = list(preprocess_edge_dict[item[0]].keys())
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

            for edge in edge_list:
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

    @staticmethod
    def get_pic_json(metric):
        """
        检查是否能够可视化
        :param metric: 指标名
        :return:
        """
        if metric in ['openrank', 'activity', 'attention',
                      'stars', 'technical_fork', 'participants', 'new_contributors',
                      'inactive_contributors', 'bus_factor',
                      'issues_new', 'issues_closed', 'issue_comments',
                      'code_change_lines_add', 'code_change_lines_remove',
                      'code_change_lines_sum', 'change_requests', 'change_requests_accepted',
                      'change_requests_reviews']:
            return True
        else:
            print(f'[WARNING] {metric} can not draw!')
        return False
    @staticmethod
    def print_pic(name, xlabel, ylabel, json_data, path=None):
        """
        可视化
        :param name:
        :param xlabel:
        :param ylabel:
        :param json_data:
        :param path:
        :return:
        """
        plt.bar(json_data.keys(), json_data.values())
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=90, fontsize=7)
        plt.suptitle(name)
        if path is not None:
            save_path = path
        else:
            save_path = "./picture.jpg"
        plt.savefig(save_path)

    def print_result(self, option):
        if '/' in option:
            print(f'repo name: {option}')
            print(f'repo url: https://github.com/{option}')
        else:
            print(f'user name: {option}')
            print(f'user url: https://github.com/{option}')

        print()

        for key, value in self.result_dict.items():
            print(key)
            print(value)

    def output_pdf(self, args, option, metric_list):
        """
        将结果输出至PDF中
        :param args:
        :param metric_list:
        :return:
        """
        save_path = args.save_path
        output_path_pdf = f'{save_path}report.pdf' if save_path[-1] == '/' else f'{save_path}/report.pdf'

        pdf = fpdf.FPDF(format='letter', unit='in')
        pdf.add_page()
        pdf.set_font('Times', '', 13)
        pdf.set_line_width(0.5)
        effective_page_width = pdf.w - 2*pdf.l_margin

        result_json = json.dumps(self.result_dict)
        if '/' in option:
            pdf.multi_cell(effective_page_width, 0.3, f'repo name: {option}')
            pdf.multi_cell(effective_page_width, 0.3, f'repo url: https://github.com/{option}')
        else:
            pdf.multi_cell(effective_page_width, 0.3, f'user name: {option}')
            pdf.multi_cell(effective_page_width, 0.3, f'user url: https://github.com/{option}')

        pdf.multi_cell(effective_page_width, 0.3, result_json)

        jpg_list = list()
        for i, res in enumerate(self.response_contents):
            can_print = OpenDiggerCLI.get_pic_json(metric_list[i])
            if can_print is False:
                continue
            output_path_jpg = f'{save_path}picture{i}.jpg' if save_path[-1] == '/' else f'{save_path}/picture{i}.jpg'
            OpenDiggerCLI.print_pic(f'{metric_list[i]} for {option}', 'time', metric_list[i], res, output_path_jpg)
            jpg_list.append(output_path_jpg)
            pdf.image(output_path_jpg, w=6, h=4.5)
        pdf.output(output_path_pdf, 'F')

        for item in jpg_list:
            os.remove(item)

        return output_path_pdf

    def executive_request(self, args):
        """
        解析args中的参数
        :param args:
        :return:
        """
        repo = args.repo
        user = args.user
        metric = args.metric.lower()
        metric_list = args.metric_list
        month = args.month
        stat = args.stat
        download = args.download
        node = args.node
        edge = args.edge

        if repo and user:
            print('[ERROR] Only one of repo and user can be chosen')
            return
        if not repo and not user:
            print('[ERROR] One of repo and user must be chosen')
            return

        if metric_list:
            if repo:
                print('[INFO] The optional metric for the repo is')
                for item in self.repo_metric_list:
                    print(item)
            else:
                print('[INFO] The optional metric for the user is')
                for item in self.user_metric_list:
                    print(item)
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
            if metric in self.network_metric_list:
                network_metric_list.append(metric)
            elif metric in self.repo_metric_list:
                simple_metric_list.append(metric)
            else:
                print(f'[ERROR] {metric} does not exist')

        if len(network_metric_list) > 0 and len(network_metric_list) != len(temp_metric_list):
            print('[ERROR] can not query network and non-network metrics at the same time')
            return

        self.query_month(metric_list=simple_metric_list, month_list=month_list, stat_list=stat_list,
                         option=option)

        self.query_network(metric_list=network_metric_list, node_list=node_list, edge_list=edge_list,
                           option=option)

        # debug
        # print(query_result_dict)

        if download:
            output_path = self.output_pdf(args, option, temp_metric_list)
            print('[INFO] the pdf output is completed and saved at ', output_path)
        else:
            self.print_result(option)




