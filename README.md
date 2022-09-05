# DBSCAN-CellX
DBSCAN-CellX is a clustering and positional classification tool espacially designed for cell cultures. Made by the AG Graw, Bioquant Heidelberg.

## Structure of this Repo
This Repo consists of two parts, mainly the DBSCAN-CellX Python package and a easy to use GUI.
The folder "dbscan-cellx" is the Python package, which has to be downloaded and installed locally. Please refer to the installation guide. 
The folder called App holds the GUI App called DBSCAN_CellX_App.py. The GUI was made with Streamlit. 

## Installation
### Package
The Python package of DBSCAN-CellX is a standalone package which has to be installed manually. All required dependencies are installed automatically with the installation of the package itself. If the user wants to use the DBSCAN-CellX package together with the GUI, the user has to install the package in the same environment as the App. To install the package the user has to download the whole "dbscan-cellx" folder with all its contents. Next the user has to define a certain environment to install the package into. As mentioned before, if the user wants to use the GUI together with the package, the package has to be installed into the App environment. 
After downloading the user has to open the directory in a terminal of choice and call this installation function inside the directory.
```
C:\Users\USER-NAME\dbscan-cellx> python -m pip install -e .
```
After instalaltion the package should be fully installed inside the opened environment. 

### App
To install the App the easiest way is to install a new (conda) environment with the corresponding environment list. The installation of the whole APp with all its dependencies can be done by downloading the whole App folder. Inside the folder is a file called "env.txt". To install a new fresh conda environment with this file please use the follwing code:
```
conda create --name ENV-NAME --file env.txt
```
Please make sure that the path to the "env.txt" file is set or the current directory is located inside the App folder. 
After the installation is finished, the user can now activate the newly installed conda environment.

## Usage
### DBSCAN-CellX Package
To use the DBSCAN-CellX package after installation, the user has three options. The first option is to call the main function of the DBSCAN-CellX script inside a Python script.
```
from dbscan_cellx import dbscan_cellx # Imports the dbscan_cellx package


dbscan_cellx.main() # Calls the main function
```
Here the user can input the desired parameters found listed below. 

The other option is to call the main function through a terminal. As long as the DBSCAN-CellX package was installed successfully the package can be called from the terminal inside the activated environment directly. The input parameters for the terminal call are done through a seperate ArgumentParser and has a slightly different structure as explanined furhter below. To call the package use:
```
C:\Users\USER-NAME\... > python -m dbscan_cellx [- parameters]
```





