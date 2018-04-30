class Employee:
    'parent of all employee classes'
    empCount = 0
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        Employee.empCount += 1

    def display_count(self):
        print("Total Employee %d" % Employee.empCount)

    def display_employee(self):
        print("Name: ", self.name, ", Salary: ", self.salary)

    def __str__(self):
        return "Name: %s, Salary: %s" % (self.name, self.salary)

class Department():
    def __init__(self, name):
        self.__employees = []
        self.name = name

    def __str__(self):
        return "Department Name: %s" % self.name

    def display_employees(self):
        for emp in self.__employees:
            print(str(emp))

    def build_department(self, employee):
        self.__employees.append(employee)


emp1 = Employee("Zara", 2000)
emp2 = Employee("Jim", 5000)

dep = Department("game dev")
print(str(dep))

dep.build_department(emp1)
dep.build_department(emp2)
dep.display_employees()

