PYNNGRID
=======



##  Brief description
This repository contains a customized implementation of the **Neural Network 
Filtered Backprojection (NN-FBP)** algorithm devised by **Daniel Pelt**.

The original NN-FBP code is available at: (https://github.com/dmpelt/pynnfbp).

If you intend to use this software, please cite the original publication:
Pelt, D., & Batenburg, K. (2013). "Fast tomographic reconstruction from limited
data using artificial neural networks". Image Processing, IEEE Transactions on,
22(12), pp.5238-5251.

The NN-FBP implementation in this repository does not require the
installation of the Astra Toolbox, which works with GPUs.
The gridding backprojector is used instead.




##  Installation
Basic compilers like gcc and g++ are required.
The simplest way to install all the code is to use Anaconda with python-2.7 and
add the installation of the python package scipy, scikit-image and Cython.

Procedure:

1. Create the Anaconda environment (if not already existing): `conda create -n pynn python=2.7 anaconda`.

2. Install necessary packages (if not already installed): `conda install -n iter-rec scipy scikit-image Cython`.

3. Activate environment: 'source activate iter-rec'.

4. Download the repo (if not downloaded yet): `git clone git@github.com:arcaduf/pynngrid.git`.

5. Go inside the folder and install the C code for the backprojector: `python setup.py`.

If `setup.py` runs without giving any error all subroutines in C have been installed and
your python version meets all dependencies.



##  Test the package
Go inside the folder "scripts/" and run: `python run_test.py`.

