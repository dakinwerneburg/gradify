# Model mocks for fine-grained control during tests


class MockUser:
    def __init__(self, _id):
        self.id = _id


class MockCourse:
    def __init__(self, _id, owner):
        self.id = _id
        self.owner = owner


class MockCoursework:
    def __init__(self, _id: int, max_points: int):
        self.id = _id
        self.maxPoints = max_points


class MockSubmission:
    def __init__(self, student_id: int, coursework: MockCoursework, assigned_grade: float or None):
        self.student_id = student_id
        self.coursework = coursework
        self.coursework_id = coursework.id
        self.assignedGrade = assigned_grade
