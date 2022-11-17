import importlib
import os
from abc import ABC, abstractmethod

import _hydrobricks as hb
import HydroErr
import pandas as pd
from _hydrobricks import ModelHydro, SettingsModel

from hydrobricks import utils


class Model(ABC):
    """Base class for the models"""

    def __init__(self, name=None, **kwargs):
        self.name = name
        self.settings = SettingsModel()
        self.model = ModelHydro()
        self.spatial_structure = None
        self.allowed_kwargs = {'solver', 'record_all', 'surface_types', 'surface_names'}
        self.initialized = False

        # Default options
        self.solver = 'HeunExplicit'
        self.record_all = True
        self.surface_types = ['ground']
        self.surface_names = ['ground']

        self._set_options(kwargs)

        # Setting base settings
        self.settings.log_all(self.record_all)
        self.settings.set_solver(self.solver)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def setup(self, spatial_structure, output_path, start_date, end_date):
        """
        Setup and run the model.

        Parameters
        ----------
        spatial_structure : HydroUnits
            The spatial structure of the catchment.
        output_path: str
            Path to save the results.
        start_date: str
            Starting date of the computation
        end_date: str
            Ending date of the computation

        Return
        ------
        The predicted discharge time series
        """
        if self.initialized:
            raise RuntimeError('The model has already been initialized. '
                               'Please create a new instance.')

        try:
            if not os.path.isdir(output_path):
                os.mkdir(output_path)

            self.spatial_structure = spatial_structure

            # Initialize log
            hb.init_log(output_path)

            # Modelling period
            self.settings.set_timer(start_date, end_date, 1, "Day")

            # Initialize the model (with sub basin creation)
            if not self.model.init_with_basin(
                    self.settings, spatial_structure.settings):
                raise RuntimeError('Basin creation failed.')

            self.initialized = True

        except RuntimeError:
            print("A runtime exception occurred.")
        except TypeError:
            print("A type error exception occurred.")
        except Exception:
            print("An exception occurred.")

    def run(self, parameters, forcing=None):
        """
        Setup and run the model.

        Parameters
        ----------
        parameters : ParameterSet
            The parameters for the given model.
        forcing : Forcing
            The forcing data.

        Return
        ------
        The predicted discharge time series
        """
        if not self.initialized:
            raise RuntimeError('The model has not been initialized. '
                               'Please run setup() first.')

        try:
            self.model.reset()

            self._set_parameters(parameters)
            self._set_forcing(forcing)

            if not self.model.is_ok():
                raise RuntimeError('Model is not OK.')

            timer = utils.Timer()
            timer.start()

            if not self.model.run():
                raise RuntimeError('Model run failed.')

            timer.stop()

        except RuntimeError:
            print("A runtime exception occurred.")
        except TypeError:
            print("A type error exception occurred.")
        except Exception:
            print("An exception occurred.")

    def initialize_state_variables(self, parameters, forcing=None):
        """
        Run the model and save the state variables as initial values.

        Parameters
        ----------
        parameters : ParameterSet
            The parameters for the given model.
        forcing : Forcing
            The forcing data.
        """
        self.run(parameters, forcing)
        self.model.save_as_initial_state()

    def set_forcing(self, forcing):
        """
        Set the forcing data.

        Parameters
        ----------
        forcing : Forcing
            The forcing data.
        """
        self.model.clear_time_series()
        time = utils.date_as_mjd(forcing.time.to_numpy())
        ids = self.spatial_structure.get_ids().to_numpy()
        for data_name, data in zip(forcing.data_name, forcing.data_spatialized):
            if data is None:
                raise RuntimeError(f'The forcing {data_name} has not '
                                   f'been spatialized.')
            if not self.model.create_time_series(data_name, time, ids, data):
                raise RuntimeError('Failed adding time series.')

        if not self.model.attach_time_series_to_hydro_units():
            raise RuntimeError('Attaching time series failed.')

    def create_config_file(self, directory, name, file_type='both'):
        """
        Create a configuration file describing the model structure.

        Such a file can be used when using the command-line version of hydrobricks. It
        contains the options to generate the corresponding model structure.

        Parameters
        ----------
        directory : str
            The directory to write the file.
        name : str
            The name of the generated file.
        file_type : file_type
            The type of file to generate: 'json', 'yaml', or 'both'.
        """
        settings = {
            'base': self.name,
            'solver': self.solver,
            'options': self._get_specific_options(),
            'surfaces': {
                'names': self.surface_names,
                'types': self.surface_types
            },
            'logger': 'all' if self.record_all else ''
        }
        utils.dump_config_file(settings, directory, name, file_type)

    def get_outlet_discharge(self):
        """
        Get the computed outlet discharge.
        """
        return self.model.get_outlet_discharge()

    def dump_outputs(self, path):
        """
        Write the model outputs to a netcdf file.

        Parameters
        ----------
        path: str
            Path to the target file.
        """
        self.model.dump_outputs(path)

    def analyze(self, method, parameters, parameters_to_assess, forcing, observations,
                metrics, nb_runs=10000):
        """
        Perform an analysis of the model parameters.

        Parameters
        ----------
        method: str
            The name of the analysis method to use.
            Options: monte_carlo
        parameters: ParameterSet
            The parameter set to analyze.
        parameters_to_assess: list
            A list of parameters to assess. Only the parameters in this list will be
            changed. If a parameter is related to data forcing, the spatialization
            will be performed again.
        forcing: Forcing
            Forcing data object.
        observations: Observations
            Observations to compare to.
        metrics: list
            List of the metrics to assess.
            Example: ['nse', 'kge_2012']
        nb_runs: int
            Number of assessment to make.

        Returns
        -------
        A dataframe containing the parameter values and the corresponding metrics.
        """
        if method != 'monte_carlo':
            raise NotImplementedError

        random_forcing = self._needs_random_forcing(parameters, parameters_to_assess)

        forcing.apply_defined_spatialization(parameters)
        if not random_forcing:
            self.set_forcing(forcing=forcing)

        columns = [*parameters_to_assess, *metrics]
        tested_params = pd.DataFrame(columns=columns)

        for n in range(nb_runs):
            print(f'Run {n + 1}/{nb_runs}')
            assigned_values = parameters.set_random_values(parameters_to_assess)

            if random_forcing:
                forcing.apply_defined_spatialization(parameters, parameters_to_assess)
                self.run(parameters=parameters, forcing=forcing)
            else:
                self.run(parameters=parameters)

            for metric in metrics:
                assigned_values[metric] = self.eval(metric, observations)

            tested_params = pd.concat([tested_params, assigned_values])

        return tested_params

    def eval(self, metric, observations):
        """
        Evaluate the simulation using the provided metric (goodness of fit).

        Parameters
        ----------
        metric
            The abbreviation of the function as defined in HydroErr
            (https://hydroerr.readthedocs.io/en/stable/list_of_metrics.html)
            Examples: nse, kge_2012, ...
        observations
            The time series of the observations with dates matching the simulated
            series.

        Returns
        -------
        The value of the selected metric.
        """
        sim_ts = self.get_outlet_discharge()
        eval_fct = getattr(importlib.import_module('HydroErr'), metric)
        return eval_fct(sim_ts, observations)

    @abstractmethod
    def generate_parameters(self):
        raise Exception(f'Parameters cannot be generated for the base model '
                        f'(named {self.name}).')

    def _set_options(self, kwargs):
        if 'solver' in kwargs:
            self.solver = kwargs['solver']
        if 'record_all' in kwargs:
            self.record_all = kwargs['record_all']
        if 'surface_types' in kwargs:
            self.surface_types = kwargs['surface_types']
        if 'surface_names' in kwargs:
            self.surface_names = kwargs['surface_names']

    def _add_allowed_kwargs(self, kwargs):
        self.allowed_kwargs.update(kwargs)

    def _validate_kwargs(self, kwargs):
        # Validate optional keyword arguments.
        utils.validate_kwargs(kwargs, self.allowed_kwargs)

    @abstractmethod
    def _get_specific_options(self):
        return {}

    def _set_parameters(self, parameters):
        model_params = parameters.get_model_parameters()
        for _, param in model_params.iterrows():
            if not self.settings.set_parameter(param['component'], param['name'],
                                               param['value']):
                raise RuntimeError('Failed setting parameter values.')
        self.model.update_parameters(self.settings)

    def _set_forcing(self, forcing):
        if forcing is not None:
            self.set_forcing(forcing)
        elif not self.model.forcing_loaded():
            raise RuntimeError('Please provide the forcing data at least once.')

    @staticmethod
    def _needs_random_forcing(parameters, parameters_to_assess):
        for param in parameters_to_assess:
            if not parameters.has(param):
                raise RuntimeError(f'The parameter {param} was not found.')
            if parameters.is_for_forcing(param):
                return True
        return False
