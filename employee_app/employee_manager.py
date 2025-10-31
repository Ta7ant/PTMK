import sys
import random
import time
from datetime import datetime, date
from django.core.management import execute_from_command_line
from django.db import connection
from .models import Employee
from faker import Faker


class EmployeeManager:
    def __init__(self):
        self.fake = Faker()

    def create_table(self):
        try:
            execute_from_command_line(['manage.py', 'makemigrations', 'employee_app'])
            execute_from_command_line(['manage.py', 'migrate', 'employee_app'])
            print("Table created successfully")
        except Exception as e:
            print(f"Error creating table: {e}")

    def create_employee(self, full_name, birth_date_str, gender):
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()

            if gender not in ['Male', 'Female']:
                raise ValueError("Gender must be 'Male' or 'Female'")

            employee = Employee(
                full_name=full_name,
                birth_date=birth_date,
                gender=gender
            )

            employee.save_to_db()
            age = employee.calculate_age()

            print("Employee created successfully")
            print(f"Full Name: {full_name}")
            print(f"Birth Date: {birth_date}")
            print(f"Gender: {gender}")
            print(f"Age: {age} years")

        except Exception as e:
            print(f"Error creating employee: {e}")

    def display_all_employees(self):
        try:
            employees = Employee.objects.all().order_by('full_name')

            seen = set()
            unique_employees = []

            for emp in employees:
                key = (emp.full_name, emp.birth_date)
                if key not in seen:
                    seen.add(key)
                    unique_employees.append(emp)

            if not unique_employees:
                print("No employees found in database")
                return

            print("All Employees:")
            print("Full Name | Birth Date | Gender | Age")
            print("-" * 50)

            for emp in unique_employees:
                age = emp.calculate_age()
                print(f"{emp.full_name} | {emp.birth_date} | {emp.gender} | {age}")

        except Exception as e:
            print(f"Error displaying employees: {e}")

    def bulk_save_employees(self, employees):
        Employee.objects.bulk_create(employees, batch_size=1000)

    def generate_mass_data(self):
        print("Starting mass data generation...")

        Employee.objects.all().delete()
        print("Cleared existing data")

        batch_size = 10000
        total_records = 1000000

        male_count = 0
        female_count = 0
        first_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        letter_distribution = {letter: 0 for letter in first_letters}

        print(f"Generating {total_records} random employees...")

        for i in range(0, total_records, batch_size):
            current_batch_size = min(batch_size, total_records - i)
            employees_batch = []

            for j in range(current_batch_size):
                gender = 'Male' if random.random() < 0.5 else 'Female'

                if gender == 'Male':
                    male_count += 1
                else:
                    female_count += 1

                first_letter = random.choice(first_letters)
                letter_distribution[first_letter] += 1

                if gender == 'Male':
                    first_name = self.fake.first_name_male()
                else:
                    first_name = self.fake.first_name_female()

                last_name = first_letter + self.fake.last_name()[1:]
                middle_name = self.fake.first_name()
                full_name = f"{last_name} {first_name} {middle_name}"

                start_date = date.today().replace(year=date.today().year - 65)
                end_date = date.today().replace(year=date.today().year - 18)
                birth_date = self.fake.date_between(start_date=start_date, end_date=end_date)

                employee = Employee(
                    full_name=full_name,
                    birth_date=birth_date,
                    gender=gender
                )
                employees_batch.append(employee)

            self.bulk_save_employees(employees_batch)
            progress = (i + current_batch_size) / total_records * 100
            print(f"Progress: {progress:.1f}%")

        print("Adding 100 male employees with last name starting with 'F'...")
        f_employees = []

        for i in range(100):
            first_name = self.fake.first_name_male()
            middle_name = self.fake.first_name_male()
            last_name = "F" + self.fake.last_name()[1:]
            full_name = f"{last_name} {first_name} {middle_name}"

            birth_date = self.fake.date_between(
                start_date=date.today().replace(year=date.today().year - 65),
                end_date=date.today().replace(year=date.today().year - 18)
            )

            employee = Employee(
                full_name=full_name,
                birth_date=birth_date,
                gender='Male'
            )
            f_employees.append(employee)

        self.bulk_save_employees(f_employees)

        print("Data generation completed")
        print(f"Total males: {male_count}")
        print(f"Total females: {female_count}")
        print(f"Total records: {male_count + female_count + 100}")

    def query_male_f_lastname(self):
        print("Querying male employees with last name starting with 'F'...")

        start_time = time.time()
        employees = Employee.objects.filter(
            gender='Male',
            full_name__startswith='F'
        )
        count = employees.count()
        end_time = time.time()
        execution_time = end_time - start_time

        print(f"Found: {count} employees")
        print(f"Execution time: {execution_time:.4f} seconds")

        return execution_time

    def optimize_database(self):
        print("Starting database optimization...")

        print("Before optimization:")
        time_before = self.query_male_f_lastname()

        print("Creating indexes...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_employees_gender_first_letter 
                    ON employees (gender, (SUBSTRING(full_name FROM 1 FOR 1)));
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_employees_gender 
                    ON employees (gender);
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_employees_first_letter 
                    ON employees ((SUBSTRING(full_name FROM 1 FOR 1)));
                """)

            print("Indexes created successfully")

        except Exception as e:
            print(f"Note: {e}")

        print("After optimization:")
        time_after = self.query_male_f_lastname()

        if time_before > 0:
            improvement = ((time_before - time_after) / time_before) * 100
            print("Performance results:")
            print(f"Before: {time_before:.4f} seconds")
            print(f"After: {time_after:.4f} seconds")
            print(f"Improvement: {improvement:.2f}%")

            if improvement > 0:
                print("Optimization successful")
            else:
                print("No significant improvement")