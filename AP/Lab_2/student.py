class Student:
    __students_list = []
    __HIGH_SCHOLARSHIP = 1200.0
    __MEDIUM_SCHOLARSHIP = 1000.0
    __MIN_GRADE = 1
    __MAX_GRADE = 5
    __MIN_COURSE = 1
    __MAX_COURSE = 5
    __MIN_COURSE_FOR_TRANSFER = 3
    __MID_S_GRADE = 4
    __HIGH_S_GRADE = 5

    def log_creation(func):
        def wrapper(self, *args):
            print(f"Creating a new Student with arguments: {args}")
            return func(self, *args)
        return wrapper

    @staticmethod
    def __validate_grade(grade):
        return (Student.__MIN_GRADE < grade <= Student.__MAX_GRADE)

    @staticmethod
    def __validate_course(course):
        return Student.__MIN_COURSE < course <= Student.__MAX_COURSE

    @log_creation
    def __init__(self, name="", surname="", faculty="", course=1, min_grade=1): 
        self._name = name 
        self._surname = surname 
        self.__faculty = faculty 
        self.__course = course if Student.__validate_course(course) else None
        self.__min_grade = min_grade if Student.__validate_grade(min_grade) else None
        if self.__min_grade is None:
            print(f"Error: Can't add student {self._name} {self._surname}, minimum exam's grade is out of range ({Student.__MIN_GRADE}-{Student.__MAX_GRADE}).")
        if self.__course is None:
            print(f"Error: Can't add student {self._name} {self._surname}, course is out of range ({Student.__MIN_COURSE}-{Student.__MAX_COURSE}).")
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
            print(f"Error: Course is out of range({Student.__MIN_COURSE}-{Student.__MAX_COURSE}).")

    @min_grade.setter
    def min_grade(self, min_grade):
        if Student.__validate_grade(min_grade):
            self.__min_grade = min_grade
        else:
            print(f"Error: Minimum exam's grade is out of range({Student.__MIN_GRADE}-{Student.__MAX_GRADE}).")
    
    def __str__(self):
        return f"Student {self._name} {self._surname} studies on {self.__course} course of {self.__faculty} faculty with minimum exam's grade {self.__min_grade} and scholarship of {self.__scholarship} grn."

    @classmethod    
    def show_all_students(cls):
        print("\n-------List of students-------")
        if(len(cls.__students_list) == 0):
            print("Error: Students list is empty.")
        for student in cls.__students_list:
            print(str(student))

    def to_next_course(self):
        if (self.__min_grade >= Student.__MIN_COURSE_FOR_TRANSFER):
            self.__course += 1  
            print(f"Student {self._name} {self._surname} was transferred to next course.")
        else:
            print(f"Student {self._name} {self._surname} was not transferred to next course due to grade < {Student.__MIN_COURSE_FOR_TRANSFER}.")

    @classmethod
    def to_next_course_all(cls):
        print("\n-------Transfering to next course-------")
        for student in cls.__students_list:
            student.to_next_course()

    def transfer_scholarship(self):
        scholarship = 0.0
        if(self.__min_grade == Student.__HIGH_S_GRADE):
            scholarship =  Student.__HIGH_SCHOLARSHIP
        elif(self.__min_grade == Student.__MID_S_GRADE):
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



