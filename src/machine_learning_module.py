import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from src.fhir_module import CholesterolDataClient, FHIRClient


def plot_cholesterol_levels():
    cholesterol = CholesterolDataClient("https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/")
    colesterol_x = cholesterol.get_patient_data()