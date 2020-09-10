#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from federatedml.param.base_param import BaseParam
import collections


class SplitParam(BaseParam):
    """
    Define the split method

    Parameters
    ----------
    mode: str, accepted 'random','stratified'' only in this version, specify split to use, default: 'random'

    fractions: list, e.g. [0.5, 0.3, 0.2].

    random_state: int, RandomState instance or None, default: None

    need_run: bool, default True
        Indicate if this module needed to be run
    """

    def __init__(self, mode="random", fractions=None, random_state=None, task_type="hetero", need_run=True):
        self.mode = mode
        self.fractions = fractions
        self.random_state = random_state
        self.task_type = task_type
        self.need_run = need_run

    def check(self):
        descr = "split param"
        self.mode = self.check_and_change_lower(self.mode,
                                                ["random", "stratified"],
                                                descr)

        if self.mode == "stratified" and self.fractions is not None:
            if not isinstance(self.fractions, list):
                raise ValueError("fractions of split param when using stratified should be list")
            for ele in self.fractions:
                if not isinstance(ele, float):
                    raise ValueError("element in fractions of split param should be a float list")
            if abs(1-sum(self.fractions)) > 0.000001:
                raise ValueError(f"fractions sum of split param should be 1.0. {self.fractions}, {sum(self.fractions)}")

        return True
