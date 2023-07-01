import os.path
import fpdf
import json
import requests


class Func:
    url_start = 'https://oss.x-lab.info/open_digger/github/'
    url_end = '.json'

    repo_metric_list = ['openrank', 'activity', 'attention', 'active_dates_and_times',
                        'stars', 'technical_fork', 'participants', 'new_contributors',
                        'new_contributors_detail', 'inactive_contributors', 'bus_factor',
                        'bus_factor_detail', 'issues_new', 'issues_closed', 'issue_comments',
                        'issue_response_time', 'issue_resolution_duration', 'issue_age',
                        'code_change_lines_add', 'code_change_lines_remove',
                        'code_change_lines_sum', 'change_requests', 'change_requests_accepted',
                        'change_requests_reviews', 'change_request_response_time',
                        'change_request_resolution_duration', 'change_request_age',
                        'activity_details', 'developer_network', 'repo_network', 'project_openrank_detail']

    user_metric_list = ['openrank', 'activity', 'developer_network', 'repo_network']

    network_metric_list = ['developer_network', 'repo_network', 'project_openrank']

    no_stat_metric_list = ['active_dates_and_times', 'new_contributors_detail', 'bus_factor_detail',
                           'issue_response_time', 'issue_resolution_duration', 'issues_new',
                           'change_request_response_time', 'change_request_resolution_duration',
                           'change_request_age', 'activity_details']

    quantile_list_metric_list = ['issue_response_time', 'issue_resolution_duration', 'issues_new',
                                 'change_request_response_time', 'change_request_resolution_duration',
                                 'change_request_age']

    quantile_query_list = ['avg', 'levels', 'quantile_0', 'quantile_1', 'quantile_2', 'quantile_3', 'quantile_4']

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
            result_dict[metric]['month'] = dict()
            result_dict[metric]['stat'] = dict()

            try:
                response_content = Func.get_data(metric, option)
            except Exception:
                print('[ERROR] request data failed, please check if the input is correct')
                return

            for month in month_list:
                if month == 'all':
                    result_dict[metric]['month'] = response_content
                    break
                else:
                    if metric in Func.quantile_list_metric_list:
                        result_dict[metric]['month'][month] = dict()
                        for item in Func.quantile_query_list:
                            try:
                                result_dict[metric]['month'][month][item] = response_content[item][month]
                            except Exception:
                                result_dict[metric]['month'][month][item] = 'none'
                    else:
                        try:
                            result_dict[metric]['month'][month] = response_content[month]
                        except Exception:
                            result_dict[metric]['month'][month] = 'none'

            temp_data = result_dict[metric]['month']
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
                        result_dict[metric]['stat']['min'] = (minimum_value, minimum_keys)
                    elif stat == 'max':
                        maximum_value = sorted_data[-1][1]
                        maximum_keys = [item[0] for item in sorted_data if item[1] == maximum_value]
                        result_dict[metric]['stat']['max'] = (maximum_value, maximum_keys)
                    else:
                        middle_index = len(sorted_data) // 2
                        middle_value = sorted_data[middle_index][1]
                        middle_keys = [item[0] for item in sorted_data if item[1] == middle_value]
                        result_dict[metric]['stat']['avg'] = (middle_value, middle_keys)

        for metric in network_metric_list:
            result_dict[metric] = dict()
            result_dict[metric]['node'] = dict()
            result_dict[metric]['edge'] = dict()

            try:
                response_content = Func.get_data(metric, option)
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
                        result_dict[metric]['node'][item[0]] = dict()
                        result_dict[metric]['node'][item[0]]['weight'] = item[1]
                        result_dict[metric]['node'][item[0]]['neighbor'] = list(preprocess_edge_dict[item[0]].keys())
                    break
                else:
                    result_dict[metric]['node'][node] = dict()
                    try:
                        result_dict[metric]['node'][node]['weight'] = preprocess_node_dict[node]
                    except Exception:
                        result_dict[metric]['node'][node]['weight'] = 'none'

                    try:
                        result_dict[metric]['node'][node]['neighbor'] = list(preprocess_edge_dict[node].keys())
                    except Exception:
                        result_dict[metric]['node'][node]['neighbor'] = 'none'

            for edge in edge_list:
                if edge == 'all':
                    for node1, node2_list in preprocess_edge_dict.items():
                        for node2 in node2_list:
                            k = node1 + '+' + node2
                            try:
                                result_dict[metric]['edge'][k] = preprocess_edge_dict[node1][node2]
                            except Exception:
                                result_dict[metric]['edge'][k] = 'none'
                else:
                    # 要求格式为node1+node2
                    (node1, node2) = edge.split('+')
                    try:
                        result_dict[metric]['edge'][edge] = preprocess_edge_dict[node1][node2]
                    except Exception:
                        result_dict[metric]['edge'][edge] = 'none'

        return result_dict

    @staticmethod
    def print_result(result_dict, args):
        repo_name = args.repo.split('/')[-1]
        print(f'repo name: {repo_name}')
        print(f'repo url: https://github.com/{args.repo}')
        result_json = json.dumps(result_dict, indent=4)
        print(result_json)
        pass

    @staticmethod
    def ouput_pdf(result_dict, save_path, args):
        output_path = f'{save_path}report.pdf' if save_path[-1] == '/' else f'{save_path}/report.pdf'
        pdf = fpdf.FPDF(format='letter', unit='in')
        pdf.add_page()
        pdf.set_font('Times', '', 13)
        pdf.set_line_width(0.5)
        effective_page_width = pdf.w - 2*pdf.l_margin
        repo_name = args.repo.split('/')[-1]
        result_json = json.dumps(result_dict, indent=4)
        pdf.multi_cell(effective_page_width, 0.3, f'repo name: {repo_name}')
        pdf.multi_cell(effective_page_width, 0.3, f'repo url: https://github.com/{args.repo}')
        pdf.multi_cell(effective_page_width, 0.3, result_json)
        # for item in result_dict:
        #     pdf.multi_cell(effective_page_width, 0.2, f'{item}: {result_dict[item]}')
            # print(f"{item}: {result_dict[item]}")
        # pdf.image('./structure.png',w=6, h=6)
        # for item in args:
        #     pdf.multi_cell(effective_page_width, 0.2, f'{item[0]}: {item[1]}')
        pdf.output(output_path, 'F')

        return output_path

    @staticmethod
    def executive_request(args):
        repo = args.repo
        user = args.user
        metric = args.metric.lower()
        metric_list = args.metric_list
        month = args.month
        stat = args.stat
        download = args.download
        save_path = args.save_path
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
                for item in Func.repo_metric_list:
                    print(item)
            else:
                print('[INFO] The optional metric for the user is')
                for item in Func.user_metric_list:
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
            if metric in Func.network_metric_list:
                network_metric_list.append(metric)
            elif metric in Func.repo_metric_list:
                simple_metric_list.append(metric)
            else:
                print(f'[ERROR] {metric} does not exist')

        if len(network_metric_list) > 0 and len(network_metric_list) != len(temp_metric_list):
            print('[ERROR] can not query network and non-network metrics at the same time')
            return

        query_result_dict = Func.query(option=option, simple_metric_list=simple_metric_list,
                                       network_metric_list=network_metric_list, month_list=month_list,
                                       stat_list=stat_list, node_list=node_list, edge_list=edge_list)

        # debug
        # print(query_result_dict)

        if download:
            output_path = Func.ouput_pdf(query_result_dict, save_path, args)
            print('[INFO] the pdf output is completed and saved at ', output_path)
        else:
            Func.print_result(query_result_dict, args)
