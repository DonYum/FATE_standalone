# FATE_standalone
FATE standalone based on master(2020.09.09)

## Quickly Start

#### 准备images：

```sh
wget https://webank-ai-1251170195.cos.ap-guangzhou.myqcloud.com/docker_standalone-fate-1.4.3.tar.gz
tar -xzvf docker_standalone-fate-1.4.3.tar.gz
cd docker_standalone-fate-1.4.3

docker load < python.tar
docker load < fateboard.tar
docker images
```

此时可以看到`docker_fateboard`和`docker_python`两个镜像。

#### 启动docker-compose

```sh
git clone https://github.com/DonYum/FATE_standalone.git
cd FATE_standalone
docker-compose -f docker_compose.yml up
```

这是可以在`http://{fateboard-serverip}:8080/`看到fateboard页面。

FATE_standalone下面的`fate_flow`、`federatedml`、`examples`是挂载在docker容器中的，可以直接在外面修改。

注意：修改`federatedml`组件、`examples`下面的代码不用重启服务——`federatedml`组件是通过插件方式接入的，其他部分修改，比如修改`fate_flow`下面的代码，就需要重启服务了。

## 组件开发

新组件的

### fake component

##### commits

- `ee8873499028a32b80f847f8b981bfbf3fe8aba1`: Add Fake component - using Download.
- `85400cfd4f558526a9007e01513da911e94a8dd0`: 将新的component封装进fate_flow RESTful接口和fate_flow_cli。

##### 测试

```sh
# 上传数据
python fate_flow/fate_flow_client.py -f upload -c examples/federatedml-1.x-examples/upload_data.json
# 使用sub_job方式下载
python fate_flow/fate_flow_client.py -f submit_job -d examples/demo/download_dsl.json -c examples/demo/download_conf.json
# 使用download_test功能选项直接下载
python fate_flow/fate_flow_client.py -f download_test -c examples/demo/download.json
```

### split

##### commits

- `d5ec883994e3d9e081332bf7ba8ca51acb1bd3b1`: 实现split组件。
- `1c112cf492b521069ca9a9b371e0039ac476c178`: 添加两个split Demo。
- `9dbac830e5f0d6864fcad1bcb57bcfcc904d9f39`: split: 简化代码。
- `c8eb184310fa5659ccab6fe48feb86f60338136d`: split：添加random_seed参数

##### 组件参数

```txt
"random_seed": 1          # int. 随机数种子，不同role之间需要使用相同种子，这样才能产生相同切分数据集。
"fractions": [0.8, 0.2]   # float list. 切分得到的数据集比例。需满足条件：长度不为零，sum(fractions) == 1.
```

##### 测试

```sh
# 上传数据
python fate_flow/fate_flow_client.py -f upload -c examples/demo/upload_data_guest.json
python fate_flow/fate_flow_client.py -f upload -c examples/demo/upload_data_host.json
# 测试三种组合方式
python fate_flow/fate_flow_client.py -f submit_job -d examples/demo/split_3_dsl.json -c examples/demo/split_3_conf.json
python fate_flow/fate_flow_client.py -f submit_job -d examples/demo/split_2_2_dsl.json -c examples/demo/split_2_2_conf.json
python fate_flow/fate_flow_client.py -f submit_job -d examples/demo/split_4_dsl.json -c examples/demo/split_4_conf.json
```

##### TODO

这个版本是为了把流程串起来，还有缺陷，比如使用sample方法切分会导致数据集之间有重合。

TODOs:

- 添加take方法；
- sample方法需要添加去重功能。

## 通信模式

在`standalone`模式下，`fate_flow`和`fate_board`通过`jdbc:sqlite:/fate/fate_flow/fate_flow_sqlite.db`通信。
因此需要将这两个文件夹打通。
