import pandas as pd

def generate_grouped_regex(types, args):
    ret = r"(?P<func_name>\w+)"
    for type_name in types:
        ret += "<(?P<{}>\w+)>".format(type_name)
    for arg in args:
         ret += "/(?P<{}>[0-9]*)".format(arg)
    return ret

def read_gbench_report(fn, args_name_map):
    """ reads google benchmark csv reports and returns a dictonary of dataframes 
    
    fn - filename
    args_map - dictonary mapping google benchmarks  /val/ notation to column names
    process_firs_col_func - function reading first column and returning columns   
    """
    df = pd.read_csv(fn).dropna(axis=1, how='all')
    
    # get all different benchmarks
    benchmarked_functions = set([name.split("/")[0] for name in df["name"].values ])
    
    dfs = {name: df[df['name'].str.contains(name)] for name in benchmarked_functions}
    # post process dfs
    for name, values in args_name_map.items():
        # find matching name in dfs
        for dfs_name in dfs.keys():
            if  name in dfs_name:
                match_name = dfs_name
        df = dfs[match_name]
        dfs[match_name]= pd.concat([df, df["name"].str.extract(
                generate_grouped_regex(types=values["types"],
                                       args=values["args"]))],
            axis=1,
            join="inner" )
    
    # concatenate dfs  
    orig_df =  dfs[list(dfs.keys())[0]]
    for key in list(dfs.keys())[1:]:
         orig_df = pd.concat([ orig_df, dfs[key]], sort=False, ignore_index=True)
       
    return orig_df

def read_multiple_benchmark_files(fns, col_name, col_vals, args_name_map):
    """ reads a sets of benchmark files and concatenates all """
    # read first df dict and append 
    df_orig = read_gbench_report(fns[0], args_name_map)
    df_orig[col_name] = col_vals[0]
        
    for i, fn in enumerate(fns[1:]):
        df = read_gbench_report(fn, args_name_map)
        df[col_name] = col_vals[i+1]
        df_orig = df_orig.append(df) 
            
    
    return df_orig

def create_plot(
    df, x, x_label, y, y_label, subplots, subplot_title, 
    subplots_values, facet=None , grid="both", logy=True,
    sharex=True, height=6, ncols=1, nrows=1, legend=None,
    sharey=False,
):
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt

    def reduce_tick(el, tick_idx):
        try:
            return el.get_text().split(",")[tick_idx]
        except:
            return 0
        
    #tick_idx = df.index.names.index(x)
    #n_subs = len(subplots_values)
    
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,figsize=(ncols*height, nrows*height), sharex=sharex, sharey=sharey)
    fig.subplots_adjust(hspace=0.3)
    
    def get_ax(axes, ncols, nrows, idx):
        if (ncols != 1 and nrows != 1):
            j = idx % ncols
            i = int(idx/nrows)
            return axes[i][j]
        return axes
    
    for i,m in enumerate(subplots_values):
        ax = get_ax(axes, ncols,nrows, i)
        ax.grid(True, which=grid)
        dfs = df[df[subplots]==m]
        if facet:
            grouped = dfs.groupby(facet)
        else:
            grouped = [(legend, dfs)]
        for key, item in grouped:
            if facet:
                group = grouped.get_group(key)
            else:
                group  = item
            #dfs = dft.sort_index(level=tick_idx)
            #dfs
            (group
                 .plot(
                   grid=True,
                   x=x,
                   y=y,
                   legend=(i==0),
                   label=str(key),
                   logy=logy,     
                   ax=ax
            ))
        ax.set_title(subplot_title + str(m))
        ax.set_ylabel(y_label)
        ax.set_xlabel(x_label)
        if (i%2):
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")

        #ax.set_xticklabels([reduce_tick(el, tick_idx) for el in ax.get_xticklabels()])
        fig.savefig("figs/" + x + "_" + subplots+ "_" + y)
    return fig