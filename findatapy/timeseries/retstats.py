__author__ = 'saeedamen' # Saeed Amen

#
# Copyright 2016 Cuemacro
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and limitations under the License.
#

import math
import pandas

from findatapy.timeseries.calculations import Calculations


class RetStats(object):
    """Calculating return statistics of a time series

    """

    def calculate_ret_stats_from_prices(self, prices_df, ann_factor):
        """Calculates return statistics for an asset's price

        Parameters
        ----------
        prices_df : DataFrame
            asset prices
        ann_factor : int
            annualisation factor to use on return statistics

        Returns
        -------
        DataFrame
        """
        calculations = Calculations()

        self.calculate_ret_stats(calculations.calculate_returns(prices_df), ann_factor)

    def calculate_ret_stats(self, returns_df, ann_factor):
        """Calculates return statistics for an asset's returns including IR, vol, ret and drawdowns

        Parameters
        ----------
        returns_df : DataFrame
            asset returns
        ann_factor : int
            annualisation factor to use on return statistics

        Returns
        -------
        DataFrame
        """

        # TODO work on optimizing this method
        self._rets = returns_df.mean(axis=0) * ann_factor
        self._vol = returns_df.std(axis=0) * math.sqrt(ann_factor)
        self._inforatio = self._rets / self._vol
        self._kurtosis = returns_df.kurtosis(axis=0) / math.sqrt(ann_factor)

        index_df = (1.0 + returns_df).cumprod()

        if pandas.__version__ < '0.17':
            max2here = pandas.expanding_max(index_df)
        else:
            max2here = index_df.expanding(min_periods=1).max()

        dd2here = index_df / max2here - 1

        self._dd = dd2here.min()
        self._yoy_rets = index_df.resample('A').mean().pct_change()

        return self

    def ann_returns(self):
        """Gets annualised returns

        Returns
        -------
        float
        """
        return self._rets

    def ann_vol(self):
        """Gets annualised volatility

        Returns
        -------
        float
        """
        return self._vol

    def inforatio(self):
        """Gets information ratio

        Returns
        -------
        float
        """
        return self._inforatio

    def drawdowns(self):
        """Gets drawdowns for an asset or strategy

        Returns
        -------
        float
        """
        return self._dd

    def kurtosis(self):
        """Gets kurtosis for an asset or strategy

        Returns
        -------
        float
        """
        return self._kurtosis

    def yoy_rets(self):
        """Calculates the yoy rets

        Returns
        -------
        float
        """
        return self._yoy_rets

    def summary(self):
        """Gets summary string contains various return statistics

        Returns
        -------
        str
        """
        stat_list = []

        for i in range(0, len(self._rets.index)):
            stat_list.append(self._rets.index[i] + " Ret = " + str(round(self._rets[i] * 100, 1))
                             + "% Vol = " + str(round(self._vol[i] * 100, 1))
                             + "% IR = " + str(round(self._inforatio[i], 2))
                             + " Dr = " + str(round(self._dd[i] * 100, 1))
                             + "% Kurt = " + str(round(self._kurtosis[i], 2)))

        return stat_list