# Usage

optional: create a virtual enviroment before installing libraries

>Note: Download GDAL and Fiona for your Python version [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/) first.
Install the SRM requirements through the requirements file.
```
$ pip install Fiona-1.8.21-cp310-cp310-win_amd64.whl
$ pip install GDAL-3.4.3-cp310-cp310-win_amd64.whl
```

Install the SRM requirements through the requirements file.
```
$ pip install -r requirements.txt
```
Om de applicatie te runne moet het command promt worden geopend op de locatie van de master hier moet de volgende command worden uitgvoerd
```
$ flask --app Smart-route-Maker run
```
if flask not found
```
$ python -m flask --app Smart-Route-Maker run
```

onderdelen:
routes.py
-hier wordt de call aangeroepen tot het uitvoeren van de code
smartroutemakerfacade.py
-hier staat de code en de verwijzingen naar de objecten.
results.html
-hier worden de teruggegeven waardes gevisualiseerd op de webpagina

hiernaast is er een test opgeving in de vorm van circuit gen k.ipynb hierinstaan nogeen aantal niet geimplementeerde functies en testing code.
