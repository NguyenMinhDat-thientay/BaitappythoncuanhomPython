"""
sql_repository.py
==================
Bản implementation THAY THẾ cho data_repository.py, dùng SQLite thay vì JSON.
Implement ĐÚNG 2 interface trong base_models.py:
    - SubjectTopicRepository
    - QuestionRepository

QUAN TRỌNG: Vì Người 2/3/4 chỉ gọi qua các hàm interface (add_question,
list_questions, count_questions...), họ KHÔNG cần biết bạn đổi từ JSON
sang SQL. Chỉ cần đổi 1 dòng khởi tạo repo ở nơi dùng:

    # Trước:
    repo = JsonDataRepository("data/subjects_topics.json", "data/questions.json")
    # Sau:
    repo = SqlDataRepository("data/exam_bank.db")

Toàn bộ code còn lại (import_questions.py, exam_generator.py, GUI...) giữ nguyên.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional

from base_models import (
    Subject, Topic, Question, Option,
    DifficultyLevel,
    SubjectTopicRepository, QuestionRepository,
)


SCHEMA = """
CREATE TABLE IF NOT EXISTS subjects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL,
    content TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

CREATE TABLE IF NOT EXISTS options (
    id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL,
    content TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);
"""


class SqlDataRepository(SubjectTopicRepository, QuestionRepository):

    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.db_path = db_path
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # bắt SQLite kiểm tra khóa ngoại
        return conn

    def _init_schema(self) -> None:
        conn = self._connect()
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()

    # ---------- Môn học ----------

    def add_subject(self, subject: Subject) -> None:
        conn = self._connect()
        conn.execute(
            "INSERT INTO subjects (id, name, description, created_at) VALUES (?, ?, ?, ?)",
            (subject.id, subject.name, subject.description, subject.created_at.isoformat()),
        )
        conn.commit()
        conn.close()

    def update_subject(self, subject_id: str, subject: Subject) -> None:
        conn = self._connect()
        cursor = conn.execute(
            "UPDATE subjects SET name = ?, description = ? WHERE id = ?",
            (subject.name, subject.description, subject_id),
        )
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Không tìm thấy subject id='{subject_id}'")
        conn.commit()
        conn.close()

    def delete_subject(self, subject_id: str) -> None:
        conn = self._connect()
        remaining = conn.execute(
            "SELECT COUNT(*) FROM topics WHERE subject_id = ?", (subject_id,)
        ).fetchone()[0]
        if remaining > 0:
            conn.close()
            raise ValueError(
                "Không thể xóa môn học vì vẫn còn chủ đề thuộc môn này. "
                "Hãy xóa hết chủ đề con trước."
            )
        cursor = conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Không tìm thấy subject id='{subject_id}'")
        conn.commit()
        conn.close()

    def list_subjects(self) -> list[Subject]:
        conn = self._connect()
        rows = conn.execute("SELECT id, name, description, created_at FROM subjects").fetchall()
        conn.close()
        return [Subject(id=r[0], name=r[1], description=r[2] or "",
                         created_at=datetime.fromisoformat(r[3])) for r in rows]

    def get_subject(self, subject_id: str) -> Optional[Subject]:
        conn = self._connect()
        row = conn.execute(
            "SELECT id, name, description, created_at FROM subjects WHERE id = ?", (subject_id,)
        ).fetchone()
        conn.close()
        if row is None:
            return None
        return Subject(id=row[0], name=row[1], description=row[2] or "",
                        created_at=datetime.fromisoformat(row[3]))

    # ---------- Chủ đề ----------

    def add_topic(self, topic: Topic) -> None:
        if self.get_subject(topic.subject_id) is None:
            raise ValueError(f"subject_id '{topic.subject_id}' không tồn tại")
        conn = self._connect()
        conn.execute(
            "INSERT INTO topics (id, subject_id, name, created_at) VALUES (?, ?, ?, ?)",
            (topic.id, topic.subject_id, topic.name, topic.created_at.isoformat()),
        )
        conn.commit()
        conn.close()

    def update_topic(self, topic_id: str, topic: Topic) -> None:
        if self.get_subject(topic.subject_id) is None:
            raise ValueError(f"subject_id '{topic.subject_id}' không tồn tại")
        conn = self._connect()
        cursor = conn.execute(
            "UPDATE topics SET subject_id = ?, name = ? WHERE id = ?",
            (topic.subject_id, topic.name, topic_id),
        )
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Không tìm thấy topic id='{topic_id}'")
        conn.commit()
        conn.close()

    def delete_topic(self, topic_id: str) -> None:
        conn = self._connect()
        remaining = conn.execute(
            "SELECT COUNT(*) FROM questions WHERE topic_id = ?", (topic_id,)
        ).fetchone()[0]
        if remaining > 0:
            conn.close()
            raise ValueError(
                f"Không thể xóa chủ đề vì còn {remaining} câu hỏi thuộc chủ đề này. "
                "Hãy xóa hết câu hỏi con trước."
            )
        cursor = conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Không tìm thấy topic id='{topic_id}'")
        conn.commit()
        conn.close()

    def list_topics(self, subject_id: Optional[str] = None) -> list[Topic]:
        conn = self._connect()
        if subject_id:
            rows = conn.execute(
                "SELECT id, subject_id, name, created_at FROM topics WHERE subject_id = ?",
                (subject_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT id, subject_id, name, created_at FROM topics").fetchall()
        conn.close()
        return [Topic(id=r[0], subject_id=r[1], name=r[2],
                       created_at=datetime.fromisoformat(r[3])) for r in rows]

    def get_topic(self, topic_id: str) -> Optional[Topic]:
        conn = self._connect()
        row = conn.execute(
            "SELECT id, subject_id, name, created_at FROM topics WHERE id = ?", (topic_id,)
        ).fetchone()
        conn.close()
        if row is None:
            return None
        return Topic(id=row[0], subject_id=row[1], name=row[2],
                      created_at=datetime.fromisoformat(row[3]))

    # ---------- Câu hỏi ----------

    def add_question(self, question: Question) -> None:
        ok, msg = question.is_valid()
        if not ok:
            raise ValueError(f"Câu hỏi không hợp lệ: {msg}")
        if self.get_topic(question.topic_id) is None:
            raise ValueError(f"topic_id '{question.topic_id}' không tồn tại")

        conn = self._connect()
        conn.execute(
            "INSERT INTO questions (id, topic_id, content, difficulty, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (question.id, question.topic_id, question.content,
             question.difficulty.value, question.created_at.isoformat()),
        )
        for opt in question.options:
            conn.execute(
                "INSERT INTO options (id, question_id, content, is_correct) VALUES (?, ?, ?, ?)",
                (opt.id, question.id, opt.content, int(opt.is_correct)),
            )
        conn.commit()
        conn.close()

    def update_question(self, question_id: str, question: Question) -> None:
        ok, msg = question.is_valid()
        if not ok:
            raise ValueError(f"Câu hỏi không hợp lệ: {msg}")
        if self.get_topic(question.topic_id) is None:
            raise ValueError(f"topic_id '{question.topic_id}' không tồn tại")

        conn = self._connect()
        cursor = conn.execute(
            "UPDATE questions SET topic_id = ?, content = ?, difficulty = ? WHERE id = ?",
            (question.topic_id, question.content, question.difficulty.value, question_id),
        )
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Không tìm thấy câu hỏi id='{question_id}'")

        # Xóa hết phương án cũ, ghi lại phương án mới (đơn giản, tránh so khớp từng cái)
        conn.execute("DELETE FROM options WHERE question_id = ?", (question_id,))
        for opt in question.options:
            conn.execute(
                "INSERT INTO options (id, question_id, content, is_correct) VALUES (?, ?, ?, ?)",
                (opt.id, question_id, opt.content, int(opt.is_correct)),
            )
        conn.commit()
        conn.close()

    def delete_question(self, question_id: str) -> None:
        conn = self._connect()
        conn.execute("DELETE FROM options WHERE question_id = ?", (question_id,))
        cursor = conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Không tìm thấy câu hỏi id='{question_id}'")
        conn.commit()
        conn.close()

    def get_question(self, question_id: str) -> Optional[Question]:
        conn = self._connect()
        row = conn.execute(
            "SELECT id, topic_id, content, difficulty, created_at FROM questions WHERE id = ?",
            (question_id,),
        ).fetchone()
        if row is None:
            conn.close()
            return None
        options = self._load_options(conn, question_id)
        conn.close()
        return Question(id=row[0], topic_id=row[1], content=row[2],
                         difficulty=DifficultyLevel(row[3]), options=options,
                         created_at=datetime.fromisoformat(row[4]))

    def list_questions(self, topic_id: Optional[str] = None,
                        difficulty: Optional[DifficultyLevel] = None) -> list[Question]:
        conn = self._connect()
        query = "SELECT id, topic_id, content, difficulty, created_at FROM questions WHERE 1=1"
        params = []
        if topic_id:
            query += " AND topic_id = ?"
            params.append(topic_id)
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty.value)

        rows = conn.execute(query, params).fetchall()
        result = []
        for row in rows:
            options = self._load_options(conn, row[0])
            result.append(Question(id=row[0], topic_id=row[1], content=row[2],
                                    difficulty=DifficultyLevel(row[3]), options=options,
                                    created_at=datetime.fromisoformat(row[4])))
        conn.close()
        return result

    def count_questions(self, topic_id: str, difficulty: DifficultyLevel) -> int:
        conn = self._connect()
        count = conn.execute(
            "SELECT COUNT(*) FROM questions WHERE topic_id = ? AND difficulty = ?",
            (topic_id, difficulty.value),
        ).fetchone()[0]
        conn.close()
        return count

    def get_question_bank_summary(self) -> dict:
        summary = {}
        for subject in self.list_subjects():
            topics_summary = {}
            for topic in self.list_topics(subject.id):
                counts = {level.value: self.count_questions(topic.id, level)
                          for level in DifficultyLevel}
                topics_summary[topic.id] = {"topic_name": topic.name, "counts": counts}
            summary[subject.id] = {"subject_name": subject.name, "topics": topics_summary}
        return summary

    def _load_options(self, conn: sqlite3.Connection, question_id: str) -> list[Option]:
        rows = conn.execute(
            "SELECT id, content, is_correct FROM options WHERE question_id = ?",
            (question_id,),
        ).fetchall()
        return [Option(id=r[0], content=r[1], is_correct=bool(r[2])) for r in rows]


if __name__ == "__main__":
    # Demo nhanh, tự tạo db mới nếu chưa có
    repo = SqlDataRepository("data/exam_bank.db")
    if not repo.list_subjects():
        subj = Subject.create("Môn demo SQL")
        repo.add_subject(subj)
        topic = Topic.create(subj.id, "Chủ đề demo")
        repo.add_topic(topic)
        q = Question.create(topic.id, "1 + 1 = ?", DifficultyLevel.DE,
                             [Option.create("2", True), Option.create("3", False),
                              Option.create("4", False), Option.create("5", False)])
        repo.add_question(q)
    print(f"Số môn: {len(repo.list_subjects())}, số câu hỏi: {len(repo.list_questions())}")
