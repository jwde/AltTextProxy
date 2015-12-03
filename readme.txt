Type in the following commands to your shell if this is the first time
you are running AltTextProxy:

virtualenv env
source env/bin/activate.csh
pip install -U pip
pip install -r requirements.txt
python proxy.py <PORT NUMBER>

If you are running AltTextProxy again:
source env/bin/activate.csh
python proxy.py <PORT NUMBER>

Notes:
If you are using bash (as opposed to tcsh) use activate instead of activate.csh
To exit the python virtual environment, type:
deactivate
