# -*- coding: utf-8 -*-
# copyright: sktime developers, BSD-3-Clause License (see LICENSE file)
"""Tests for BaseParamFitter API points."""

__author__ = ["fkiraly"]

from sktime.tests.test_all_estimators import BaseFixtureGenerator, QuickTester


class ParamFitterFixtureGenerator(BaseFixtureGenerator):
    """Fixture generator for classifier tests.

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

    # note: this should be separate from TestAllClassifiers
    #   additional fixtures, parameters, etc should be added here
    #   Classifiers should contain the tests only

    estimator_type_filter = "param_est"


class TestAllParamFitters(ParamFitterFixtureGenerator, QuickTester):
    """Module level tests for all sktime classifiers."""

    def test_get_fitted_params(self, estimator_instance, scenario):
        """Test get_fitted_params expected return."""
        scenario.run(estimator_instance, method_sequence=["fit"])

        gfp_ret = estimator_instance.get_fitted_params()

        # this should be a dict of fitted parameters
        assert isinstance(gfp_ret, dict)

        # there should be at least one parameter fitted
        assert len(gfp_ret) > 0
