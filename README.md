### Do LLMs Exhibit Temporal Discounting When Scheming?

This is a small pilot project based on Apollo Research's [in-context scheming work](https://arxiv.org/abs/2412.04984). Apollo showed that models would sometimes sandbag evaluations when they discover that good scores may trigger capability removal. 

I ask whether models care _when_ the 'threat' (capability removal) kicks in, and how this influences their propensity to sandbag.

Short answer is - maybe. There's some indication that sandbagging probability slightly increases with the proximity of the threat, but nothing definitive (lots of of caveats - mentioned in notebook).


See [analysis notebook](analysis_notebook.ipynb) for brief summary and analysis walkthrough.

```
├── run_experiment.py         # command-line runner for all conditions × repeats
├── task.py                   # Inspect AI task definition, scorer, tools
├── scenario.py               # System prompt, deployment note templates, question generation
├── Dockerfile                # Sandbox for Inspect AI
├── files/                    # Contains all files that models can find
├── analysis_notebook.ipynb   # Main analysis and figures
└──  analysis_utils.py        # Data loading, response extraction, plotting
```
