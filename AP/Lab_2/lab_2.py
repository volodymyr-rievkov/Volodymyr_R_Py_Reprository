from student import Student
from contract_student import ContractStudent
from working_student import WorkingStudent

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
