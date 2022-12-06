# opendota2

This repository contains functionalities that answer the given questions:

1.	Given a list of player_ids return a leaderboard of the players based on their win rate. The API can take two additional parameters
    - a time period such as “last_week”, “last_month”, “last_year” 
	- OR a date e.g. ‘2022-01-01’

2.	Given one player_id return a suggestion of a hero that the player should play based on the player's historical data.

### Project setup: 

Create python virtual environment and install [requirements.txt](./requirements.txt). To create virtual environment either use pip venv or conda.

```bash 
$ conda create --name=env_name
$ conda activate env_name
$ (env_name) pip install -r requirements.txt
```

To be able to use the created environment in jupyter notebook add environment to your jupyter.

```bash
$ python -m ipykernel install --user --name=env_name
```

The application structure is;

#### opendota2 
 * [app.py](./app.py)
 * [config.py](./config.py)
 * [docker-compose.yml](./docker-compose.yml)
 * [Dockerfile](./Dockerfile)
 * [.env](./.env)
 * [lightfm_notebook.ipynb](./lightfm_notebook.ipynb)
 * [utils.py](./utils.py)
 * [README.md](./README.md)
 * [requirements.txt](./requirements.txt)
 * [models](./models)


In `app.py` we implement an instance of Flask, and two endpoints. First endpoint returns leaderboard for the given players until specific time if the time is given. The second endpoint makes hero recommendations for the given player by using the either lightfm recommendation or popularity based recommender engine if the player is not seen by the model. 

We use [Dockerfile](./Dockerfile) to dockerize the application and add Redis as a service. 

We use [docker-compose.yml](./docker-compose.yml) to run the containers. In the docker-compose from the above gist, we can see that for the environment variables I refer to the .env file, and then I use config.py to map these variables to the Flask application. For the flask-caching library to work, we need to set some environment variables, which are for Redis connection and caching type. You can read more about the configuration from the documentation of the library, based on the caching type that you want to implement.

In the [.env](./.env) we set some variables like caching type, host, db, etc. Since we have these variables mounted from docker-compose inside our container, now we can get those variables using the os module. Let’s get those variables in config.py and we’ll use them later to map the values to our Flask application.

We implement lightfm module in [lightfm](./lightfm.ipynb) notebook. We store the model trained in the lightfm notebook inside the [models](./models) folder. In addition to that we store the helper functions in the [utils.py](./utils.py). 

## Deployment and Usage 
After we are done with the coding, go to the project directory and we start the service by running the commands:
```bash
$ docker-compose up -d --build 
$ flask run 
```
To check if the services are running enter the following command:
``` bash
$ docker ps
```
When we see that the application is running without any problems we can us [Postman](https://www.postman.com/) to make the request. 

To get the leaderboard based on the query parameter ```list of player ids``` and ```date``` we run command: 

**_NOTE:_** date can take parameters such as; last_week, last_mont or last_year.

```http
localhost:5000/players?player_id=316217576&player_id=341678201&player_id=350465356&date=2022-01-01
```

``` python 
[
    {
        "player_id": "316217576",
        "win_rate": 0.49
    },
    {
        "player_id": "341678201",
        "win_rate": 0.66
    },
    {
        "player_id": "350465356",
        "win_rate": 0
    }
]
```
To get the hero recommendations based on the parameter ```player id```we run command: 
```http
localhost:5000/recommend_hero?player_id=92949094
```

``` python 
[
    {
        "hero_id": "3",
        "name": "Bane"
    }
]
```