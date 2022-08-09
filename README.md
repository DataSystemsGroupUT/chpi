# CHPI 
chpi is clustering part of implementation for paper: "To tune or not to tune? An Approach for Recommending Important Hyperparameters for Classification and Clustering Algorithms"


## Software implementation

All source code used to generate the results and figures in the paper are in
the `chpi` folder.


## Getting the code

You can download a copy of all the files in this repository by cloning this repo.

    git clone https://github.com/DataSystemsGroupUT/chpi



## Dependencies

You'll need a working Python environment to run the code.
The required dependencies are specified in the file `environment.yml`.

We use `conda` virtual environments to manage the project dependencies in
isolation.
Thus, you can install our dependencies without causing conflicts with your
setup (even with different Python versions).

Run the following command in the repository folder (where `environment.yml`
is located) to create a separate environment and install all required
dependencies in it:

    conda env create -f environment.yml



## Reproducing the results

Before running any code you must activate the conda environment:

    source activate ENVIRONMENT_NAME

or, if you're on Windows:

    activate ENVIRONMENT_NAME

This will enable the environment for your current terminal session.
Any subsequent commands will use software that is installed in the environment.




Another way of exploring the code results is to execute the Jupyter notebooks
individually.
To do this, you must first start the notebook server by going into the
repository top level and running:

    jupyter notebook



## License

All source code is made available under a *MIT* license. You can freely
use and modify the code, without warranty, so long as you provide attribution
to the authors. See `LICENSE.md` for the full license text.

The manuscript text is not open source. The authors reserve the rights to the
article content, which is currently submitted for publication.
