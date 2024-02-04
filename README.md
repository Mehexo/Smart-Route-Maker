## Usage

> Note: Download GDAL and Fiona for your Python version [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/) first.

Install the SRM requirements through the requirements file.

```
$ pip install -r requirements.txt
```

Run the flask app.

```
$ flask --app srm run
```


if flask not found
```
python -m flask --app srm run
```
# Usage

optional:create a virtual enviroment before running the codeinstalatie

>Note: Download GDAL and Fiona for your Python version [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/) first.
Install the SRM requirements through the requirements file.
```
$ pip install -r requirements.txt
```
eventuele variabelen die je kan aanpassen zijn:in 'Routes.py' wordt de genereer route functie aangeroepen
In'SmartRouteMakerFacade.py' onder de definitie 'plan_k_circuit' kan de omtrek van de cirkel worden ingesteld als parameter 'max_length'in 'SmartRouteMakerFacade.py' onder de definitie'plan_k_circuit' kan het aantal punten op de cirkel worden aangepast door de 'i_points' variable te veranderen naar het aantal puntenin 'SmartRouteMakerFacade.py' onder de definitie 'plan_k_circuit' kan de 'variance' worden aangepast voor een groter of kleiner cirkelin 'Graph.py' onder de definitie 'full_geometry_point_graph'kan de maximale straal voor data ophalen van de api worden aangepastRun the flask app.command moet uitgevoerd worden in een command promt waarvan de huidige locatie de srm-master folder is
```

$ flask --app Smart-route-Maker run
```
if flask not found
```
python -m flask --app Smart-Route-Maker run
```
