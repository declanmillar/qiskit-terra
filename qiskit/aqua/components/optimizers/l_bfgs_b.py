# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

import logging

from scipy import optimize as sciopt

from qiskit.aqua.components.optimizers import Optimizer

logger = logging.getLogger(__name__)


class L_BFGS_B(Optimizer):
    """Limited-memory BFGS algorithm.

    Uses scipy.optimize.fmin_l_bfgs_b
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fmin_l_bfgs_b.html
    """

    CONFIGURATION = {
        'name': 'L_BFGS_B',
        'description': 'L_BFGS_B Optimizer',
        'input_schema': {
            '$schema': 'http://json-schema.org/schema#',
            'id': 'l_bfgs_b_schema',
            'type': 'object',
            'properties': {
                'maxfun': {
                    'type': 'integer',
                    'default': 1000
                },
                'maxiter': {
                    'type': 'integer',
                    'default': 15000
                },
                'factr': {
                    'type': 'integer',
                    'default': 10
                },
                'iprint': {
                    'type': 'integer',
                    'default': -1
                },
                'epsilon': {
                    'type': 'number',
                    'default': 1e-08
                }
            },
            'additionalProperties': False
        },
        'support_level': {
            'gradient': Optimizer.SupportLevel.supported,
            'bounds': Optimizer.SupportLevel.supported,
            'initial_point': Optimizer.SupportLevel.required
        },
        'options': ['maxfun', 'maxiter', 'factr', 'iprint', 'epsilon'],
        'optimizer': ['local']
    }

    def __init__(self, maxfun=1000, maxiter=15000, factr=10, iprint=-1, epsilon=1e-08):
        """
        Constructor.

        For details, please refer to
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fmin_l_bfgs_b.html

        Args:
            maxfun (int): Maximum number of function evaluations.
            maxiter (int): Maximum number of iterations.
            factr (float): The iteration stops when (f^k - f^{k+1})/max{|f^k|,
                           |f^{k+1}|,1} <= factr * eps, where eps is the machine precision,
                           which is automatically generated by the code. Typical values for
                           factr are: 1e12 for low accuracy; 1e7 for moderate accuracy;
                           10.0 for extremely high accuracy. See Notes for relationship to ftol,
                           which is exposed (instead of factr) by the scipy.optimize.minimize
                           interface to L-BFGS-B.
            iprint (int): Controls the frequency of output. iprint < 0 means no output;
                          iprint = 0 print only one line at the last iteration; 0 < iprint < 99
                          print also f and |proj g| every iprint iterations; iprint = 99 print
                          details of every iteration except n-vectors; iprint = 100 print also the
                          changes of active set and final x; iprint > 100 print details of
                          every iteration including x and g.
            epsilon (float): Step size used when approx_grad is True, for numerically
                             calculating the gradient
        """
        self.validate(locals())
        super().__init__()
        for k, v in locals().items():
            if k in self._configuration['options']:
                self._options[k] = v

    def optimize(self, num_vars, objective_function, gradient_function=None, variable_bounds=None, initial_point=None):
        super().optimize(num_vars, objective_function, gradient_function, variable_bounds, initial_point)

        if gradient_function is None and self._batch_mode:
            epsilon = self._options['epsilon']
            gradient_function = Optimizer.wrap_function(Optimizer.gradient_num_diff, (objective_function, epsilon))

        approx_grad = True if gradient_function is None else False
        sol, opt, info = sciopt.fmin_l_bfgs_b(objective_function, initial_point, bounds=variable_bounds,
                                              fprime=gradient_function, approx_grad=approx_grad, **self._options)

        return sol, opt, info['funcalls']
