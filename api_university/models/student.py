from sqlalchemy import func, asc
from typing import NoReturn

from api_university.handlers import make_error
from api_university.db.db_sqlalchemy import db
from api_university.responses.response_strings import gettext_
from .relationships import students_courses


class StudentModel(db.Model):
    __tablename__ = "students"

    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"))

    def __repr__(self):
        return f"StudentModel {self.student_id}"

    @classmethod
    def get_all_students(cls) -> "StudentModel":
        return cls.query.order_by(asc(cls.student_id)).all()
    
    @classmethod
    def get_number_of_students(cls) -> "StudentModel":
        return cls.query.count().first()
    
    @classmethod
    def get_max_student_id(cls) -> "StudentModel":
        query, = cls.query.with_entities(func.max(cls.student_id)).first()
        if not query:
            query = 0
        return query

    @classmethod
    def find_by_id(cls, student_id: int) -> "StudentModel":
        return cls.query.filter_by(student_id=student_id).first()
   
    @classmethod
    def find_by_id_or_404(cls, student_id: int) -> "StudentModel":
        message = gettext_("student_not_found").format(student_id)
        status = 404
        return cls.query.get_or_404(student_id, make_error(status, message))

    @classmethod
    def not_find_by_id_or_400(cls, student_id: int) -> None:
        message = gettext_("student_exists").format(student_id)
        status = 400
        return cls.query.not_exists_or_400(student_id, make_error(status, message))

    @classmethod
    def get_students_by_ids_or_404(cls, student_ids: list) -> list["StudentModel"] or None:
        if student_ids is None:
            selected_students = None
        else:
            selected_students = [cls.find_by_id_or_404(student) for student in student_ids]
        return selected_students

    def save_to_db(self) -> NoReturn:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> NoReturn:
        db.session.delete(self)
        db.session.commit()

