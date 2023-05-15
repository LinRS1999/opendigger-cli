### opendigger-cli

---



~~~bash
1. 项目打包为whl
python setup.py bdist_wheel

2. 进入build文件夹
cd build

3. 安装pip
pip install opendigger_cli-1.0-py3-none-any.whl --force-reinstall

4. cmd测试
PS C:\Users\LinRS> python -m opendigger-cli --repo X-lab2017/open-digger --metric OpenRank
repo name: open-digger
repo url: https://github.com/X-lab2017/open-digger
openrank: {'2020-08': 4.5, '2020-09': 4.91, '2020-10': 5.59, '2020-11': 6.31, '2020-12': 9.96, '2021-01': 10.61, '2021-02': 6.28, '2021-03': 4.14, '2021-04': 4.44, '2021-05': 4.26, '2021-06': 6.46, '2021-07': 4.84, '2021-08': 3.93, '2021-09': 3.34, '2021-10': 3, '2021-11': 2.89, '2021-12': 3.33, '2022-01': 4.71, '2022-02': 4.87, '2022-03': 6.06, '2022-04': 3.76, '2022-05': 4.14, '2022-06': 7.67, '2022-07': 9.17, '2022-08': 8.53, '2022-09': 9.96, '2022-10': 11.84, '2022-11': 14.65, '2022-12': 19.36, '2023-01': 19.9, '2023-02': 40.48, '2023-03': 22.05, '2023-04': 18.79, '2021-10-raw': 2.84}

PS C:\Users\LinRS> python -m opendigger-cli --repo X-lab2017/open-digger --metric OpenRank --month 2023-01
repo name: open-digger
repo url: https://github.com/X-lab2017/open-digger
month: 2023-01
openrank: 19.9
~~~
