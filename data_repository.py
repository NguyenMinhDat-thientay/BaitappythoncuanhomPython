"""
data_repository.py
===================
[NGƯỜI 1 sở hữu file này]

Nhiệm vụ: Quản lý dữ liệu Môn học - Chủ đề - Câu hỏi bằng file JSON.
Implement 2 "hợp đồng" đã định nghĩa trong base_models.py:
    - SubjectTopicRepository  -> CRUD Môn học, Chủ đề
    - QuestionRepository      -> CRUD Câu hỏi + kiểm tra hợp lệ

CÁCH ĐỌC FILE NÀY (đọc theo đúng thứ tự để hiểu logic):
    1. Hàm _load_json / _save_json      -> đọc/ghi file JSON
    2. Hàm _to_dict / _from_dict         -> chuyển object <-> dict để lưu JSON
    3. Class JsonDataRepository          -> nơi implement toàn bộ CRUD
    4. Phần if __name__ == "__main__"    -> demo chạy thử + sinh dữ liệu mẫu

BẠN CHỈ CẦN SỬA/THÊM trong class JsonDataRepository nếu muốn mở rộng.
KHÔNG sửa base_models.py nếu chưa thống nhất với nhóm.
"""

import json
import os
from dataclasses import asdict
from datetime import datetime
from typing import Optional

from base_models import (
    Subject, Topic, Question, Option,
    DifficultyLevel,
    SubjectTopicRepository, QuestionRepository,
    generate_id,
)


# ============================================================
# BƯỚC 1: Hàm đọc/ghi file JSON (dùng chung cho mọi loại dữ liệu)
# ============================================================

def _load_json(file_path: str) -> list:
    """Đọc file JSON, nếu file chưa tồn tại thì trả về danh sách rỗng."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(file_path: str, data: list) -> None:
    """Ghi danh sách dict xuống file JSON, tạo thư mục cha nếu chưa có."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# BƯỚC 2: Chuyển đổi object <-> dict
# (JSON không lưu được object Python trực tiếp, phải quy đổi tay)
# ============================================================

def _subject_to_dict(s: Subject) -> dict:
    return {"id": s.id, "name": s.name, "description": s.description,
            "created_at": s.created_at.isoformat()}


def _subject_from_dict(d: dict) -> Subject:
    return Subject(id=d["id"], name=d["name"], description=d.get("description", ""),
                    created_at=datetime.fromisoformat(d["created_at"]))


def _topic_to_dict(t: Topic) -> dict:
    return {"id": t.id, "subject_id": t.subject_id, "name": t.name,
            "created_at": t.created_at.isoformat()}


def _topic_from_dict(d: dict) -> Topic:
    return Topic(id=d["id"], subject_id=d["subject_id"], name=d["name"],
                  created_at=datetime.fromisoformat(d["created_at"]))


def _question_to_dict(q: Question) -> dict:
    return {
        "id": q.id,
        "topic_id": q.topic_id,
        "content": q.content,
        "difficulty": q.difficulty.value,
        "options": [asdict(o) for o in q.options],
        "created_at": q.created_at.isoformat(),
    }


def _question_from_dict(d: dict) -> Question:
    options = [Option(id=o["id"], content=o["content"], is_correct=o["is_correct"])
               for o in d["options"]]
    return Question(
        id=d["id"],
        topic_id=d["topic_id"],
        content=d["content"],
        difficulty=DifficultyLevel(d["difficulty"]),
        options=options,
        created_at=datetime.fromisoformat(d["created_at"]),
    )


# ============================================================
# BƯỚC 3: Class chính - implement 2 abstract class
# ============================================================

class JsonDataRepository(SubjectTopicRepository, QuestionRepository):
    """
    Lưu trữ toàn bộ dữ liệu bằng 2 file JSON:
        - subjects_topics_path: chứa Môn học + Chủ đề
        - questions_path: chứa Câu hỏi

    Cách hoạt động: MỖI LẦN add/update/delete đều đọc file -> sửa trong
    bộ nhớ -> ghi lại file ngay. Đơn giản, dễ debug, phù hợp quy mô đồ án.
    """

    def __init__(self, subjects_topics_path: str, questions_path: str):
        self.subjects_topics_path = subjects_topics_path
        self.questions_path = questions_path

    # ============================================================
    # Môn học (Subject) - CRUD đầy đủ
    # ============================================================

    def add_subject(self, subject: Subject) -> None:
        store = self._load_store()
        if any(s["id"] == subject.id for s in store["subjects"]):
            raise ValueError(f"subject id='{subject.id}' đã tồn tại")
        store["subjects"].append(_subject_to_dict(subject))
        self._save_store(store)

    def update_subject(self, subject_id: str, subject: Subject) -> None:
        store = self._load_store()
        index = next((i for i, s in enumerate(store["subjects"]) if s["id"] == subject_id), None)
        if index is None:
            raise ValueError(f"Không tìm thấy subject id='{subject_id}'")
        subject.id = subject_id  # giữ nguyên id gốc
        store["subjects"][index] = _subject_to_dict(subject)
        self._save_store(store)

    def delete_subject(self, subject_id: str) -> None:
        store = self._load_store()
        if any(t["subject_id"] == subject_id for t in store["topics"]):
            raise ValueError(
                "Không thể xóa môn học vì vẫn còn chủ đề thuộc môn này. "
                "Hãy xóa hết chủ đề con trước."
            )
        new_subjects = [s for s in store["subjects"] if s["id"] != subject_id]
        if len(new_subjects) == len(store["subjects"]):
            raise ValueError(f"Không tìm thấy subject id='{subject_id}'")
        store["subjects"] = new_subjects
        self._save_store(store)

    def list_subjects(self) -> list[Subject]:
        store = self._load_store()
        return [_subject_from_dict(s) for s in store["subjects"]]

    def get_subject(self, subject_id: str) -> Optional[Subject]:
        for s in self.list_subjects():
            if s.id == subject_id:
                return s
        return None

    # ============================================================
    # Chủ đề (Topic) - CRUD đầy đủ
    # ============================================================

    def add_topic(self, topic: Topic) -> None:
        store = self._load_store()
        subject_ids = {s["id"] for s in store["subjects"]}
        if topic.subject_id not in subject_ids:
            raise ValueError(f"subject_id '{topic.subject_id}' không tồn tại")
        store["topics"].append(_topic_to_dict(topic))
        self._save_store(store)

    def update_topic(self, topic_id: str, topic: Topic) -> None:
        store = self._load_store()
        index = next((i for i, t in enumerate(store["topics"]) if t["id"] == topic_id), None)
        if index is None:
            raise ValueError(f"Không tìm thấy topic id='{topic_id}'")
        subject_ids = {s["id"] for s in store["subjects"]}
        if topic.subject_id not in subject_ids:
            raise ValueError(f"subject_id '{topic.subject_id}' không tồn tại")
        topic.id = topic_id  # giữ nguyên id gốc
        store["topics"][index] = _topic_to_dict(topic)
        self._save_store(store)

    def delete_topic(self, topic_id: str) -> None:
        # Chặn xóa nếu còn câu hỏi thuộc chủ đề này - tránh câu hỏi "mồ côi"
        remaining_questions = [q for q in _load_json(self.questions_path) if q["topic_id"] == topic_id]
        if remaining_questions:
            raise ValueError(
                f"Không thể xóa chủ đề vì còn {len(remaining_questions)} câu hỏi "
                "thuộc chủ đề này. Hãy xóa hết câu hỏi con trước."
            )
        store = self._load_store()
        new_topics = [t for t in store["topics"] if t["id"] != topic_id]
        if len(new_topics) == len(store["topics"]):
            raise ValueError(f"Không tìm thấy topic id='{topic_id}'")
        store["topics"] = new_topics
        self._save_store(store)

    def list_topics(self, subject_id: Optional[str] = None) -> list[Topic]:
        store = self._load_store()
        topics = [_topic_from_dict(t) for t in store["topics"]]
        if subject_id:
            topics = [t for t in topics if t.subject_id == subject_id]
        return topics

    def get_topic(self, topic_id: str) -> Optional[Topic]:
        for t in self.list_topics():
            if t.id == topic_id:
                return t
        return None

    # ============================================================
    # Câu hỏi (Question) - CRUD chính theo yêu cầu đề bài
    # ============================================================

    def add_question(self, question: Question) -> None:
        # LUÔN kiểm tra hợp lệ trước khi lưu - đúng yêu cầu "Kiểm tra nội dung và đáp án"
        ok, msg = question.is_valid()
        if not ok:
            raise ValueError(f"Câu hỏi không hợp lệ: {msg}")

        # Kiểm tra topic_id có tồn tại
        if self.get_topic(question.topic_id) is None:
            raise ValueError(f"topic_id '{question.topic_id}' không tồn tại")

        questions = _load_json(self.questions_path)
        if any(q["id"] == question.id for q in questions):
            raise ValueError(f"question id='{question.id}' đã tồn tại")
        questions.append(_question_to_dict(question))
        _save_json(self.questions_path, questions)

    def update_question(self, question_id: str, question: Question) -> None:
        ok, msg = question.is_valid()
        if not ok:
            raise ValueError(f"Câu hỏi không hợp lệ: {msg}")
        if self.get_topic(question.topic_id) is None:
            raise ValueError(f"topic_id '{question.topic_id}' không tồn tại")

        questions = _load_json(self.questions_path)
        index = next((i for i, q in enumerate(questions) if q["id"] == question_id), None)
        if index is None:
            raise ValueError(f"Không tìm thấy câu hỏi id='{question_id}'")

        question.id = question_id  # giữ nguyên id gốc, không đổi id khi update
        questions[index] = _question_to_dict(question)
        _save_json(self.questions_path, questions)

    def delete_question(self, question_id: str) -> None:
        questions = _load_json(self.questions_path)
        new_questions = [q for q in questions if q["id"] != question_id]
        if len(new_questions) == len(questions):
            raise ValueError(f"Không tìm thấy câu hỏi id='{question_id}'")
        _save_json(self.questions_path, new_questions)

    def get_question(self, question_id: str) -> Optional[Question]:
        questions = _load_json(self.questions_path)
        for q in questions:
            if q["id"] == question_id:
                return _question_from_dict(q)
        return None

    def list_questions(self, topic_id: Optional[str] = None,
                        difficulty: Optional[DifficultyLevel] = None) -> list[Question]:
        questions = [_question_from_dict(q) for q in _load_json(self.questions_path)]
        if topic_id:
            questions = [q for q in questions if q.topic_id == topic_id]
        if difficulty:
            questions = [q for q in questions if q.difficulty == difficulty]
        return questions

    def count_questions(self, topic_id: str, difficulty: DifficultyLevel) -> int:
        """[Người 2 dùng hàm này để kiểm tra đủ số câu trước khi sample()]"""
        return len(self.list_questions(topic_id=topic_id, difficulty=difficulty))

    # ============================================================
    # Hàm tổng hợp - phục vụ GUI (Người 4) và kiểm tra ma trận (Người 2)
    # ============================================================

    def get_question_bank_summary(self) -> dict:
        """
        Trả về thống kê toàn bộ ngân hàng câu hỏi, dạng:
        {
            subject_id: {
                "subject_name": str,
                "topics": {
                    topic_id: {
                        "topic_name": str,
                        "counts": {"de": 3, "kho": 2}
                    }
                }
            }
        }
        [Người 4] dùng hàm này để đổ dữ liệu vào Treeview tổng quan.
        [Người 2] dùng để kiểm tra nhanh chủ đề nào còn thiếu câu ở mức độ nào
        trước khi cho người dùng nhập ma trận đề.
        """
        summary = {}
        for subject in self.list_subjects():
            topics_summary = {}
            for topic in self.list_topics(subject.id):
                counts = {level.value: self.count_questions(topic.id, level)
                          for level in DifficultyLevel}
                topics_summary[topic.id] = {"topic_name": topic.name, "counts": counts}
            summary[subject.id] = {"subject_name": subject.name, "topics": topics_summary}
        return summary

    # ============================================================
    # Hàm nội bộ để gộp subjects + topics vào 1 file
    # ============================================================

    def _load_store(self) -> dict:
        if not os.path.exists(self.subjects_topics_path):
            return {"subjects": [], "topics": []}
        with open(self.subjects_topics_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_store(self, store: dict) -> None:
        os.makedirs(os.path.dirname(self.subjects_topics_path), exist_ok=True)
        with open(self.subjects_topics_path, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)


# ============================================================
# BƯỚC 4: DEMO - sinh dữ liệu mẫu (chạy: python data_repository.py)
# Đây chính là phần "dữ liệu JSON mẫu" mà đề bài yêu cầu.
# ============================================================

def seed_sample_data(repo: JsonDataRepository) -> None:
    """
    Tạo dữ liệu mẫu: 2 môn, 3 chủ đề, mỗi câu hỏi có ĐÚNG 4 phương án.
    Sinh đủ số lượng câu hỏi mỗi (chủ đề, mức độ) để demo việc rút đề
    theo ma trận (exam_generator.py) không bị lỗi "không đủ câu".
    """

    subj_python = Subject.create("Lập trình Python")
    subj_kt = Subject.create("Kinh tế vi mô")
    repo.add_subject(subj_python)
    repo.add_subject(subj_kt)

    topic_loop = Topic.create(subj_python.id, "Vòng lặp")
    topic_oop = Topic.create(subj_python.id, "Lập trình hướng đối tượng")
    topic_cung_cau = Topic.create(subj_kt.id, "Cung - Cầu")
    for t in (topic_loop, topic_oop, topic_cung_cau):
        repo.add_topic(t)

    # 6 câu hỏi "thật", đã bổ sung đủ 4 phương án, dùng 2 mức Dễ/Khó
    real_questions = [
        Question.create(
            topic_loop.id, "Vòng lặp for trong Python dùng để làm gì?",
            DifficultyLevel.DE,
            [Option.create("Lặp qua các phần tử của một iterable", True),
             Option.create("Chỉ dùng để lặp vô hạn", False),
             Option.create("Không thể dùng với list", False),
             Option.create("Chỉ hoạt động với số nguyên", False)],
        ),
        Question.create(
            topic_loop.id, "Kết quả của range(0, 10, 2) là dãy số nào?",
            DifficultyLevel.KHO,
            [Option.create("0,2,4,6,8", True),
             Option.create("0,1,2,...,9", False),
             Option.create("2,4,6,8,10", False),
             Option.create("0,2,4,6,8,10", False)],
        ),
        Question.create(
            topic_oop.id, "Từ khóa nào dùng để kế thừa class trong Python?",
            DifficultyLevel.DE,
            [Option.create("class Con(Cha):", True),
             Option.create("class Con extends Cha:", False),
             Option.create("class Con -> Cha:", False),
             Option.create("class Con inherits Cha:", False)],
        ),
        Question.create(
            topic_oop.id, "@abstractmethod dùng để làm gì?",
            DifficultyLevel.KHO,
            [Option.create("Bắt buộc class con phải implement hàm đó", True),
             Option.create("Xóa hàm khỏi class cha", False),
             Option.create("Chạy hàm tự động khi import", False),
             Option.create("Biến hàm thành hàm tĩnh (static)", False)],
        ),
        Question.create(
            topic_cung_cau.id, "Khi giá tăng, lượng cầu thường thay đổi thế nào?",
            DifficultyLevel.DE,
            [Option.create("Giảm", True),
             Option.create("Tăng", False),
             Option.create("Không đổi", False),
             Option.create("Tăng rồi giảm", False)],
        ),
        Question.create(
            topic_cung_cau.id, "Điểm cân bằng thị trường là điểm mà tại đó?",
            DifficultyLevel.KHO,
            [Option.create("Lượng cung = lượng cầu", True),
             Option.create("Giá = 0", False),
             Option.create("Cung lớn hơn cầu", False),
             Option.create("Cầu lớn hơn cung", False)],
        ),
    ]
    for q in real_questions:
        repo.add_question(q)

    # Sinh thêm câu hỏi mẫu để mỗi (chủ đề, mức độ) có ít nhất 15 câu,
    # đủ để demo rút đề 20 câu CÙNG 1 mức độ (3 chủ đề x 15 câu = 45 câu/mức).
    MIN_PER_COMBO = 15
    topics = [topic_loop, topic_oop, topic_cung_cau]
    for topic in topics:
        for difficulty in DifficultyLevel:
            current_count = repo.count_questions(topic.id, difficulty)
            for i in range(current_count, MIN_PER_COMBO):
                content = (f"[Câu mẫu tự sinh #{i + 1}] Chủ đề '{topic.name}' "
                           f"- mức '{difficulty.value}' - nội dung minh họa để test hệ thống")
                options = [
                    Option.create("Phương án đúng (minh họa)", True),
                    Option.create("Phương án nhiễu 1", False),
                    Option.create("Phương án nhiễu 2", False),
                    Option.create("Phương án nhiễu 3", False),
                ]
                repo.add_question(Question.create(topic.id, content, difficulty, options))

    print(f"Đã tạo {len(repo.list_subjects())} môn, "
          f"{len(repo.list_topics())} chủ đề, "
          f"{len(repo.list_questions())} câu hỏi.")


if __name__ == "__main__":
    repo = JsonDataRepository(
        subjects_topics_path="data/subjects_topics.json",
        questions_path="data/questions.json",
    )

    # Chỉ seed dữ liệu mẫu nếu chưa có dữ liệu (tránh tạo trùng mỗi lần chạy)
    if not repo.list_subjects():
        seed_sample_data(repo)
    else:
        print("Dữ liệu đã tồn tại, bỏ qua bước seed.")
        print(f"Hiện có {len(repo.list_questions())} câu hỏi trong ngân hàng.")

    # Demo: liệt kê câu hỏi mức Dễ
    print("\n--- Câu hỏi mức DỄ ---")
    for q in repo.list_questions(difficulty=DifficultyLevel.DE):
        print(f"[{q.id}] {q.content}")
