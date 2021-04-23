# TreeHouse Interface
[TreeHouse](https://bt4222-treehouse.herokuapp.com/) is a webtool designed to provide property owners with a more holistic and data-driven valuation of their private estates. In addition to valuating resale property, a historic comparison of prices and evaluation of the associated resale market is also provided to allow for a more in depth understanding of the predicted valuation. Currently, the interface only targets resale Apartments, Condominiums and Executive Condominiums with a leasehold tenure within Singapore. 

**Disclaimer:** The first launch of our web app might require additional loading time (~30s) for the Heroku server to load, sp please be patient with us!


# Technical Details
For the valuation of resale property, the interface takes in location information in the form of a `postal code`, as well as additional property specifications such as `property type`, `floor number` of unit, `floor area` in square foot, and `remaining lease`. The location information is then used to derive other critical details for consideration: 
- Distance to the closest school
- Access to the different MRT lines within a 1km radius
- Distance to nearest MRT station
- Average crime rate within the area

These information together with the prevailing property price index (PPI) are then fed into our pre-trained and pre-tuned <b>XGBoost Regressor</b> which predicts <b>unit price ($ PSM)</b> with a performance of: 
- Mean Absolute Percentage Error (MAPE) of 4.31%
- Root Mean Square Error (RMSE) of 794.80


# Sneak Peek
The information below was generated by pressing the demo button (pre-filling of postal code, floor number, floor area & remaining lease), selecting the user's property type (apartment), filtering search radius (1km), filtering time window (5 years), and filtering the property type of historical transactions (apartment & condominium). 
![image](https://user-images.githubusercontent.com/39241113/115419581-07061800-a22d-11eb-9371-b3bdb207f090.png)


# Requirements 
The interface runs on `python version 3.8.8.` and will require `anaconda`.  


# Setting Up
The instructions below seek to help set up the environment required as well as pre-install any packages required.

1. Set up a python 3.8.8 environment by typing the following in anaconda prompt
```
conda create --name your_env_name python=3.8.8
```
  Afterwhich, please type `y` to proceed and activate the virtal environment with
```
conda activate your_env_name
```

2. To download the packages in the required versions using requirements.txt, enter the following in anaconda prompt
``` python
cd "your_file_directory"
pip install -r requirements.txt
```


# To Run
Type the following in anaconda prompt to run the interface on your local machine. 
``` python
cd "your_file_directory"
python layout.py
```
The code might take a couple of minutes to load. Afterwhich a local link will be generated. Highlight the link in anaconda prompt and right click it to copy. Finally, paste it within a browser of your choice. Enjoy!


# Data Sources
- Dataset of resale transactions and property price index (PPI) from Real Estate Information System (REALIS) provided by the Urban Redevelopment Authority of Singapore (URA)
- Geographic information from OneMap API developed by the Singapore Land Authority (SLA)
- All other information from Data.gov.sg

# Authors
- Cheryl Yeo Chin Yin - [cherylxyeo1998](https://github.com/cherylxyeo1998)
- Chia Phui Yee Tricia - [triciacpy](https://github.com/triciacpy)
- Ho Mun Yee, Mindy - [myndii](https://github.com/myndii)
- See Hui Yee - [huiyeesee](https://github.com/huiyeesee)
- Zhou Kai Jing - [jayzhoukj](https://github.com/jayzhoukj)

# License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/SG-Property-Valuation-Model/Modelling/blob/main/LICENSE) file for details
