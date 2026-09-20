"""
test_data_repository.py
========================
[NGƯỜI 1 sở hữu file này]

Chạy: python -m pytest tests/test_data_repository.py -v
(hoặc: python tests/test_data_repository.py  nếu không có pytest)

Test dùng file JSON RIÊNG (test_data/...) để không đụng vào dữ liệu thật
trong data/ - mỗi lần chạy test sẽ xóa và tạo lại từ đầu.
"""

import os
import sys
import shutil
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from base_models import Subject, Topic, Question, Option, DifficultyLevel
from data_repository import JsonDataRepository


TEST_DIR = os.path.join(os.path.dirname(__file__), "test_data")


class TestJsonDataRepository(unittest.TestCase):

    def setUp(self):
        """Chạy TRƯỚC mỗi test: tạo repo sạch, không dính dữ liệu test trước đó."""
        if os.path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        self.repo = JsonDataRepository(
            subjects_topics_path=os.path.join(TEST_DIR, "subjects_topics.json"),
            questions_path=os.path.join(TEST_DIR, "questions.json"),
        )
        self.subject = Subject.create("Môn test")
        self.repo.add_subject(self.subject)
        self.topic = Topic.create(self.subject.id, "Chủ đề test")
        self.repo.add_topic(self.topic)

    def tearDown(self):
        """Chạy SAU mỗi test: dọn dẹp file test."""
        if os.path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)

    def _make_valid_question(self) -> Question:
        return Question.create(
            self.topic.id, "1 + 1 = ?", DifficultyLevel.DE,
            [Option.create("2", True), Option.create("3", False),
             Option.create("4", False), Option.create("5", False)],
        )

    # ---------- Test Subject / Topic ----------

    def test_add_and_get_subject(self):
        found = self.repo.get_subject(self.subject.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Môn test")

    def test_add_topic_with_invalid_subject_id_raises_error(self):
        bad_topic = Topic.create("subject_khong_ton_tai", "Chủ đề lỗi")
        with self.assertRaises(ValueError):
            self.repo.add_topic(bad_topic)

    def test_update_subject(self):
        self.subject.name = "Môn test (đã sửa)"
        self.repo.update_subject(self.subject.id, self.subject)
        found = self.repo.get_subject(self.subject.id)
        self.assertEqual(found.name, "Môn test (đã sửa)")

    def test_delete_subject_success_when_no_topics(self):
        empty_subject = Subject.create("Môn không có chủ đề")
        self.repo.add_subject(empty_subject)
        self.repo.delete_subject(empty_subject.id)
        self.assertIsNone(self.repo.get_subject(empty_subject.id))

    def test_delete_subject_fails_when_has_topic(self):
        """Ràng buộc quan trọng: không được xóa môn khi còn chủ đề con."""
        with self.assertRaises(ValueError):
            self.repo.delete_subject(self.subject.id)  # self.subject đã có self.topic

    def test_update_topic(self):
        self.topic.name = "Chủ đề test (đã sửa)"
        self.repo.update_topic(self.topic.id, self.topic)
        found = self.repo.get_topic(self.topic.id)
        self.assertEqual(found.name, "Chủ đề test (đã sửa)")

    def test_delete_topic_success_when_no_question(self):
        empty_topic = Topic.create(self.subject.id, "Chủ đề rỗng")
        self.repo.add_topic(empty_topic)
        self.repo.delete_topic(empty_topic.id)
        self.assertIsNone(self.repo.get_topic(empty_topic.id))

    def test_delete_topic_fails_when_has_question(self):
        """Ràng buộc quan trọng: không được xóa chủ đề khi còn câu hỏi con."""
        q = self._make_valid_question()
        self.repo.add_question(q)
        with self.assertRaises(ValueError):
            self.repo.delete_topic(self.topic.id)

    # ---------- Test CRUD câu hỏi ----------

    def test_add_question_success(self):
        q = self._make_valid_question()
        self.repo.add_question(q)
        found = self.repo.get_question(q.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.content, "1 + 1 = ?")

    def test_add_question_without_correct_option_raises_error(self):
        """Kiểm tra: câu hỏi KHÔNG có đáp án đúng phải bị từ chối."""
        bad_question = Question.create(
            self.topic.id, "Câu hỏi lỗi", DifficultyLevel.DE,
            [Option.create("A", False), Option.create("B", False),
             Option.create("C", False), Option.create("D", False)],
        )
        with self.assertRaises(ValueError):
            self.repo.add_question(bad_question)

    def test_add_question_with_empty_content_raises_error(self):
        bad_question = Question.create(
            self.topic.id, "   ", DifficultyLevel.DE,
            [Option.create("A", True), Option.create("B", False),
             Option.create("C", False), Option.create("D", False)],
        )
        with self.assertRaises(ValueError):
            self.repo.add_question(bad_question)

    def test_add_question_with_wrong_option_count_raises_error(self):
        """Ràng buộc: mỗi câu hỏi phải có ĐÚNG 4 phương án, không hơn không kém."""
        only_3_options = Question.create(
            self.topic.id, "Câu chỉ có 3 phương án", DifficultyLevel.DE,
            [Option.create("A", True), Option.create("B", False), Option.create("C", False)],
        )
        with self.assertRaises(ValueError):
            self.repo.add_question(only_3_options)

    def test_update_question(self):
        q = self._make_valid_question()
        self.repo.add_question(q)

        q.content = "1 + 1 = ? (đã sửa)"
        self.repo.update_question(q.id, q)

        found = self.repo.get_question(q.id)
        self.assertEqual(found.content, "1 + 1 = ? (đã sửa)")

    def test_delete_question(self):
        q = self._make_valid_question()
        self.repo.add_question(q)
        self.repo.delete_question(q.id)
        self.assertIsNone(self.repo.get_question(q.id))

    def test_delete_nonexistent_question_raises_error(self):
        with self.assertRaises(ValueError):
            self.repo.delete_question("id_khong_ton_tai")

    def test_list_questions_filter_by_difficulty(self):
        easy_q = self._make_valid_question()  # DE
        hard_q = Question.create(
            self.topic.id, "Câu khó", DifficultyLevel.KHO,
            [Option.create("A", True), Option.create("B", False),
             Option.create("C", False), Option.create("D", False)],
        )
        self.repo.add_question(easy_q)
        self.repo.add_question(hard_q)

        result = self.repo.list_questions(difficulty=DifficultyLevel.DE)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, easy_q.id)

    def test_list_questions_filter_by_topic(self):
        topic2 = Topic.create(self.subject.id, "Chủ đề khác")
        self.repo.add_topic(topic2)

        q1 = self._make_valid_question()
        q2 = Question.create(
            topic2.id, "Câu ở chủ đề khác", DifficultyLevel.DE,
            [Option.create("A", True), Option.create("B", False),
             Option.create("C", False), Option.create("D", False)],
        )
        self.repo.add_question(q1)
        self.repo.add_question(q2)

        result = self.repo.list_questions(topic_id=self.topic.id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, q1.id)

    # ---------- Test hàm tiện ích ----------

    def test_count_questions(self):
        self.repo.add_question(self._make_valid_question())  # DE
        count = self.repo.count_questions(self.topic.id, DifficultyLevel.DE)
        self.assertEqual(count, 1)
        count_zero = self.repo.count_questions(self.topic.id, DifficultyLevel.KHO)
        self.assertEqual(count_zero, 0)

    def test_question_bank_summary_structure(self):
        self.repo.add_question(self._make_valid_question())
        summary = self.repo.get_question_bank_summary()

        self.assertIn(self.subject.id, summary)
        self.assertEqual(summary[self.subject.id]["subject_name"], "Môn test")
        self.assertIn(self.topic.id, summary[self.subject.id]["topics"])

        counts = summary[self.subject.id]["topics"][self.topic.id]["counts"]
        self.assertEqual(counts["de"], 1)
        self.assertEqual(counts["kho"], 0)


if __name__ == "__main__":
    unittest.main()
