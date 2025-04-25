import sys
import matplotlib.pyplot as plt

def exploratory_stats(ref_filename, sim_filename, agg, figure_filename):  
    fig, ax = plt.subplots(figsize=(12,8), dpi=600)
    fig.savefig(fname=figure_filename)

#%% assign inputs
if __name__ == "__main__":
    print("Received args:", sys.argv)

    agg = sys.argv[1] 
    
    ref_filename = sys.argv[2]
    sim_filename = sys.argv[3]
    figure_filename = sys.argv[4]
    
    exploratory_stats(ref_filename, sim_filename, agg, figure_filename)
