import uvicorn
from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel
from typing import Union
import joblib

description="""Welcome to the Getaround API. It will be useful to estimate the daily rental price of your car. \n
The API has 3 groups of endpoints:

### Introduction Endpoints \n
- **/**: Return a simple welcoming message

### Exploration Endpoint\n
- **/Search_by_brand** : Allows you to request the data for a desired brand car \n
- **/Search_by_max_mileage** : Allows you to request the data for a desired max mileage \n
- **/Get_unique_values** : Allows you to get all the unique values from the desired column (listed in /predict endpoint)

### Machine Learning Prediction Endpoint
- **/predict**: Gives you an estimated rental price per day for a car.\n

Don't hesitate to try it out 🕹️ \n
👇 If you want further information on this project, check my Github account below """

tags_metadata = [
    {
        "name": "Introduction Endpoint",
        "description": "Simple endpoints to try out!",
    },
    {
        "name": "Machine Learning Prediction Endpoint",
        "description": "Prediction price."
    },
    {
        "name": "Exploration Endpoint",
        "description": "Allows you to query the data."
    }
]

app = FastAPI(
    title="GetAroundAPI🚗",
    description=description,
    version="0.1",
    contact={
        "name": "Github account",
        "url": "https://github.com/JeremyLPS",
    },
    openapi_tags=tags_metadata
)

@app.get("/", tags=["Introduction Endpoint"])
async def root():
    message = """👋🏻 Welcome to the Getaround API. 🗒️ The documentation of this API is available at the /docs section"""
    return message


# Defining required input for prediction
class CarFeatures(BaseModel):
    model_key: str = 'Fiat'
    mileage: Union[int, float] = 150000
    engine_power: Union[int, float] = 90
    fuel: str = "diesel"
    paint_color: str = "white"
    car_type: str = "sedan"
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

@app.get("/Search_by_brand", tags=["Exploration Endpoint"])
async def search_by_brand(brand: str="Ford"):
    """
    Here you can search data by car brand !

    Please select a brand within these ones :

    'Citroën', 'Peugeot', 'PGO', 'Renault', 'Audi', 'BMW', 'Ford',
    'Mercedes', 'Opel', 'Porsche', 'Volkswagen', 'KIA Motors',
    'Alfa Romeo', 'Ferrari', 'Fiat', 'Lamborghini', 'Maserati',
    'Lexus', 'Honda', 'Mazda', 'Mini', 'Mitsubishi', 'Nissan', 'SEAT',
    'Subaru', 'Suzuki', 'Toyota', 'Yamaha'
   
    """
    brand_list = ['Citroën', 'Peugeot', 'PGO', 'Renault', 'Audi', 'BMW', 'Ford',
       'Mercedes', 'Opel', 'Porsche', 'Volkswagen', 'KIA Motors',
       'Alfa Romeo', 'Ferrari', 'Fiat', 'Lamborghini', 'Maserati',
       'Lexus', 'Honda', 'Mazda', 'Mini', 'Mitsubishi', 'Nissan', 'SEAT',
       'Subaru', 'Suzuki', 'Toyota', 'Yamaha']
    try:
        if brand not in brand_list:
            raise ValueError("The value you entered is not part of the brand_list. Please check and try again.")
        df = pd.read_csv("https://jedha-deployment.s3.amazonaws.com/get_around_pricing_project.csv")
        model = df[df["model_key"]==brand]

        return model.to_dict()
    
    except Exception as e:
        return {"error": str(e)}

@app.get("/Search_by_max_mileage", tags=["Exploration Endpoint"])
async def search_max_mileage(max_mileage: int=50000):
    """
    Here you can search data by max mileage!

    Enter the maximum mileage desired (must be a positive number)"""

    try:
        if max_mileage < 0 :
            raise ValueError("You must entry a positive number. Please check and try again.")
        df = pd.read_csv("https://jedha-deployment.s3.amazonaws.com/get_around_pricing_project.csv")
        maximum_mileage = df[df["mileage"]<=max_mileage]

        return maximum_mileage.to_dict()
    
    except Exception as e:
        return {"error": str(e)}

@app.get("/Get_unique_values",tags=["Exploration Endpoint"])
async def get_unique_values(col: str):
    """ Here you can see all the available values for a desired column !\n
    **The list of columns is written in */predict* endpoint**

    🚨Trying to get unique values from "mileage" and "rental_price_per_day" will return an error🚨"""
    try:
        df = pd.read_csv("https://jedha-deployment.s3.amazonaws.com/get_around_pricing_project.csv")
        list_of_unique_values = df[col].unique()
        return list(list_of_unique_values)
    
    except Exception as e:
        return {"error": str(e)}

@app.post("/predict", tags=["Machine Learning Prediction Endpoint"])
async def predict(CarFeatures: CarFeatures):
    """
    In order to get the estimated rental price per day for your car you must enter the required informations...\n
    Here are the inputs you must fill: \n

    - **model_key**: the brand of the car (Ford, Citroën, BMW, etc.)\n
    - **mileage**: the mileage of the car (must be positive)\n
    - **engine_power**: the engine power of the car (must be positive)\n
    - **fuel**: the fuel type of the car (within diesel, petrol, hybrid or electric)\n
    - **paint_color**: the color of the car(within black, grey, white, red, silver, blue, orange, beige, brown, green)\n
    - **car_type**: the type of car (within sedan, hatchback, suv, van, estate, convertible, coupe, subcompact)\n
    - **private_parking_available**: Does the car have a private parking ? (True or False)\n
    - **has_gps**: Does the car have a GPS or not (True or False)\n
    - **has_air_conditioning**: Does the car have air conditioning ? (True or False)\n
    - **automatic_car**: Does the car is automatic ? (True or False)\n
    - **has_getaround_connect**: Does the car have Getaround Connect or not (True or False)\n
    - **has_speed_regulator**: Does the car have a speed regulator or not (True or False)\n
    - **winter_tires**: Does the car have winter tires or not (True or False)\n
    
    
    Please be careful with the input data to make the prediction work ☑️"""

    df = pd.DataFrame(dict(CarFeatures), index=[0])
    # Load the model & preprocessor
    try:
        model = joblib.load('linear.pkl')
        preprocessor = joblib.load('preprocessor.pkl')
    except Exception as e:
        return {"error": str(e)}  # Return error message if loading fails

    # Assuming the preprocessor is a StandardScaler or a similar transformer
    try:
        X = preprocessor.transform(df)
    except Exception as e:
        return {"error": str(e)}  # Return error message if transformation fails

    try:
        prediction = model.predict(X)
        return {f"The estimated rental price per day for this vehicle is {round(prediction[0],2)} $"}
    except Exception as e:
        return {"error": str(e)}  # Return error message if prediction fails



if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000) # Here you define your web server to run the `app` variable (which contains FastAPI instance), with a specific host IP (0.0.0.0) and port (5000)