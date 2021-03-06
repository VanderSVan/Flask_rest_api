from string import ascii_uppercase
from random import choices, sample, choice, randint

from api_university.models.student import StudentModel
from api_university.models.group import GroupModel
from api_university.models.course import CourseModel


def generate_available_places_in_groups(lower_limit_of_students: int,
                                        upper_limit_of_students: int,
                                        number_of_groups: int) -> dict[int:int]:
    """
    Creates dictionary with available places as random value and group_id as key.
    :param lower_limit_of_students: Lower boundary of students in a group.
    :param upper_limit_of_students: Upper boundary of students in a group.
    :param number_of_groups: How many students per group.
    :return:{group_id: int, group_id: int, ...}
    """
    return {group_id: randint(lower_limit_of_students, upper_limit_of_students)
            for group_id in range(1, number_of_groups + 1)}


def _generate_group_name(letters: str, separator: str) -> str:
    """Creates random string like type: AA-11"""
    result_list = choices(letters, k=2)
    two_digit_number = randint(10, 100)
    result_list.append(separator)
    result_list.append(str(two_digit_number))
    return "".join(result_list)


def generate_group_instances(number_of_groups: int) -> list[GroupModel]:
    """
    Model: AA-11
    Generates random group instances.
    """
    return [GroupModel(group_id=group_id,
                       name=_generate_group_name(ascii_uppercase, '-'))
            for group_id in range(1, number_of_groups + 1)]


def generate_course_instances(courses: dict) -> list[CourseModel]:
    """
    Generates course instances from dict,
    where course name as key and description as value.
    """
    return [CourseModel(course_id=course_id,
                        name=course[0].title(),
                        description=course[1].title())
            for course_id, course in enumerate(courses.items(), start=1)]


def _assign_student_to_group(available_places_in_groups: dict) -> int or None:
    """
    If there is a place in the group, assigns a student there,
    and the number of available places will decrease by 1.
    If there are no available places, returns None.
    """
    if sum(available_places_in_groups.values()) == 0:
        return None
    for group_id, available_places in available_places_in_groups.items():
        if available_places == 0:
            continue
        available_places_in_groups[group_id] -= 1
        return group_id


def generate_student_instances(number_of_students: int,
                               first_names: list,
                               last_names: list,
                               available_places_in_groups: dict,
                               courses: list[CourseModel]) -> list[StudentModel]:
    """ Generates random student instances with all relationships. """
    random_students_list = sample(range(1, number_of_students + 1), number_of_students)
    return [StudentModel(student_id=student_id,
                         first_name=choice(first_names).title(),
                         last_name=choice(last_names).title(),
                         group_id=_assign_student_to_group(available_places_in_groups),
                         courses=sample(courses, randint(1, 3)))
            for student_id in random_students_list]


if __name__ == '__main__':
    from input_data import courses_dict, first_names_list, last_names_list

    # Constants
    test_number_of_groups = 10
    test_number_of_students = 10
    limit_output = 5

    # Create list of group objects
    all_groups = generate_group_instances(number_of_groups=test_number_of_groups)

    # Create list of course objects
    all_courses = generate_course_instances(courses=courses_dict)

    # Create dict with available places as value and group_id as key
    available_places_for_groups = generate_available_places_in_groups(lower_limit_of_students=5,
                                                                      upper_limit_of_students=10,
                                                                      number_of_groups=test_number_of_groups)
    # Create list of student objects
    all_students = generate_student_instances(number_of_students=test_number_of_students,
                                              first_names=first_names_list,
                                              last_names=last_names_list,
                                              available_places_in_groups=available_places_for_groups,
                                              courses=all_courses)

    all_students.sort(key=lambda inst: inst.student_id)

    for student_num, student in enumerate(all_students[:limit_output], start=1):
        print(student_num)
        print('full name =', student.first_name, student.last_name, ';')
        print('in the group:', all_groups[student.group_id - 1].name, ';')
        print('on courses:', list(map(lambda inst: inst.name, student.courses)), '\n')
