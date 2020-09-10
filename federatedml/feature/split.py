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


class RandomSpliter(object):
    """
    Random Split Method

    Parameters
    ----------
    fraction : None or float,  spliting ratio, default: 0.1

    random_state: int, RandomState instance or None, optional, default: None

    """

    def __init__(self, fraction=0.1, random_state=None):
        self.fraction = fraction
        self.random_state = random_state
        self.tracker = None

    def set_tracker(self, tracker):
        self.tracker = tracker

    def sample(self, data_inst, sample_ids=None):
        """
        Interface to call random split method

        Parameters
        ----------
        data_inst : DTable
            The input data

        sample_ids : None or list
            if None, will sample data from the class instance's parameters,
            otherwise, it will be sample transform process, which means use the samples_ids to generate data

        Returns
        -------
        new_data_inst: DTable
            the output sample data, same format with input

        sample_ids: list, return only if sample_ids is None


        """

        if sample_ids is None:
            new_data_inst, sample_ids = self.__sample(data_inst)
            return new_data_inst, sample_ids
        else:
            new_data_inst = self.__sample(data_inst, sample_ids)
            return new_data_inst


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
        self.spliter = RandomSpliter(split_param.fractions,
                                        split_param.random_state)
        self.spliter.set_tracker(self.tracker)

        self.task_type = split_param.task_type
        self.fractions = split_param.fractions

    def _init_role(self, component_parameters):
        self.task_role = component_parameters["local"]["role"]

    def sample(self, data_inst, sample_ids=None):
        """
        Entry to use sample method

        Parameters
        ----------
        data_inst : DTable
            The input data

        sample_ids : None or list
            if None, will sample data from the class instance's parameters,
            otherwise, it will be sample transform process, which means use the samples_ids the generate data

        Returns
        -------
        sample_data: DTable
            the output sample data, same format with input
        """
        ori_schema = data_inst.schema
        sample_data = self._sample(data_inst, sample_ids)

        try:
            if len(sample_data) == 2:
                sample_data[0].schema = ori_schema
        except:
            sample_data.schema = ori_schema

        return sample_data

    def _sample(self, data_inst, sample_ids=None):
        """
        Interface to call random split method

        Parameters
        ----------
        data_inst : DTable
            The input data

        sample_ids : None or list
            if None, will sample data from the class instance's parameters,
            otherwise, it will be sample transform process, which means use the samples_ids to generate data

        Returns
        -------
        new_data_inst: DTable
            the output sample data, same format with input

        sample_ids: list, return only if sample_ids is None
        """

        if sample_ids is None:
            new_data_inst, sample_ids = self.__sample(data_inst)
            return new_data_inst, sample_ids
        else:
            new_data_inst = self.__sample(data_inst, sample_ids)
            return new_data_inst

    def __sample(self, data_inst, sample_ids=None):
        """
        Random sample method, a line's occur probability is decide by fraction
            support down sample and up sample
                if use down sample: should give a float ratio between [0, 1]
                otherwise: should give a float ratio larger than 1.0

        Parameters
        ----------
        data_inst : DTable
            The input data

        sample_ids : None or list
            if None, will sample data from the class instance's parameters,
            otherwise, it will be sample transform process, which means use the samples_ids to generate data

        Returns
        -------
        new_data_inst: DTable
            the output sample data, same format with input

        sample_ids: list, return only if sample_ids is None
        """
        LOGGER.info("start to run random spliting")

        return_sample_ids = False
        if self.method == "downsample":
            if sample_ids is None:
                return_sample_ids = True
                idset = [key for key, value in data_inst.mapValues(lambda val: None).collect()]
                if self.fraction < 0 or self.fraction > 1:
                    raise ValueError("sapmle fractions should be a numeric number between 0 and 1inclusive")

                sample_num = max(1, int(self.fraction * len(idset)))

                sample_ids = resample(idset,
                                      replace=False,
                                      n_samples=sample_num,
                                      random_state=self.random_state)

            sample_dtable = session.parallelize(zip(sample_ids, range(len(sample_ids))),
                                                include_key=True,
                                                partition=data_inst._partitions)
            new_data_inst = data_inst.join(sample_dtable, lambda v1, v2: v1)

            callback(self.tracker, [Metric("count", new_data_inst.count())])

            if return_sample_ids:
                return new_data_inst, sample_ids
            else:
                return new_data_inst

        elif self.method == "upsample":
            data_set = list(data_inst.collect())
            idset = [key for (key, value) in data_set]
            id_maps = dict(zip(idset, range(len(idset))))

            if sample_ids is None:
                return_sample_ids = True
                if self.fraction <= 0:
                    raise ValueError("sapmle fractions should be a numeric number large than 0")

                sample_num = int(self.fraction * len(idset))
                sample_ids = resample(idset,
                                      replace=True,
                                      n_samples=sample_num,
                                      random_state=self.random_state)

            new_data = []
            for i in range(len(sample_ids)):
                index = id_maps[sample_ids[i]]
                new_data.append((i, data_set[index][1]))

            new_data_inst = session.parallelize(new_data,
                                                include_key=True,
                                                partition=data_inst._partitions)

            callback(self.tracker, [Metric("count", new_data_inst.count())])

            if return_sample_ids:
                return new_data_inst, sample_ids
            else:
                return new_data_inst

        else:
            raise ValueError("random spliter not support method {} yet".format(self.method))

    def set_flowid(self, flowid="samole"):
        self.flowid = flowid

    def sync_sample_ids(self, sample_ids):
        transfer_inst = SampleTransferVariable()

        transfer_inst.sample_ids.remote(sample_ids,
                                        role="host",
                                        suffix=(self.flowid,))

    def recv_sample_ids(self):
        transfer_inst = SampleTransferVariable()

        sample_ids = transfer_inst.sample_ids.get(idx=0,
                                                  suffix=(self.flowid,))
        return sample_ids

    def run_sample(self, data_inst, task_type, task_role):
        """
        Sample running entry

        Parameters
        ----------
        data_inst : DTable
            The input data

        task_type : "homo" or "hetero"
            if task_type is "homo", it will sample standalone
            if task_type is "heterl": then spliting will be done in one side, after that
                the side sync the sample ids to another side to generated the same sample result

        task_role: "guest" or "host":
            only consider this parameter when task_type is "hetero"
            if task_role is "guest", it will firstly sample ids, and sync it to "host"
                to generate data instances with sample ids
            if task_role is "host": it will firstly get the sample ids result of "guest",
                then generate sample data by the receiving ids

        Returns
        -------
        sample_data_inst: DTable
            the output sample data, same format with input

        """
        LOGGER.info("begin to run spliting process")

        if task_type not in [consts.HOMO, consts.HETERO]:
            raise ValueError("{} task type not support yet".format(task_type))

        # res = self.sample(data_inst)[0]
        res = data_inst

        # data_set = list(data_inst.collect())
        # res = session.parallelize(data_set, include_key=True, partition=data_inst._partitions)
        # res.schema = data_inst.schema

        LOGGER.info(f"res={res}, count={res.count()}")
        LOGGER.info(f"res.meta={res.get_metas()}")
        LOGGER.info(f"res.name={res.get_name()}")
        LOGGER.info(f"res.namespace={res.get_namespace()}")
        LOGGER.info(f"res.partitions={res.get_partitions()}")

        data_res = []
        # data_res = [res for i in self.fractions]
        # data_res = [res.sample(1, 1) for i in self.fractions]
        # data_res = [res.take(100) for i in self.fractions]
        for i in self.fractions:
            _res = res.sample(i, 1)
            _res.schema = data_inst.schema
            data_res.append(_res)

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

        # if task_type == consts.HOMO:
        #     return self.sample(data_inst)[0]

        # elif task_type == consts.HETERO:
        #     if task_role == consts.GUEST:
        #         sample_data_inst, sample_ids = self.sample(data_inst)
        #         self.sync_sample_ids(sample_ids)

        #     elif task_role == consts.HOST:
        #         sample_ids = self.recv_sample_ids()
        #         sample_data_inst = self.sample(data_inst, sample_ids)

        #     else:
        #         raise ValueError("{} role not support yet".format(task_role))

        #     return sample_data_inst

    def fit(self, data_inst):
        return self.run_sample(data_inst, self.task_type, self.role)

    def transform(self, data_inst):
        return self.run_sample(data_inst, self.task_type, self.role)

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
    tracker.log_metric_data("sample_count",
                            "random",
                            callback_metrics)

    tracker.set_metric_meta("sample_count",
                            "random",
                            MetricMeta(name="sample_count",
                                        metric_type="SAMPLE_TEXT"))
