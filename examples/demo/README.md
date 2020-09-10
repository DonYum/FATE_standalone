
### 数据

数据操作针对的都是local role，所以操作的role都是`local`。

#### 上传数据

python fate_flow/fate_flow_client.py -f upload -c examples/federatedml-1.x-examples/upload_data.json
python fate_flow/fate_flow_client.py -f upload -c examples/federatedml-1.x-examples/upload_data_host.json
python fate_flow/fate_flow_client.py -f upload -c examples/federatedml-1.x-examples/upload_data_guest.json

python fate_flow/fate_flow_client.py -f upload -c examples/confs/upload_data_guest.json
python fate_flow/fate_flow_client.py -f upload -c examples/confs/upload_data_host.json

#### 查看数据????

#### 下载数据
python fate_flow/fate_flow_client.py -f download_test -c examples/confs/download.json
python fate_flow_client.py -f download -n table_namespace -t table_name -w work_mode -o save_file

#### 导出model output data
python fate_flow_client.py -f component_output_model -j $job_id -r $role -p $party_id -cpn $component_name -o $output_path

### 任务

#### 提交DSL

- python fate_flow/fate_flow_client.py -f submit_job -d examples/confs/job_dsl.json -c examples/confs/job_runtime_conf.json
- python fate_flow/fate_flow_client.py -f submit_job -d examples/confs/download_dsl.json -c examples/confs/download_conf.json
- python fate_flow/fate_flow_client.py -f submit_job -d examples/confs/sample_test_dsl.json -c examples/confs/sample_test_conf.json

- pipeline：
    python fate_flow/fate_flow_client.py -f submit_job -d examples/federatedml-1.x-examples/multi_model_pipeline/test_multi_pipeline_dsl.json -c examples/federatedml-1.x-examples/multi_model_pipeline/test_multi_pipeline_conf.json

- python fate_flow/fate_flow_client.py -f submit_job -d examples/confs/test_1_dsl.json -c examples/confs/test_1_conf.json

#### 查看job状态
python fate_flow/fate_flow_client.py -f query_job -r guest -p 10000 -j 202008311115403110241


#### 查看logs
python fate_flow_client.py -f job_log -j $jobid -o $output_dir


#### predict

#### evaluation

#### model export
