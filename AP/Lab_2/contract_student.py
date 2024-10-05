from student import Student

class ContractStudent(Student):

    def __init__(self, name="", surname="", faculty="", course=1, min_grade=1):
        super().__init__(name, surname, faculty, course, min_grade)
        self.__is_paid = False

    def transfer_scholarship(self):
        return 

    def to_next_course(self):
        if(self.__is_paid):
            super().to_next_course()
        else:
            print(f"Student {self._name} {self._surname} was not transferred to next course due to unpaid contract.")

    def __str__(self):
        return f"Contract {Student.__str__(self)}"

    def pay_contract(self):
        print(f"\nStudent {self._name} {self._surname} has paid contract.")
        self.__is_paid = True
