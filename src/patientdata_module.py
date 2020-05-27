from abc import ABC, abstractmethod


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


class BloodPressureData(PatientData):
    def __init__(self, systolic, diastolic, unit, effective_date):
        self._systolic = systolic
        self._diastolic = diastolic
        self._unit = unit
        self._effective_date = effective_date

    def get_data(self):
        return self._systolic, self._diastolic, self._unit, self._effective_date

    def set_data(self, data):
        self._systolic = data(0)
        self._diastolic = data(1)
        self._unit = data(2)
        self._effective_date = data(3)
