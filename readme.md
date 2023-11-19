# Opendigger-CLI产品设计文档 & 说明书


## 项目概况

本项目我们团队采用`Python Pip`包管理工具，将原本使用HTTPS URL的方式获取的OpenDigger统计指标改为用Command Line（命令行）获取，支持MacOS、Linux与Windows平台。在[这里](##安装说明)可以使用Pip安装或源码安装。

### 产品特点

- **功能丰富，形式多样。**该工具支持基础指标的查询，同时可以对各类数据进行统计分析和关系梳理，得到更丰富的指标细节。除此之外，该工具还能够导出开源项目健康报告，包括文字、统计图表等多种形式。
- **友好的人机交互。**输出格式整齐，信息提示完整，对用户更友好。这意味着使用该工具时，用户不仅可以获得详尽的数据分析结果，还能以直观易懂的方式呈现在屏幕上。
- **支持跨平台。**该工具可以在MacOS、Linux和Windows三个平台上运行，使得用户能够在不同的操作系统上享受相同的数据分析体验。
- **安装简单，使用方便。**该工具使用Pip包管理工具进行安装，用户只需要运行一条简单的命令就能够完成安装。使用方面也非常简单，用户只需要输入相关命令即可进行数据查询和分析。

### 文件结构
  - opendigger_cli
    - functions
      - __init__.py
      - common.py
      - base.py
      - metric_list.py
      - query_month.py
      - query_network.py
    - __init__.py
    - main.py
  - setup.py
  - requirements.txt

  主要源代码介绍
  1. main.py：读取控制台输入并进行解析，将输入args传递给各个查询子模块
  2. setup.py：用于生成打包源代码，生成.whl文件
  3. common.py：存放项目中的utils公共类和方法
  4. base.py：查询子模块基类，各个查询子模块需要继承该父类
  5. metric_list.py：查询子模块，列出Opendigger中所有的metric
  6. query_month.py：查询子模块，查询月份相关数据
  7. query_network.py：查询子模块，查询网络相关数据



## 功能设计

### 参数汇总

|               |        是否必选        |    作用    |
| :-----------: | :--------------------: | :--------: |
|    --repo     | --repo和--user两者选一 |  查询仓库  |
|    --user     | --repo和--user两者选一 |  查询用户  |
|   --metric    |          必选          |  查询指标  |
| --metric_list |          可选          | 查询指标组 |
|    --month    |          可选          |    月份    |
|    --stat     |          可选          |  统计数据  |
|  --download   |          可选          |  下载报告  |
|  --save_path  |          可选          |  保存路径  |
|    --node     |          可选          |  指定节点  |
|    --edge     |          可选          |   指定边   |



### 统计维度

使用者可以选择repo、user两种维度统计，本项目会根据用户的选择，提供不同的统计数据

- 参数设置：
  - --repo=仓库名【type：str】，例：--repo=X-lab2017/open-digger
  - --user=用户名【type：str】，例：--user=X-lab2017
- 详细说明 ：
  - 两种参数只能选择一种，都选或都不选会返回错误信息

### 评价指标

使用者可使用的OpenDigger中的统计指标，本项目会根据用户的选择而进一步筛选指标

- 参数设置
  - --metric=指标名，【type：str】，例：--metric=OpenRank
  - --metric_list，【type：store_true】，例：--metric_list
- 详细说明
  - --metric查询给出的metric的相应结果，如需查询所有指标输入**--metric=all**
  - --metric对大小写不敏感
  - --metric中对于有空格的指标，需将空格替换为下划线，如Issue age替换为Issue_age
  - --metric支持多选，内容以逗号划分并**不应键入多余空格**，如--metric=OpenRank,Activity,Attention
  - --metric_list查询对应统计维度中OpenDigger所提供的指标列表
  - --metric_list之后不应再输入其他字段和参数

### 指定自然月

本项目可以支持查询特定仓库在**特定自然月**上在特定指标上的数据，当输入指定的month时，查询所有json文件相应key为该month的数据

- 参数设置
  - --month=月份，【type：str】【default=all】，例：--month=2023-01
- 详细说明
  - --month支持多选，内容以逗号划分并**不应键入多余空格**，如--month=2023-01,2023-0

### 统计信息

对于key=month，value=数值的数据，我们可以提供min、max、avg等统计信息

- 参数设置
  - --stat=统计指标，【type：str】【可选列表：min、max、avg】，例：--stat=min
- 详细说明
  - --stat支持多选，内容以逗号划分并**不应键入多余空格**，例：--stat=min,max,avg

### 下载报告

本项目提供PDF格式的查询报告，用户可根据需要进行下载

- 参数设置
  - --download，【type：store_true】，例：--download
  - --save_path，【type：str】【default=./】，例--save_path=/home/xxx/xxx
- 详细说明
  - --save_path需要在之前先键入--download才能正常运行
  - 下载的pdf文件名默认为report.pdf

### Network指标图关系信息

使用者可查询Network指标中的节点与边的相关信息

- 参数设置

  - --node，【type：str】，例：--node=james
  - --edge，【type：str】，例：--edge=james+paul

- 详细说明

  - 该系列参数需要在--metric中键入Type=Network中存在的指标，且查询时不应同时包括network和非network指标，并不应结合--month与--stat使用

  - --node查询该节点的权重值与该节点的邻居，如需查询所有节点键入--node=all

  - --node支持多选，内容以逗号划分并**不应键入多余空格**，如--node=james,paul

  - --edge查询两个节点之间边的权重值，如需查询所有边键入--edge=all

  - --edge支持多选，内容以逗号划分并**不应键入多余空格**，如--edge=james+paul,harden+durant

    

## 安装说明:

- 源码安装

```Bash
# 下载
git clone https://github.com/LinRS1999/opendigger-cli.git

# 项目打包为whl
python setup.py bdist_wheel

# 进入dist文件夹
cd dist

# 使用pip工具安装，x.x.x视具体版本更改
pip install opendigger_cli-x.x.x-py3-none-any.whl --force-reinstall
```

- pip安装

```Bash
pip install opendigger_cli -i https://pypi.org/simple
```

- 环境配置说明

  - Python 3.8+

    

## 执行样例

### 快速开始

```python
opendigger-cli [--repo] [--metric] [--month] [--stat] [--download]
opendigger-cli --repo X-lab2017/open-digger --metric openrank,activity --month all --stat avg,min,max --download
```

### 查询仓库

#### 查询X-lab2017/open-digger仓库

​	**在所有月份上OpenRank和Activity指标上的数据，并对其计算平均值、最大值和最小值**

- 命令：`opendigger-cli --repo X-lab2017/open-digger --metric openrank,activity --month all --stat avg,min,max`

#### 查询X-lab2017/oss101仓库

​	**在2023-01,2023-02,2023-03,2023-04,2023-05,2023-06月份上Attention和Stars指标上的数据，并对其计算平均值、最大值和最小值，并下载，其下载地址为当前目录的report.pdf**

- 命令: `opendigger-cli --repo X-lab2017/oss101 --metric attention,stars --month 2023-01,2023-02,2023-03,2023-04,2023-05,2023-06  --stat avg,min,max --download`

### 查询用户

​	**查询will-ww用户在所有月份上OpenRank指标上的数据，并对其计算平均值、最大值和最小值，并下载，其下载地址为当前目录的report.pdf**

- 命令：`opendigger-cli --user will-ww --metric openrank --month all  --download`

### 查询Network指标

**查询X-lab2017/open-digger仓库的Develop network指标中frank-zsy和xgdyp的权重和其邻居节点名，同时查询xgdyp和frank-zsy、xgdyp和will-ww两者之间的权重值**

- 命令：`opendigger-cli --repo X-lab2017/open-digger --metric developer_network --node frank-zsy,xgdyp --edge xgdyp+frank-zsy,xgdyp+will-ww`

**查询X-lab2017/oss101仓库的Develop network指标中will-ww的权重和其邻居节点名，同时查询will-ww和TieWay59两者之间的权重值**

- 命令：`opendigger-cli --repo X-lab2017/oss101 --metric developer_network --node will-ww --edge will-ww+TieWay59 --download`




## 二次开发指南

  - 本项目已封装好请求数据、控制台输出等功能于common.py，如：
    1. 请求数据：request_json_data()
    2. 控制台输出：PrintUtil()
  - 二次开发时，补充以下伪代码就可以开发新的命令行查询功能
  ```
  # 1. 在main.py的setup_parser()中加入xxx指标
  parser.add_argument('--xxx', type=str, help='xxx')

  # 2. 在functions中声明一个查询子模块类，并继承父类Base，实现其预定义的功能
  class Base:
      def __init__(self):
          pass

      def check_args(self, args):
          # 检查args合法性并根据args判断是否调用cal方法计算
          raise NotImplementedError

      def cal(self):
          # 获取数据，计算指标
          raise NotImplementedError

      def run(self, args):
          # 调用check_args、cal或其他自定义方法
          raise NotImplementedError

  # 3. 在__init__.py中补充
  from .query_network import QueryNetwork
  from .query_month import QueryMonth
  from .metric_list import MetricList
  from .xxx import xxx

  __all__ = 'QueryMonth', 'QueryNetwork', 'MetricList', 'xxx'

  # 4. 在main.py的main()函数中自定义指标子模块查询优先级顺序
  # 实例化类并调用run方法 

  def main():
      parser = setup_parser()
      args = parser.parse_args()

      metric_list_class = MetricList()
      metric_list_class.run(args)

      query_month_class = QueryMonth()
      query_month_class.run(args)

      query_network_class = QueryNetwork()
      query_network_class.run(args)
      
      xxx_class = xxx()
      xxx_class.run(args)
  ```