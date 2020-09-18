
### jq

python fate_flow/fate_flow_client.py -f upload -c jq/upload_hetero_guest.json -drop 0
python fate_flow/fate_flow_client.py -f upload -c jq/upload_hetero_host.json -drop 0
python fate_flow/fate_flow_client.py -f submit_job -d jq/submit_hetero_dsl.json -c jq/submit_hetero_conf.json

python fate_flow/fate_flow_client.py -f upload -c jq/upload_homo_guest.json -drop 0
python fate_flow/fate_flow_client.py -f upload -c jq/upload_homo_host.json -drop 0

### 数据

数据操作针对的都是local role，所以操作的role都是`local`。

#### 上传数据

python fate_flow/fate_flow_client.py -f upload -c examples/federatedml-1.x-examples/upload_data.json
python fate_flow/fate_flow_client.py -f upload -c examples/federatedml-1.x-examples/upload_data_host.json
python fate_flow/fate_flow_client.py -f upload -c examples/federatedml-1.x-examples/upload_data_guest.json

python fate_flow/fate_flow_client.py -f upload -c examples/demo/upload_data_guest.json
python fate_flow/fate_flow_client.py -f upload -c examples/demo/upload_data_host.json

#### 下载数据

- python fate_flow_client.py -f download -n table_namespace -t table_name -w work_mode -o save_file

##### 测试fake component

- python fate_flow/fate_flow_client.py -f download_test -c examples/demo/download.json
- python fate_flow/fate_flow_client.py -f submit_job -d examples/demo/download_dsl.json -c examples/demo/download_conf.json

#### 查看数据????

#### 导出model output data

python fate_flow_client.py -f component_output_model -j $job_id -r $role -p $party_id -cpn $component_name -o $output_path

### 任务

#### 提交DSL

- python fate_flow/fate_flow_client.py -f submit_job -d examples/demo/job_dsl.json -c examples/demo/job_runtime_conf.json
- python fate_flow/fate_flow_client.py -f submit_job -d examples/demo/sample_test_dsl.json -c examples/demo/sample_test_conf.json

- pipeline：

    python fate_flow/fate_flow_client.py -f submit_job -d examples/federatedml-1.x-examples/multi_model_pipeline/test_multi_pipeline_dsl.json -c examples/federatedml-1.x-examples/multi_model_pipeline/test_multi_pipeline_conf.json

- split:

    python fate_flow/fate_flow_client.py -f submit_job -d examples/demo/split_3_dsl.json -c examples/demo/split_3_conf.json
    python fate_flow/fate_flow_client.py -f submit_job -d examples/demo/split_2_2_dsl.json -c examples/demo/split_2_2_conf.json
    python fate_flow/fate_flow_client.py -f submit_job -d examples/demo/split_4_dsl.json -c examples/demo/split_4_conf.json

#### 查看job状态
python fate_flow/fate_flow_client.py -f query_job -r guest -p 10000 -j 202008311115403110241


#### 获取配置

python fate_flow/fate_flow_client.py -f job_config -j   202002280915402308774 -r guest -p 10000 -o examples/federatedml-1.x-examples/homo_logistic_regression

#### 查看logs
python fate_flow_client.py -f job_log -j $jobid -o $output_dir


### 测试Join

python fate_flow/fate_flow_client.py -f upload -c examples/demo/upload_data.json

python fate_flow/fate_flow_client.py -f submit_job -d examples/federatedml-1.x-examples/intersect/test_intersect_without_dataio_job_dsl.json -c examples/federatedml-1.x-examples/intersect/test_intersect_without_dataio_job_conf.json

#### predict

#### evaluation

#### model export
