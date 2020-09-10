#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from arch.api import session
from arch.api.utils import log_utils
from sklearn.utils import resample
from fate_flow.entity.metric import Metric
from fate_flow.entity.metric import MetricMeta
from federatedml.param.split_param import SplitParam
from federatedml.util import consts
from federatedml.transfer_variable.transfer_class.sample_transfer_variable import SampleTransferVariable
from federatedml.model_base import ModelBase
import random

LOGGER = log_utils.getLogger()


class Spliter(ModelBase):
    """
    Split Object

    Parameters
    ----------
    split_param : object, self-define split parameters,
        define in federatedml.param.split_param

    """

    def __init__(self):
        super(Spliter, self).__init__()
        self.task_type = None
        # self.task_role = None
        self.flowid = 0
        self.model_param = SplitParam()

    def _init_model(self, split_param):
        self.task_type = split_param.task_type
        self.fractions = split_param.fractions
        self.random_seed = split_param.random_seed or 1

    def _init_role(self, component_parameters):
        self.task_role = component_parameters["local"]["role"]

    def set_flowid(self, flowid="split"):
        self.flowid = flowid

    def run_split(self, data_inst, task_type, task_role):
        """
        Sample running entry

        Parameters
        ----------
        data_inst : DTable
            The input data

        Returns
        -------
        split_data_inst: DTable
            the output split data, same format with input

        """
        LOGGER.info("begin to run spliting process")

        if task_type not in [consts.HOMO, consts.HETERO]:
            raise ValueError("{} task type not support yet".format(task_type))

        # res = self.sample(data_inst)[0]
        res = data_inst

        # data_set = list(data_inst.collect())
        # res = session.parallelize(data_set, include_key=True, partition=data_inst._partitions)
        # res.schema = data_inst.schema

        LOGGER.info(f"random_seed={self.random_seed()}")
        LOGGER.info(f"res={res}, count={res.count()}")
        LOGGER.info(f"res.meta={res.get_metas()}")
        LOGGER.info(f"res.name={res.get_name()}")
        LOGGER.info(f"res.namespace={res.get_namespace()}")
        LOGGER.info(f"res.partitions={res.get_partitions()}")

        data_res = []
        # data_res = [res for i in self.fractions]
        # data_res = [res.sample(1, self.random_seed) for i in self.fractions]
        # data_res = [res.take(100) for i in self.fractions]
        for i in self.fractions:
            _res = res.sample(i, self.random_seed)
            _res.schema = data_inst.schema
            data_res.append(_res)

        # For debugging
        LOGGER.info(f"type={data_res}, {res}")

        try:
            LOGGER.info(f"res.count={[i.count() for i in data_res]}")
        except:
            pass

        try:
            LOGGER.info(f"res.first()={res.first()}")
        except:
            pass
        try:
            LOGGER.info(f"res.first()[1].features={res.first()[1].features}")
        except:
            pass

        try:
            for i in range(len(data_res)):
                LOGGER.info(f"data_res[{i}].first()={data_res[i].first()}")
        except:
            pass
        try:
            for i in range(len(data_res)):
                LOGGER.info(f"data_res[{i}].first()[1].features={data_res[i].first()[1].features}")
        except:
            pass

        self.data_output = data_res         # !!!!!!

        return data_res

    def fit(self, data_inst):
        return self.run_split(data_inst, self.task_type, self.role)

    def transform(self, data_inst):
        return self.run_split(data_inst, self.task_type, self.role)

    def check_consistency(self):
        pass

    """
    def run(self, component_parameters, args=None):
        self._init_runtime_parameters(component_parameters)
        self._init_role(component_parameters)
        stage = "fit"
        if args.get("data", None) is None:
            return

        self._run_data(args["data"], stage)
    """

    def save_data(self):
        return self.data_output


def callback(tracker, callback_metrics, other_metrics=None):
    tracker.log_metric_data("split_count",
                            "random",
                            callback_metrics)

    tracker.set_metric_meta("split_count",
                            "random",
                            MetricMeta(name="split_count",
                                        metric_type="SAMPLE_TEXT"))
