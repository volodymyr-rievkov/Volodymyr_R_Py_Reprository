class Student:
    __students_list = []
    __HIGH_SCHOLARSHIP = 1200.0
    __MEDIUM_SCHOLARSHIP = 1000.0

    def log_creation(func):
        def wrapper(self, *args):
            print(f"Creating a new Student with arguments: {args}")
            return func(self, *args)
        return wrapper

    @staticmethod
    def __validate_grade(grade):
        return (0 < grade <= 5)

    @staticmethod
    def __validate_course(course):
        return 0 < course <= 5

    @log_creation
    def __init__(self, name=None, surname=None, faculty=None, course=1, min_grade=1):
        self._name = name if name else ""
        self._surname = surname if surname else ""
        self.__faculty = faculty if faculty else ""
        self.__course = course if Student.__validate_course(course) else None
        self.__min_grade = min_grade if Student.__validate_grade(min_grade) else None
        if self.__min_grade is None:
            print(f"Error: Can't add student {self._name} {self._surname}, minimum exam's grade is out of range (1-5).")
        if self.__course is None:
            print(f"Error: Can't add student {self._name} {self._surname}, course is out of range (1-5).")
        else:
            Student.__students_list.append(self)
            print(f"Student {self._name} {self._surname} was added.")
        self.__scholarship = 0.0

    @property
    def name(self):
        return self._name
    
    @property
    def surname(self):
        return self._surname
    
    @property
    def faculty(self):
        return self.__faculty

    @property
    def course(self):
        return self.__course  

    @property 
    def min_grade(self):
        return self.__min_grade

    @name.setter
    def name(self, name):
        self._name = name

    @surname.setter
    def surname(self, surname):
        self._surname = surname

    @faculty.setter
    def faculty(self, faculty):
        self.__faculty = faculty

    @course.setter
    def course(self, course):
        if(Student.__validate_course(course)):
            self.__course = course
        else:
            print("Error: Course is out of range(1-5).")

    @min_grade.setter
    def min_grade(self, min_grade):
        if Student.__validate_grade(min_grade):
            self.__min_grade = min_grade
        else:
            print("Error: Minimum exam's grade is out of range(1-5).")
    
    def __str__(self):
        return f"Student {self._name} {self._surname} studies on {self.__course} course of {self.__faculty} faculty with minimum exam's grade {self.__min_grade} and scholarship of {self.__scholarship} grn."

    @classmethod    
    def show_all_students(cls):
        print("\n-------List of students-------")
        if(len(cls.__students_list) == 0):
            print("Error: Students list is empty.")
            return 
        for student in cls.__students_list:
            print(str(student))

    def to_next_course(self):
        if (self.__min_grade >= 3):
            self.__course += 1  
            print(f"Student {self._name} {self._surname} was transferred to next course.")
        else:
            print(f"Student {self._name} {self._surname} was not transferred to next course due to grade < 3.")

    @classmethod
    def to_next_course_all(cls):
        print("\n-------Transfering to next course-------")
        for student in cls.__students_list:
            student.to_next_course()

    def transfer_scholarship(self):
        scholarship = 0.0
        if(self.__min_grade == 5):
            scholarship =  Student.__HIGH_SCHOLARSHIP
        elif(self.__min_grade == 4):
            scholarship = Student.__MEDIUM_SCHOLARSHIP
        self.__scholarship += scholarship
        print(f"Student {self._name} {self._surname} has got scholarship of {scholarship} grn.")

    @classmethod 
    def transfer_scholarship_all(cls):
        print("\n-------Scholarship transferring-------")
        for student in cls.__students_list:
            student.transfer_scholarship()

    @classmethod
    def students_amount(cls):
        return len(cls.__students_list)

    @classmethod
    def find_student(cls, name, surname):
        for student in cls.__students_list:
            if(student.name == name and student.surname == surname):
                return student
        print(f"Error: Student {name} {surname} was not found.")
        return None

class ContractStudent(Student):

    def __init__(self, name=None, surname=None, faculty=None, course=1, min_grade=1):
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

class WorkingStudent(ContractStudent, Employee):

    def __init__(self, name=None, surname=None, faculty=None, course=1, min_grade=1, company=None, salary=0.0):
        ContractStudent.__init__(self, name, surname, faculty, course, min_grade)
        Employee.__init__(self, company, salary)

    def __str__(self):
        return f"Working {Student.__str__(self)} Also, an {Employee.__str__(self)}"


Student("Tom", "Cruise", "Economy", 1, 5)
Student("Cameron", "Diaz", "Medicine", 2, 4)
Student("Elon", "Musk", "Engineering", 3, 2)
ContractStudent("Andrew", "Lincoln", "Law", 4, 4)
ContractStudent("Norman", "Reedus", "Pharmacy", 4, 2)
WorkingStudent("Ryan", "Gosling", "Mechanical Engineering", 2, 3, "Uber", 20000.0)
Student.show_all_students()
ContractStudent.find_student("Andrew", "Lincoln").pay_contract()
Student.to_next_course_all()
Student.transfer_scholarship_all()
Student.show_all_students()
