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
python -m opendigger-cli --repo X-lab2017/open-digger --metric OpenRank --month 2023-01

python -m opendigger-cli --repo X-lab2017/open-digger --metric OpenRank
~~~

![image-20230515173401597](C:\Users\LinRS\AppData\Roaming\Typora\typora-user-images\image-20230515173401597.png)