import json
import os
from datetime import date
from typing import List, Optional

# ---------- Модели данных ----------
class Student:
    def __init__(self, sid: int, name: str):
        self.id = sid
        self.name = name
    def to_dict(self): return {"id": self.id, "name": self.name}
    @staticmethod
    def from_dict(d): return Student(d["id"], d["name"])

class Subject:
    def __init__(self, sid: int, name: str):
        self.id = sid
        self.name = name
    def to_dict(self): return {"id": self.id, "name": self.name}
    @staticmethod
    def from_dict(d): return Subject(d["id"], d["name"])

class Grade:
    def __init__(self, student_id: int, subject_id: int, grade: int, date_str: str):
        self.student_id = student_id
        self.subject_id = subject_id
        self.grade = grade
        self.date = date_str
    def to_dict(self): return {"student_id": self.student_id, "subject_id": self.subject_id, "grade": self.grade, "date": self.date}
    @staticmethod
    def from_dict(d): return Grade(d["student_id"], d["subject_id"], d["grade"], d["date"])

class Homework:
    def __init__(self, subject_id: int, description: str, due_date: str, assigned_date: str):
        self.subject_id = subject_id
        self.description = description
        self.due_date = due_date
        self.assigned_date = assigned_date
    def to_dict(self): return {"subject_id": self.subject_id, "description": self.description, "due_date": self.due_date, "assigned_date": self.assigned_date}
    @staticmethod
    def from_dict(d): return Homework(d["subject_id"], d["description"], d["due_date"], d["assigned_date"])

class Attendance:
    def __init__(self, student_id: int, date_str: str, status: str):
        self.student_id = student_id
        self.date = date_str
        self.status = status   # "Present"/"Absent"
    def to_dict(self): return {"student_id": self.student_id, "date": self.date, "status": self.status}
    @staticmethod
    def from_dict(d): return Attendance(d["student_id"], d["date"], d["status"])

# ---------- Работа с JSON ----------
class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _path(self, filename): return os.path.join(self.data_dir, filename)

    def _load(self, filename, cls):
        path = self._path(filename)
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return [cls.from_dict(item) for item in json.load(f)]

    def _save(self, filename, items):
        with open(self._path(filename), "w", encoding="utf-8") as f:
            json.dump([item.to_dict() for item in items], f, ensure_ascii=False, indent=2)

    # Методы для каждого типа
    def load_students(self): return self._load("students.json", Student)
    def save_students(self, students): self._save("students.json", students)
    def load_subjects(self): return self._load("subjects.json", Subject)
    def save_subjects(self, subjects): self._save("subjects.json", subjects)
    def load_grades(self): return self._load("grades.json", Grade)
    def save_grades(self, grades): self._save("grades.json", grades)
    def load_homeworks(self): return self._load("homeworks.json", Homework)
    def save_homeworks(self, homeworks): self._save("homeworks.json", homeworks)
    def load_attendance(self): return self._load("attendance.json", Attendance)
    def save_attendance(self, attendance): self._save("attendance.json", attendance)

# ---------- Основное приложение ----------
class ElectronicDiary:
    def __init__(self):
        self.db = DataManager()
        self.students = self.db.load_students()
        self.subjects = self.db.load_subjects()
        self.grades = self.db.load_grades()
        self.homeworks = self.db.load_homeworks()
        self.attendance = self.db.load_attendance()

    def _next_id(self, items): return max([item.id for item in items], default=0) + 1

    def _find_student(self, sid):
        for s in self.students:
            if s.id == sid: return s
        return None

    def _find_subject_by_id(self, sid):
        for s in self.subjects:
            if s.id == sid: return s
        return None

    def add_student(self):
        name = input("Имя ученика: ").strip()
        if name:
            self.students.append(Student(self._next_id(self.students), name))
            self.db.save_students(self.students)
            print(f"Ученик '{name}' добавлен.")

    def add_subject(self):
        name = input("Название предмета: ").strip()
        if name:
            self.subjects.append(Subject(self._next_id(self.subjects), name))
            self.db.save_subjects(self.subjects)
            print(f"Предмет '{name}' добавлен.")

    def add_grade(self):
        if not self.students or not self.subjects:
            print("Сначала добавьте учеников и предметы."); return
        self._show_students()
        sid = self._get_int("ID ученика: ")
        if not self._find_student(sid): print("Не найден"); return
        self._show_subjects()
        subj_id = self._get_int("ID предмета: ")
        if not self._find_subject_by_id(subj_id): print("Не найден"); return
        grade = self._get_int("Оценка (2-5): ", 2, 5)
        if grade is None: return
        self.grades.append(Grade(sid, subj_id, grade, date.today().isoformat()))
        self.db.save_grades(self.grades)
        print("Оценка выставлена.")

    def view_student_grades(self):
        if not self.students: print("Нет учеников"); return
        self._show_students()
        sid = self._get_int("ID ученика: ")
        student = self._find_student(sid)
        if not student: print("Не найден"); return
        student_grades = [g for g in self.grades if g.student_id == sid]
        if not student_grades: print("Нет оценок"); return
        by_subject = {}
        for g in student_grades:
            subj = self._find_subject_by_id(g.subject_id)
            name = subj.name if subj else f"ID {g.subject_id}"
            by_subject.setdefault(name, []).append(g.grade)
        print(f"\nОценки {student.name}:")
        for subj_name, grades in by_subject.items():
            print(f"  {subj_name}: {grades} | Средний: {sum(grades)/len(grades):.2f}")

    def add_homework(self):
        if not self.subjects: print("Нет предметов"); return
        self._show_subjects()
        subj_id = self._get_int("ID предмета: ")
        if not self._find_subject_by_id(subj_id): print("Не найден"); return
        desc = input("Описание: ").strip()
        due = input("Срок (YYYY-MM-DD, Enter если нет): ").strip()
        self.homeworks.append(Homework(subj_id, desc, due, date.today().isoformat()))
        self.db.save_homeworks(self.homeworks)
        print("ДЗ добавлено.")

    def view_homeworks(self):
        if not self.homeworks: print("Нет ДЗ"); return
        choice = input("Все задания? (y/n): ").lower()
        if choice == 'y':
            for hw in self.homeworks:
                subj = self._find_subject_by_id(hw.subject_id)
                print(f"\n{subj.name if subj else '?'}: {hw.description} (выдано {hw.assigned_date})" + (f", срок {hw.due_date}" if hw.due_date else ""))
        else:
            subj_name = input("Название предмета: ").strip()
            subj = next((s for s in self.subjects if s.name.lower() == subj_name.lower()), None)
            if not subj: print("Не найден"); return
            for hw in self.homeworks:
                if hw.subject_id == subj.id:
                    print(f"{hw.description} (выдано {hw.assigned_date})" + (f", срок {hw.due_date}" if hw.due_date else ""))

    def mark_attendance(self):
        if not self.students: print("Нет учеников"); return
        today = date.today().isoformat()
        for s in self.students:
            if any(a.student_id == s.id and a.date == today for a in self.attendance):
                print(f"{s.name} уже отмечен сегодня.")
                continue
            status = input(f"{s.name} присутствует? (y/n): ").lower()
            self.attendance.append(Attendance(s.id, today, "Present" if status == 'y' else "Absent"))
        self.db.save_attendance(self.attendance)
        print("Посещаемость сохранена.")

    def view_attendance(self):
        if not self.students: print("Нет учеников"); return
        self._show_students()
        sid = self._get_int("ID ученика: ")
        student = self._find_student(sid)
        if not student: print("Не найден"); return
        records = [a for a in self.attendance if a.student_id == sid]
        if not records: print("Нет записей"); return
        print(f"\nПосещаемость {student.name}:")
        for r in records: print(f"  {r.date}: {'Присутствовал' if r.status == 'Present' else 'Отсутствовал'}")
        present = sum(1 for r in records if r.status == "Present")
        print(f"Итого: присутствовал {present} из {len(records)} ({present/len(records)*100:.1f}%)")

    def _show_students(self):
        print("Ученики:")
        for s in self.students: print(f"  {s.id}: {s.name}")

    def _show_subjects(self):
        print("Предметы:")
        for s in self.subjects: print(f"  {s.id}: {s.name}")

    def _get_int(self, prompt, low=None, high=None):
        try:
            val = int(input(prompt))
            if low is not None and val < low: raise ValueError
            if high is not None and val > high: raise ValueError
            return val
        except ValueError:
            print(f"Ошибка: требуется целое число" + (f" от {low} до {high}" if low is not None else ""))
            return None

    def run(self):
        while True:
            print("\n" + "="*40 + "\n1. Ученик\n2. Предмет\n3. Оценка\n4. Показать оценки\n5. ДЗ\n6. Показать ДЗ\n7. Отметить посещаемость\n8. Посещаемость ученика\n0. Выход")
            cmd = input("Выберите: ")
            if cmd == "1": self.add_student()
            elif cmd == "2": self.add_subject()
            elif cmd == "3": self.add_grade()
            elif cmd == "4": self.view_student_grades()
            elif cmd == "5": self.add_homework()
            elif cmd == "6": self.view_homeworks()
            elif cmd == "7": self.mark_attendance()
            elif cmd == "8": self.view_attendance()
            elif cmd == "0": break
            else: print("Неверно")
        print("Данные сохранены. До свидания!")

if __name__ == "__main__":
    ElectronicDiary().run()
