from sqladmin import ModelView
from mysite.database.models import User, Category, Course, StudyGroup, Application, Enrollment


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.full_name, User.email, User.role, User.user_status, User.created_at]
    icon = "fa-solid fa-user"


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.category_name]
    icon = "fa-solid fa-list"


class CourseAdmin(ModelView, model=Course):
    column_list = [Course.id, Course.title, Course.category_id, Course.level, Course.price, Course.status, Course.is_active]
    icon = "fa-solid fa-graduation-cap"


class StudyGroupAdmin(ModelView, model=StudyGroup):
    column_list = [StudyGroup.id, StudyGroup.name, StudyGroup.course_id, StudyGroup.teacher_id, StudyGroup.starts_on, StudyGroup.status]
    icon = "fa-solid fa-users"


class ApplicationAdmin(ModelView, model=Application):
    column_list = [Application.id, Application.student_id, Application.course_id, Application.manager_id, Application.status, Application.created_at]
    icon = "fa-solid fa-file-signature"


class EnrollmentAdmin(ModelView, model=Enrollment):
    column_list = [Enrollment.id, Enrollment.student_id, Enrollment.group_id, Enrollment.status, Enrollment.created_at]
    icon = "fa-solid fa-user-check"
