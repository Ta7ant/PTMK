from django.core.management.base import BaseCommand
from employee_app.employee_manager import EmployeeManager


class Command(BaseCommand):
    help = 'Employee Management Application for PTMK test task'

    def add_arguments(self, parser):
        parser.add_argument('mode', type=int, help='Mode of operation (1-6)')
        parser.add_argument('args', nargs='*', help='Additional arguments')

    def handle(self, *args, **options):
        mode = options['mode']
        manager = EmployeeManager()

        try:
            if mode == 1:
                # 1
                manager.create_table()

            elif mode == 2:
                # 2
                if len(args) != 3:
                    self.stderr.write("Error")
                    self.stdout.write("Usage: python manage.py myapp 2 \"Full Name\" YYYY-MM-DD Gender")
                    self.stdout.write("Example: python manage.py myapp 2 \"Ivanov Petr Sergeevich\" 2009-07-12 Male")
                    return

                full_name, birth_date, gender = args
                manager.create_employee(full_name, birth_date, gender)

            elif mode == 3:
                # 3
                manager.display_all_employees()

            elif mode == 4:
                # 4
                manager.generate_mass_data()

            elif mode == 5:
                # 5
                manager.query_male_f_lastname()

            elif mode == 6:
                # 6
                manager.optimize_database()

            else:
                self.stderr.write("Error")
                self.stdout.write("Available modes: 1, 2, 3, 4, 5, 6")

        except Exception as e:
            self.stderr.write(f"❌ Error: {e}")