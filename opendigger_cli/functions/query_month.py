import os
import fpdf
import json

from .base import Base
from .common import print_util, project_config, request_json_data
from fuzzywuzzy import process
from datetime import datetime
import matplotlib.pyplot as plt


class QueryMonth(Base):
    def __init__(self):
        super().__init__()
        self.option = None

        self.metric_list = None
        self.month_list = None
        self.stat_list = None

        self.download = None
        self.save_path = None

        self.result_dict = dict()
        self.response_contents = []

        self.quantile_metric_list = ['issue_response_time', 'issue_resolution_duration', 'issues_new',
                                     'change_request_response_time', 'change_request_resolution_duration',
                                     'change_request_age']
        self.quantile_query_list = ['avg', 'levels', 'quantile_0', 'quantile_1',
                                    'quantile_2', 'quantile_3', 'quantile_4']

        self.no_stat_metric_list = ['active_dates_and_times', 'new_contributors_detail', 'bus_factor_detail',
                                    'issue_response_time', 'issue_resolution_duration', 'issues_new',
                                    'change_request_response_time', 'change_request_resolution_duration',
                                    'change_request_age', 'activity_details']

        self.draw_metric_list = ['openrank', 'activity', 'attention',
                                 'stars', 'technical_fork', 'participants', 'new_contributors',
                                 'inactive_contributors', 'bus_factor',
                                 'issues_new', 'issues_closed', 'issue_comments',
                                 'code_change_lines_add', 'code_change_lines_remove',
                                 'code_change_lines_sum', 'change_requests', 'change_requests_accepted',
                                 'change_requests_reviews']

        self.network_metric_list = ['developer_network', 'repo_network', 'project_openrank']

    def check_args(self, args):
        repo = args.repo
        user = args.user
        metric = args.metric

        month = args.month
        stat = args.stat

        download = args.download
        save_path = args.save_path

        self.download = True if download else False
        self.save_path = save_path if save_path else './'

        if not os.path.exists(self.save_path):
            os.makedirs(save_path)
            print_util.warn(f"Directory '{self.save_path}' not exists, created")

        if download and not save_path:
            print_util.warn('The save_path is not specified, '
                            'the pdf file will be saved in the current working directory')

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

                if match_res[0] not in self.network_metric_list:
                    corrected_metric_list.append(match_res[0])
        if user:
            for temp_metric in temp_metric_list:
                match_res = process.extractOne(temp_metric, project_config.USER_METRIC_LIST)

                if match_res[1] != 100:
                    print_util.warn(f'The metric of the query: {temp_metric} does not exist in all computable metrics.'
                                    f' You may be referring to {match_res[0]}. Next, {match_res[0]} will be used to '
                                    f'calculate the metric')

                if match_res[0] not in self.network_metric_list:
                    corrected_metric_list.append(match_res[0])
        self.metric_list = corrected_metric_list

        temp_month_list = month.split(',') if month else []
        corrected_month_list = []
        all_flag = False
        for month in temp_month_list:
            if month == 'all':
                all_flag = True
                break
            try:
                datetime.strptime(month, "%Y-%m")
                corrected_month_list.append(month)
            except ValueError:
                print_util.warn(f'Date format error: {month}, this will not be calculated next')

        if all_flag:
            corrected_month_list = ['all']
        self.month_list = corrected_month_list

        temp_stat_list = stat.split(',') if stat else list()
        corrected_stat_list = []
        for stat in temp_stat_list:
            if stat not in ['avg', 'min', 'max']:
                print_util.warn(f'Stat format error: {stat}, this will not be calculated next')
            else:
                corrected_stat_list.append(stat)
        self.stat_list = corrected_stat_list

    def cal(self):
        for i, metric in enumerate(self.metric_list):
            self.result_dict[metric] = dict()
            self.result_dict[metric]['month'] = dict()
            self.result_dict[metric]['stat'] = dict()

            response_content = request_json_data(metric, self.option)
            self.response_contents.append(response_content)

            for month in self.month_list:
                if month == 'all':
                    self.result_dict[metric]['month'] = response_content
                else:
                    if metric in self.quantile_metric_list:
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

            if len(self.stat_list) and len(data.keys()):
                sorted_data = sorted(data.items(), key=lambda x: x[1])

                for stat in self.stat_list:
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

        return self.result_dict

    def print_pic(self, name, xlabel, ylabel, json_data, path=None):
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

    def output_pdf(self):
        """
        将结果输出至PDF中
        :param args:
        :param metric_list:
        :return:
        """
        output_path_pdf = f'{self.save_path}report.pdf' if self.save_path[-1] == '/' else f'{self.save_path}/report.pdf'

        pdf = fpdf.FPDF(format='letter', unit='in')
        pdf.add_page()
        pdf.set_font('Times', '', 13)
        pdf.set_line_width(0.5)
        effective_page_width = pdf.w - 2*pdf.l_margin

        result_json = json.dumps(self.result_dict)
        if '/' in self.option:
            pdf.multi_cell(effective_page_width, 0.3, f'repo name: {self.option}')
            pdf.multi_cell(effective_page_width, 0.3, f'repo url: https://github.com/{self.option}')
        else:
            pdf.multi_cell(effective_page_width, 0.3, f'user name: {self.option}')
            pdf.multi_cell(effective_page_width, 0.3, f'user url: https://github.com/{self.option}')

        pdf.multi_cell(effective_page_width, 0.3, result_json)

        jpg_list = list()
        for i, res in enumerate(self.response_contents):
            can_print = self.metric_list[i] in self.draw_metric_list

            if can_print is False:
                print_util.warn(f'{self.metric_list[i]} cannot be visualized')
                continue
            output_path_jpg = f'{self.save_path}picture{i}.jpg' if self.save_path[-1] == '/' else f'{self.save_path}/picture{i}.jpg'
            self.print_pic(f'{self.metric_list[i]} for {self.option}', 'time', self.metric_list[i], res, output_path_jpg)
            jpg_list.append(output_path_jpg)
            pdf.image(output_path_jpg, w=6, h=4.5)
        pdf.output(output_path_pdf, 'F')

        for item in jpg_list:
            os.remove(item)

        print_util.info(f'the pdf output is completed and saved at {output_path_pdf}')
        return output_path_pdf

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
        if self.download:
            self.output_pdf()

        if len(self.result_dict):
            self.print_result()
            exit(0)
