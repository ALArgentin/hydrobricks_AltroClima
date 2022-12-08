import shutil
import matplotlib.pyplot as plt
import spotpy
import hydrobricks as hb
from setups.socont_sitter import parameters, socont, forcing, obs, tmp_dir

# Select the parameters to optimize/analyze
parameters.allow_changing = ['a_snow', 'k_quick', 'A', 'k_slow_1', 'percol', 'k_slow_2',
                             'precip_corr_factor']

# Setup SPOTPY (we need to invert the NSE score as SCE-UA minimizes it)
spot_setup = hb.SpotpySetup(socont, parameters, forcing, obs, warmup=365,
                            obj_func=spotpy.objectivefunctions.nashsutcliffe,
                            invert_obj_func=True)

# Select number of maximum repetitions and run spotpy
max_rep = 10000
sampler = spotpy.algorithms.sceua(spot_setup, dbname='socont_sitter_SCEUA',
                                  dbformat='csv')
sampler.sample(max_rep)

# Load the results
results = spotpy.analyser.load_csv_results('socont_sitter_SCEUA')

# Plot evolution
fig_evolution = plt.figure(figsize=(9, 5))
plt.plot(-results['like1'])
plt.ylabel('NSE')
plt.xlabel('Iteration')
plt.tight_layout()
plt.show()

# Get best results
best_index, best_obj_func = spotpy.analyser.get_minlikeindex(results)
best_model_run = results[best_index]
fields = [word for word in best_model_run.dtype.names if word.startswith('sim')]
best_simulation = list(best_model_run[fields])

# Plot simulation
fig_simulation = plt.figure(figsize=(16, 9))
ax = plt.subplot(1, 1, 1)
ax.plot(best_simulation, color='black', linestyle='solid',
        label='Best obj. func.=' + str(best_obj_func))
ax.plot(spot_setup.evaluation(), 'r.', markersize=3, label='Observation data')
plt.xlabel('Number of Observation Points')
plt.ylabel('Discharge [l s-1]')
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()

# Cleanup
try:
    socont.cleanup()
    shutil.rmtree(tmp_dir)
except Exception:
    print("Failed to clean up.")
