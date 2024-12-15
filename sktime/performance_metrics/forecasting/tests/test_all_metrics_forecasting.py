"""Tests for all sktime forecasting metrics - point forecasts."""

import numpy as np
import pandas as pd
import pytest

from sktime.tests.test_all_estimators import BaseFixtureGenerator, QuickTester
from sktime.utils._testing.panel import _make_panel
from sktime.utils._testing.series import _make_series
from sktime.utils.parallel import _get_parallel_test_fixtures

MULTIOUTPUT = ["uniform_average", "raw_values", "numpy"]

# list of parallelization backends to test
BACKENDS = _get_parallel_test_fixtures("config")


class ForecastingMetricPtFixtureGenerator(BaseFixtureGenerator):
    """Fixture generator for time series forecasting metric tests, point forecasts.

    Fixtures parameterized
    ----------------------
    estimator_class: estimator inheriting from BaseObject
        ranges over estimator classes not excluded by EXCLUDE_ESTIMATORS, EXCLUDED_TESTS
    estimator_instance: instance of estimator inheriting from BaseObject
        ranges over estimator classes not excluded by EXCLUDE_ESTIMATORS, EXCLUDED_TESTS
        instances are generated by create_test_instance class method
    scenario: instance of TestScenario
        ranges over all scenarios returned by retrieve_scenarios
    """

    # note: this should be separate from TestAllForecastingMetricsPt
    #   additional fixtures, parameters, etc should be added here
    #   ForecastingMetricsPt should contain the tests only

    estimator_type_filter = "metric_forecasting_point"

    fixture_sequence = [
        "estimator_class",
        "estimator_instance",
        "fitted_estimator",
        "scenario",
    ]


class TestAllForecastingPtMetrics(ForecastingMetricPtFixtureGenerator, QuickTester):
    """Module level tests for all sktime forecast metrics, point forecasts."""

    @pytest.mark.parametrize("n_columns", [1, 2])
    @pytest.mark.parametrize("multioutput", MULTIOUTPUT)
    def test_metric_output_direct(estimator_class, multioutput, n_columns):
        """Test output is of correct type, dependent on multioutput.

        Also tests that four ways to call the metric yield equivalent results:
            1. using the __call__ dunder
            2. calling the evaluate method
        """
        metric = estimator_class

        # create numpy weights based on n_columns
        if multioutput == "numpy":
            if n_columns == 1:
                return None
            multioutput = np.random.rand(n_columns)

        # create test data
        y_pred = _make_series(n_columns=n_columns, n_timepoints=20, random_state=21)
        y_true = _make_series(n_columns=n_columns, n_timepoints=20, random_state=42)

        # coerce to DataFrame since _make_series does not return consistent output type
        y_pred = pd.DataFrame(y_pred)
        y_true = pd.DataFrame(y_true)

        res = dict()

        res[1] = metric(multioutput=multioutput)(
            y_true=y_true,
            y_pred=y_pred,
            y_pred_benchmark=y_pred,
            y_train=y_true,
        )

        res[2] = metric(multioutput=multioutput).evaluate(
            y_true=y_true,
            y_pred=y_pred,
            y_pred_benchmark=y_pred,
            y_train=y_true,
        )

        if isinstance(multioutput, np.ndarray) or multioutput == "uniform_average":
            assert all(isinstance(x, float) for x in res.values())
        elif multioutput == "raw_values":
            assert all(isinstance(x, np.ndarray) for x in res.values())
            assert all(x.ndim == 1 for x in res.values())
            assert all(len(x) == len(y_true.columns) for x in res.values())

        # assert results from all options are equal
        assert np.allclose(res[1], res[2])

    @pytest.mark.parametrize("n_columns", [1, 2])
    @pytest.mark.parametrize("multioutput", MULTIOUTPUT)
    def test_metric_output_by_instance(estimator_class, multioutput, n_columns):
        """Test output of evaluate_by_index for type, dependent on multioutput."""
        # create numpy weights based on n_columns
        metric = estimator_class

        if multioutput == "numpy":
            if n_columns == 1:
                return None
            multioutput = np.random.rand(n_columns)

        # create test data
        y_pred = _make_series(n_columns=n_columns, n_timepoints=20, random_state=21)
        y_true = _make_series(n_columns=n_columns, n_timepoints=20, random_state=42)

        # coerce to DataFrame since _make_series does not return consistent output type
        y_pred = pd.DataFrame(y_pred)
        y_true = pd.DataFrame(y_true)

        res = metric(multioutput=multioutput).evaluate_by_index(
            y_true=y_true,
            y_pred=y_pred,
            y_pred_benchmark=y_pred,
            y_train=y_true,
        )

        if isinstance(multioutput, str) and multioutput == "raw_values":
            assert isinstance(res, pd.DataFrame)
            assert (res.columns == y_true.columns).all()
        else:
            assert isinstance(res, pd.Series)

        assert (res.index == y_true.index).all()

    def test_uniform_average_time(estimator_class):
        """Tests that uniform_average_time indeed ignores index."""
        metric = estimator_class

        y_true = _make_panel()
        y_pred = _make_panel()

        metric_obj = metric(multilevel="uniform_average_time")

        y_true_noix = y_true.reset_index(drop=True)
        y_pred_noix = y_pred.reset_index(drop=True)

        res = metric_obj.evaluate(
            y_true=y_true,
            y_pred=y_pred,
            y_pred_benchmark=y_pred,
            y_train=y_true,
        )

        res_noix = metric_obj.evaluate(
            y_true=y_true_noix,
            y_pred=y_pred_noix,
            y_pred_benchmark=y_pred_noix,
            y_train=y_true_noix,
        )

        assert np.allclose(res, res_noix)


    def test_metric_weights(estimator_class):
        """Test that weights are correctly applied to the metric."""
        metric = estimator_class

        y_true = np.array([3, -0.5, 2, 7, 2])
        y_pred = np.array([2.5, 0.5, 2, 8, 2.25])
        wts = np.array([0.1, 0.2, 0.1, 0.3, 2.4])

        y_kwargs = {
            "y_true": y_true,
            "y_pred": y_pred,
            "y_pred_benchmark": y_true,
            "y_train": y_true,
        }

        metric_obj = metric()
        if metric_obj(**y_kwargs) == metric_obj(sample_weight=wts, **y_kwargs):
            raise ValueError(f"Metric {metric} does not handle sample_weight correctly")

        # wt_metr = metric(sample_weight=wts)
        # res_wt = wt_metr(y_true, y_pred)
        # assert np.allclose(res_wt, metric_obj(y_true, y_pred, sample_weight=wts))
