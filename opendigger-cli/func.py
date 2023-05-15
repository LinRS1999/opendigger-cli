import requests


class Func:
    _url_start = 'https://oss.x-lab.info/open_digger/github/X-lab2017/open-digger/'
    _url_end = '.json'

    @staticmethod
    def _get(url):
        response = requests.get(url)
        response_content = eval(response.content.decode())

        return response_content

    @staticmethod
    def _print_consle(*args):
        print('repo name: open-digger')
        print('repo url: https://github.com/X-lab2017/open-digger')

        for item in args:
            print(f'{item[0]}: {item[1]}')

    @staticmethod
    def _example_one(metric):
        metric = metric.lower().replace(' ', '_')
        url = Func._url_start + metric + Func._url_end
        response_content = Func._get(url)
        Func._print_consle((metric, response_content))

    @staticmethod
    def _example_two(metric, month):
        metric = metric.lower().replace(' ', '_')
        url = Func._url_start + metric + Func._url_end
        response_content = Func._get(url)
        metric_result = response_content[month]
        Func._print_consle(('month', month), (metric, metric_result))

    @staticmethod
    def executive_request(args):
        metric = args.metric
        month = args.month
        if metric and not month:
            Func._example_one(metric)
        elif metric and month:
            Func._example_two(metric, month)

