"""
base_models.py
================
File TRUNG TÂM chứa các class cha / cấu trúc dữ liệu dùng chung
cho toàn bộ dự án "Quản lý ngân hàng câu hỏi & tạo đề kiểm tra".

QUY TẮC CHO CẢ NHÓM:
- KHÔNG copy các class dưới đây sang file khác, chỉ import.
- KHÔNG tự ý đổi tên field trong dataclass (Subject, Topic, Question...).
- Muốn thêm field mới -> bàn với cả nhóm rồi sửa DUY NHẤT ở file này.
- Mỗi class ABC (abstract) là "hợp đồng" - class con PHẢI implement đủ
  các @abstractmethod, nếu thiếu Python sẽ báo lỗi ngay khi khởi tạo.

PHÂN CHIA GỢI Ý CHO 4 THÀNH VIÊN (dựa trên đề bài):
- Member A: CRUD ngân hàng câu hỏi (implement QuestionRepository)
- Member B: Tạo đề theo ma trận mức độ + trộn câu/seed (implement ExamGenerator)
- Member C: Chấm điểm, thống kê theo chủ đề (implement Grader)
- Member D: Giao diện Tkinter (Treeview, Text, form, Canvas biểu đồ)
           + Custom QuestionEditor, xuất file
Tất cả đều import model (Subject, Topic, Question...) từ file này.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


# ============================================================
# 1. ENUM - các giá trị cố định, tránh mỗi người gõ chuỗi khác nhau
# ============================================================

class DifficultyLevel(str, Enum):
    """Mức độ câu hỏi. Dùng Enum thay vì gõ tay "de"/"kho" để tránh sai chính tả."""
    DE = "de"      # Dễ
    KHO = "kho"    # Khó


# Đã bỏ QuestionType (single/multi choice) - hệ thống chỉ hỗ trợ 1 đáp án đúng/câu,
# nên không cần phân loại loại câu hỏi nữa.


# ============================================================
# 2. HELPER - sinh ID thống nhất cho toàn hệ thống
# ============================================================

def generate_id(prefix: str) -> str:
    """Mọi entity đều dùng hàm này để sinh id, KHÔNG tự chế kiểu id riêng."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# ============================================================
# 3. BASE ENTITY - class cha cho mọi đối tượng có id + created_at
# ============================================================

@dataclass
class BaseEntity:
    id: str
    created_at: datetime = field(default_factory=datetime.now)


# ============================================================
# 4. DỮ LIỆU CHÍNH: Môn học - Chủ đề - Câu hỏi - Phương án - Đề thi - Kết quả
# ============================================================

@dataclass
class Subject(BaseEntity):
    """Môn học. Ví dụ: Lập trình Python, Kinh tế vi mô..."""
    name: str = ""
    description: str = ""

    @staticmethod
    def create(name: str, description: str = "") -> "Subject":
        return Subject(id=generate_id("subj"), name=name, description=description)


@dataclass
class Topic(BaseEntity):
    """Chủ đề thuộc 1 môn học. Ví dụ môn Python -> chủ đề 'Vòng lặp'."""
    subject_id: str = ""
    name: str = ""

    @staticmethod
    def create(subject_id: str, name: str) -> "Topic":
        return Topic(id=generate_id("topic"), subject_id=subject_id, name=name)


@dataclass
class Option:
    """Một phương án trả lời (KHÔNG kế thừa BaseEntity vì không cần created_at)."""
    id: str
    content: str
    is_correct: bool = False

    @staticmethod
    def create(content: str, is_correct: bool = False) -> "Option":
        return Option(id=generate_id("opt"), content=content, is_correct=is_correct)


@dataclass
class Question(BaseEntity):
    """
    Câu hỏi trong ngân hàng đề.
    LƯU Ý: options là list[Option]; đáp án đúng nằm trong Option.is_correct,
    KHÔNG tạo thêm field 'answer' riêng để tránh 2 nguồn dữ liệu lệch nhau.
    """
    topic_id: str = ""
    content: str = ""
    difficulty: DifficultyLevel = DifficultyLevel.DE
    options: list[Option] = field(default_factory=list)

    @staticmethod
    def create(topic_id: str, content: str, difficulty: DifficultyLevel,
               options: list[Option]) -> "Question":
        return Question(
            id=generate_id("q"),
            topic_id=topic_id,
            content=content,
            difficulty=difficulty,
            options=options,
        )

    def correct_option_ids(self) -> list[str]:
        return [opt.id for opt in self.options if opt.is_correct]

    def is_valid(self) -> tuple[bool, str]:
        """
        Kiểm tra nội dung và đáp án hợp lệ (đúng yêu cầu đề bài: 'Kiểm tra
        nội dung và đáp án'). Mọi người dùng lại hàm này, KHÔNG viết validate riêng.
        Hệ thống chỉ hỗ trợ 1 đáp án đúng/câu (single choice).
        """
        if not self.content.strip():
            return False, "Nội dung câu hỏi không được rỗng"
        if len(self.options) != 4:
            return False, "Câu hỏi phải có đúng 4 phương án"
        correct_count = len(self.correct_option_ids())
        if correct_count == 0:
            return False, "Câu hỏi phải có ít nhất 1 đáp án đúng"
        if correct_count > 1:
            return False, "Câu hỏi chỉ được có đúng 1 đáp án đúng (single choice)"
        return True, "OK"


@dataclass
class ExamMatrixItem:
    """1 dòng trong ma trận đề: lấy bao nhiêu câu ở mức độ nào, thuộc chủ đề nào."""
    topic_id: str
    difficulty: DifficultyLevel
    num_questions: int


@dataclass
class Exam(BaseEntity):
    """
    Đề thi được sinh ra. seed dùng để TÁI LẬP đề (yêu cầu 'nâng cao' trong đề bài):
    cùng 1 seed + cùng ngân hàng câu hỏi -> sinh lại đúng đề y hệt.
    """
    subject_id: str = ""
    title: str = ""
    seed: int = 0
    question_ids: list[str] = field(default_factory=list)
    # Lưu thứ tự phương án đã bị trộn cho từng câu: {question_id: [option_id,...]}
    shuffled_options: dict = field(default_factory=dict)

    @staticmethod
    def create(subject_id: str, title: str, seed: int) -> "Exam":
        return Exam(id=generate_id("exam"), subject_id=subject_id, title=title, seed=seed)


@dataclass
class StudentAnswer:
    """Câu trả lời của học sinh cho 1 câu hỏi trong đề."""
    question_id: str
    selected_option_ids: list[str] = field(default_factory=list)


@dataclass
class ExamResult(BaseEntity):
    """Kết quả làm bài của 1 học sinh cho 1 đề."""
    exam_id: str = ""
    student_name: str = ""
    answers: list[StudentAnswer] = field(default_factory=list)
    score: float = 0.0
    # Thống kê số câu đúng/tổng theo từng chủ đề: {topic_id: (dung, tong)}
    topic_stats: dict = field(default_factory=dict)

    @staticmethod
    def create(exam_id: str, student_name: str) -> "ExamResult":
        return ExamResult(id=generate_id("result"), exam_id=exam_id, student_name=student_name)


# ============================================================
# 5. ABSTRACT CLASSES - "hợp đồng" cho từng mảng chức năng
# ============================================================

class SubjectTopicRepository(ABC):
    """
    [Member A phụ trách - cùng nhóm với QuestionRepository]
    CRUD ĐẦY ĐỦ cho Môn học và Chủ đề. Tách riêng khỏi QuestionRepository vì
    Môn/Chủ đề là dữ liệu "cha", Câu hỏi là dữ liệu "con" tham chiếu tới chúng.

    QUY TẮC RÀNG BUỘC (áp dụng cho mọi implementation):
    - delete_subject: PHẢI raise lỗi nếu môn học còn chủ đề con.
    - delete_topic: PHẢI raise lỗi nếu chủ đề còn câu hỏi con.
      (Người dùng phải xóa hết câu hỏi/chủ đề con trước - tránh dữ liệu mồ côi)
    """

    @abstractmethod
    def add_subject(self, subject: Subject) -> None:
        pass

    @abstractmethod
    def update_subject(self, subject_id: str, subject: Subject) -> None:
        pass

    @abstractmethod
    def delete_subject(self, subject_id: str) -> None:
        pass

    @abstractmethod
    def add_topic(self, topic: Topic) -> None:
        pass

    @abstractmethod
    def update_topic(self, topic_id: str, topic: Topic) -> None:
        pass

    @abstractmethod
    def delete_topic(self, topic_id: str) -> None:
        pass

    @abstractmethod
    def list_subjects(self) -> list[Subject]:
        pass

    @abstractmethod
    def list_topics(self, subject_id: Optional[str] = None) -> list[Topic]:
        pass

    @abstractmethod
    def get_subject(self, subject_id: str) -> Optional[Subject]:
        pass

    @abstractmethod
    def get_topic(self, topic_id: str) -> Optional[Topic]:
        pass


class QuestionRepository(ABC):
    """
    [Member A phụ trách] CRUD ngân hàng câu hỏi.
    Mọi implementation (lưu JSON, CSV, SQLite...) đều PHẢI có đủ 5 hàm này,
    với ĐÚNG kiểu tham số/trả về như khai báo -> các thành viên khác
    gọi hàm mà không cần quan tâm lưu trữ bên dưới là gì.
    """

    @abstractmethod
    def add_question(self, question: Question) -> None:
        pass

    @abstractmethod
    def update_question(self, question_id: str, question: Question) -> None:
        pass

    @abstractmethod
    def delete_question(self, question_id: str) -> None:
        pass

    @abstractmethod
    def get_question(self, question_id: str) -> Optional[Question]:
        pass

    @abstractmethod
    def list_questions(self, topic_id: Optional[str] = None,
                        difficulty: Optional[DifficultyLevel] = None) -> list[Question]:
        """Lọc câu hỏi theo chủ đề và/hoặc mức độ, dùng cho cả Treeview lẫn tạo đề."""
        pass

    @abstractmethod
    def count_questions(self, topic_id: str, difficulty: DifficultyLevel) -> int:
        """
        Đếm số câu hỏi hiện có theo (chủ đề, mức độ).
        [Người 2] PHẢI gọi hàm này TRƯỚC khi random.sample() để kiểm tra
        đủ số lượng câu hỏi theo ma trận đề, tránh lỗi 'sample lớn hơn population'.
        """
        pass


class ExamGenerator(ABC):
    """
    [Member B phụ trách] Tạo đề theo ma trận mức độ (dùng random.sample())
    và trộn thứ tự câu/phương án theo seed (dùng 1 instance random.Random(seed)
    RIÊNG cho từng lần tạo đề, KHÔNG dùng random.seed(seed) toàn cục).
    """

    @abstractmethod
    def generate_exam(self, subject_id: str, title: str,
                       matrix: list[ExamMatrixItem], seed: int) -> Exam:
        """Sinh đề mới theo ma trận. PHẢI tạo rng = random.Random(seed) RIÊNG
        (không dùng random.seed() toàn cục) trước khi gọi rng.sample()/
        rng.shuffle(), để đảm bảo tái lập được (yêu cầu nâng cao) mà không
        bị ảnh hưởng bởi state random ở nơi khác trong ứng dụng (vd GUI)."""
        pass

    @abstractmethod
    def rebuild_exam(self, exam: Exam) -> Exam:
        """Tái lập lại đúng thứ tự câu/phương án từ exam.seed đã lưu."""
        pass


class Grader(ABC):
    """[Member C phụ trách] Chấm điểm và thống kê theo chủ đề."""

    @abstractmethod
    def grade(self, exam: Exam, questions: list[Question],
              answers: list[StudentAnswer]) -> ExamResult:
        pass

    @abstractmethod
    def topic_statistics(self, result: ExamResult) -> dict:
        """Trả về dict {topic_id: {'correct': int, 'total': int, 'percent': float}}
        để Member D vẽ Canvas biểu đồ."""
        pass


class ExamExporter(ABC):
    """[Member D phụ trách - phần xuất file] Xuất đề & đáp án ra file."""

    @abstractmethod
    def export_exam(self, exam: Exam, questions: list[Question], file_path: str) -> None:
        """Xuất đề (không kèm đáp án đúng) ra file, vd .docx/.txt/.pdf."""
        pass

    @abstractmethod
    def export_answer_key(self, exam: Exam, questions: list[Question], file_path: str) -> None:
        """Xuất riêng đáp án ra file."""
        pass


# ============================================================
# 6. VÍ DỤ NHANH (chạy thử: python base_models.py)
# ============================================================

if __name__ == "__main__":
    subj = Subject.create("Lập trình Python")
    topic = Topic.create(subj.id, "Vòng lặp for/while")

    opts = [
        Option.create("for chạy trước khi kiểm tra điều kiện", False),
        Option.create("for lặp qua từng phần tử của một iterable", True),
        Option.create("while không thể dùng break", False),
        Option.create("for chỉ dùng được với số nguyên", False),
    ]
    q = Question.create(topic.id, "Đặc điểm nào đúng về vòng lặp for trong Python?",
                         DifficultyLevel.KHO, opts)

    ok, msg = q.is_valid()
    print("Question hợp lệ?", ok, "-", msg)
    print("Đáp án đúng:", q.correct_option_ids())
