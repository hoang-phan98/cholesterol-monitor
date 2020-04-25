from abc import ABC, abstractmethod
from datetime import *


class PatientData(ABC):
    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def set_data(self, data):
        pass


class CholesterolData(PatientData):
    def __init__(self, value, unit, effective_date):
        self._value = value
        self._unit = unit
        self._effective_date = effective_date

    def get_data(self):
        return self._value, self._unit, self._effective_date

    def set_data(self, data):
        self._value = data(0)
        self._unit = data(1)
        self._effective_date = data(2)


if __name__ == '__main__':
    patient_data = CholesterolData(200.48, "mg/ML", "20/3/19")
    print(patient_data.get_data())
