# gbench2pandas

gbench2pandas is a small wrapper to read google benchmark reports to pandas DataFrames.

# Installation

gbench2pandas can be installed using

~~~~.bash
python setup.py install --user
~~~~

## Dependencies
It is recommended to have matplotlib installed, which is usually the case when using jupyter. Matplotlib itself depends on libpng and freetype.
The simplest way to install matplotlib is via your distros package manager.


# Usage

~~~.python
args_name_map = {"bench_lu_task":{"types":["type"], 
                                  "args":["matrix_size", "num_blocks"]}, 
                 "bench_lu_omp" :{"types":["type"],
                                  "args":["matrix_size"]}}

df read_gbench_report(fn="gbench_report.csv", args_name_map=args_name_map)
~~~

or for multiple report files

~~~.python

df = g2p.read_multiple_benchmark_files(fns, "threads", max_threads, args_name_map)
~~~

