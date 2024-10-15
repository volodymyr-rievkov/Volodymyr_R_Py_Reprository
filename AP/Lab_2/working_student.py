from contract_student import ContractStudent
from employee import Employee

class WorkingStudent(ContractStudent, Employee):

    def __init__(self, name="", surname="", faculty="", course=1, min_grade=1, company="", salary=0.0):
        ContractStudent.__init__(self, name, surname, faculty, course, min_grade)
        Employee.__init__(self, company, salary)

    def __str__(self):
        return f"Working {ContractStudent.__str__(self)} Also, an {Employee.__str__(self)}"
    
