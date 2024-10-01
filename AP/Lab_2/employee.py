class Employee:
    def __init__(self, company=None, salary=0.0):
        self.__company = company if company is not None else ""
        self.__salary = salary

    @property
    def company(self):
        return self.__company

    @property
    def salary(self):
        return self.__salary

    @company.setter
    def company(self, company):
        self.__company = company

    @salary.setter
    def salary(self, salary):
        self.__salary = salary

    def __str__(self):
        return f"Employee at {self.__company} with salary {self.__salary} grn."
