import os
from dataclasses import dataclass
from psycopg2 import Error
from psycopg2.extensions import connection as psycopg2_conn
from dotenv import load_dotenv

from api_university.db.tools.utils import (
    PsqlDatabaseConnection,
    try_except_decorator
)
from api_university.db.tools.sql_operations import (
    DatabaseSQLOperation,
    RoleSQLOperation,
    UserSQLOperation,
    PrivilegeSQLOperation
)

load_dotenv()


@dataclass()
class DatabaseOperation:
    connection: psycopg2_conn
    db_name: str = os.getenv("PG_DB")
    user_name: str = os.getenv("PG_USER")
    user_password: str = os.getenv("PG_USER_PASSWORD")
    role_name: str = os.getenv("PG_ROLE")

    @try_except_decorator(Error)
    def create_db(self):
        cursor = self.connection.cursor()
        cursor.execute(DatabaseSQLOperation.check_db_existence(self.db_name))
        exists, = cursor.fetchone()
        if exists:
            print(f"\tDatabase '{self.db_name}' already exists.")
        else:
            cursor.execute(DatabaseSQLOperation.create_db(self.db_name))
            print(f"\tDatabase '{self.db_name}' has been created.")

    @try_except_decorator(Error)
    def drop_db(self):
        cursor = self.connection.cursor()
        cursor.execute(DatabaseSQLOperation.check_db_existence(self.db_name))
        exists, = cursor.fetchone()
        if exists:
            cursor.execute(DatabaseSQLOperation.drop_db(self.db_name))
            print(f"\tDatabase '{self.db_name}' has been successfully dropped.")
        else:
            print(f"\tCan not drop the db '{self.db_name}', database does not exists.")

    @try_except_decorator(Error)
    def create_role(self):
        cursor = self.connection.cursor()
        cursor.execute(RoleSQLOperation.check_role_existence(self.role_name))
        exists, = cursor.fetchone()
        if exists:
            print(f"\tRole '{self.role_name}' already exists.")
        else:
            cursor.execute(RoleSQLOperation.create_new_role(self.role_name))
            print(f"\tRole '{self.role_name}' has been created")

    @try_except_decorator(Error)
    def drop_role(self):
        cursor = self.connection.cursor()
        cursor.execute(RoleSQLOperation.check_role_existence(self.role_name))
        exists, = cursor.fetchone()
        if exists:
            cursor.execute(RoleSQLOperation.drop_role(self.role_name))
            print(f"\tRole '{self.role_name}' has been successfully dropped.")
        else:
            print(f"\tCan not drop role '{self.role_name}', role does not exists.")

    @try_except_decorator(Error)
    def join_user_to_role(self, user_name: str):
        cursor = self.connection.cursor()
        cursor.execute(UserSQLOperation.check_membership(user_name))
        exists, = cursor.fetchone()
        if exists:
            print(f"\tUser '{user_name}' already joined.")
        else:
            cursor.execute(RoleSQLOperation.join_user_to_role(self.role_name, user_name))
            print(f"\tUser '{user_name}' has been successfully joined to role.")

    @try_except_decorator(Error)
    def remove_user_from_role(self, user_name: str):
        cursor = self.connection.cursor()
        cursor.execute(UserSQLOperation.check_membership(user_name))
        exists, = cursor.fetchone()
        if exists:
            cursor.execute(RoleSQLOperation.remove_user_from_role(self.role_name, user_name))
            print(f"\tUser '{user_name}' has been successfully removed from role.")
        else:
            print(f"\tUser '{user_name}' has no membership in any role.")

    @try_except_decorator(Error)
    def create_user(self):
        cursor = self.connection.cursor()
        cursor.execute(UserSQLOperation.check_user_existence(self.user_name))
        exists, = cursor.fetchone()
        if exists:
            print(f"\tUser '{self.user_name}' already exists.")
        else:
            cursor.execute(UserSQLOperation.create_new_user(self.user_name, self.user_password))
            print(f"\tUser '{self.user_name}' has been created")

    @try_except_decorator(Error)
    def drop_user(self):
        cursor = self.connection.cursor()
        cursor.execute(UserSQLOperation.check_user_existence(self.user_name))
        exists, = cursor.fetchone()
        if exists:
            cursor.execute(UserSQLOperation.drop_user(self.user_name))
            print(f"\tUser '{self.user_name}' has been successfully dropped.")
        else:
            print(f"\tCan not drop user '{self.user_name}', user does not exists.")

    @try_except_decorator(Error)
    def grant_all_privileges(self, role_or_user_name: str):
        cursor = self.connection.cursor()
        cursor.execute(PrivilegeSQLOperation.grant_all_privileges(self.db_name, role_or_user_name))
        print(f"\tAll privileges have been granted to '{role_or_user_name}'")

    @try_except_decorator(Error)
    def remove_all_privileges(self, role_or_user_name: str):
        cursor = self.connection.cursor()
        cursor.execute(PrivilegeSQLOperation.remove_all_privileges(self.db_name, role_or_user_name))
        print(f"\tAll privileges have been removed from '{role_or_user_name}'")

    def create_all(self):
        if self.db_name is not None:
            self.create_db()

        if self.user_name is not None:
            self.create_user()

        if self.role_name is not None:
            self.create_role()
            self.grant_all_privileges(self.role_name)
            self.join_user_to_role(self.user_name)
        else:
            self.grant_all_privileges(self.user_name)

    def drop_all(self):
        if self.role_name is not None:
            self.remove_all_privileges(self.role_name)
            self.remove_user_from_role(self.user_name)
            self.drop_role()
        else:
            self.remove_all_privileges(self.user_name)

        self.drop_db()
        self.drop_user()


if __name__ == '__main__':
    with PsqlDatabaseConnection() as conn:

        # init database params:
        database = DatabaseOperation(connection=conn)

        # db operations:
        # database.create_all()
        database.drop_all()
