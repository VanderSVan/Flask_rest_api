from flask import request
from flask_restful import Resource
from marshmallow import INCLUDE

from api_university.models.course import CourseModel
from api_university.schemas.course import CourseSchema
from api_university.responses.response_strings import gettext_

short_course_schema = CourseSchema(only=('course_id', 'name',))
full_course_schema = CourseSchema()

short_course_list_schema = CourseSchema(many=True, only=('course_id', 'name',))
full_course_list_schema = CourseSchema(many=True)


class Course(Resource):
    @classmethod
    def get(cls, course_id):
        """file: api_university/Swagger/Course/get.yml"""
        course = CourseModel.find_by_id_or_404(course_id)
        if request.args.get('full', 'false').lower() == 'true':
            response = full_course_schema.dump(course), 200
        else:
            response = short_course_schema.dump(course), 200
        return response

    @classmethod
    def post(cls, course_id):
        """file: api_university/Swagger/Course/post.yml"""
        course_json = request.get_json()
        course_json['course_id'] = course_id
        new_course = full_course_schema.load(course_json, unknown=INCLUDE)
        new_course.save_to_db()
        return {'status': 200, 'message': gettext_("course_post").format(course_id)}, 200

    @classmethod
    def put(cls, course_id):
        """file: api_university/Swagger/Course/put.yml"""
        course_json = request.get_json()
        course_json['course_id'] = course_id
        updated_course = full_course_schema.load(course_json, partial=True, unknown=INCLUDE)
        updated_course.save_to_db()
        return {'status': 200, 'message': gettext_("course_put").format(course_id)}, 200

    @classmethod
    def delete(cls, course_id):
        """file: api_university/Swagger/Course/delete.yml"""
        course = CourseModel.find_by_id_or_404(course_id)
        course.delete_from_db()
        return {'status': 200, 'message': gettext_("course_delete").format(course_id)}, 200


class CourseList(Resource):
    @classmethod
    def get(cls):
        """file: api_university/Swagger/CourseList/get.yml"""
        course_list = CourseModel.get_all_courses()
        if request.args.get('full', 'false').lower() == 'true':
            response = full_course_list_schema.dump(course_list), 200
        else:
            response = short_course_list_schema.dump(course_list), 200
        return response
