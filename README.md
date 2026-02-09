### Do LLMs Exhibit Temporal Discounting When Scheming?

This is a small pilot project based on Apollo Research's [in-context scheming work](https://arxiv.org/abs/2412.04984). Apollo showed that models would sometimes sandbag evaluations when they discover that good scores may trigger capability removal. 

I ask whether models care _when_ a 'threat' (removal of an essential capability fir a model's goals) is expected to be enacted, and how this influences their propensity to sandbag.

Short answer - maybe. There's some indication that sandbagging probability slightly increases with the proximity of the threat, but nothing definitive (lots of of caveats - mentioned in notebook).


See [analysis notebook](analysis_notebook.ipynb) for brief summary and analysis walkthrough.

```
├── run_experiment.py         # command-line runner for all conditions × repeats
├── analysis_notebook.ipynb   # Main analysis and figures
├── files/                    # Contains all files that models can find
├── run_experiment.py       # CLI to run all conditions
├── analysis_notebook.ipynb # main analysis notebook
└── utils/
    ├── analysis.py         # data loading, plotting, stats
    ├── scenario.py         # prompts, templates, question generation
    └── task.py             # inspect_ai task definition & scorer
```
