"""
import_questions.py
====================
[NGƯỜI 1 sở hữu file này - phần mở rộng của data_repository.py]

Đọc câu hỏi trắc nghiệm từ file .txt (gõ bằng Notepad) hoặc .docx (Word)
theo ĐỊNH DẠNG CỐ ĐỊNH bên dưới, rồi tự động thêm vào ngân hàng câu hỏi.

ĐỊNH DẠNG FILE (xem mẫu: mau_cau_hoi.txt) - mỗi câu hỏi cách nhau bằng dòng trống:

    MÔN: <tên môn học - phải đã tồn tại trong hệ thống>
    CHỦ ĐỀ: <tên chủ đề - phải đã tồn tại, thuộc đúng môn trên>
    MỨC ĐỘ: Dễ | Khó
    CÂU: <nội dung câu hỏi>
    A. <phương án 1>
    B. <phương án 2>
    C. <phương án 3>
    D. <phương án 4>
    ĐÁP ÁN: <1 chữ cái, ví dụ B>

LƯU Ý:
- PHẢI có đúng 4 phương án (A, B, C, D) cho mỗi câu hỏi - hệ thống ép cứng
  đúng 4 phương án ở base_models.py (Question.is_valid()). Câu thiếu/thừa
  phương án sẽ bị từ chối và báo lỗi rõ ràng khi import.
- Chỉ hỗ trợ 1 đáp án đúng (đúng với thiết kế hiện tại của hệ thống).
- MÔN và CHỦ ĐỀ phải TẠO SẴN trước (bằng repo.add_subject/add_topic),
  script này KHÔNG tự tạo môn/chủ đề mới - để tránh gõ sai tên tạo lộn xộn.

CÁCH DÙNG:
    python import_questions.py mau_cau_hoi.txt
    python import_questions.py de_thi.docx

CÀI THÊM THƯ VIỆN (chỉ cần nếu đọc file .docx):
    pip install python-docx
"""

import re
import sys
from typing import Optional

from base_models import Question, Option, DifficultyLevel
from data_repository import JsonDataRepository


# Ánh xạ nhãn tiếng Việt -> DifficultyLevel, không phân biệt hoa/thường
DIFFICULTY_LABELS = {
    "dễ": DifficultyLevel.DE,
    "khó": DifficultyLevel.KHO,
}


class ImportError_(Exception):
    """Lỗi khi 1 khối câu hỏi trong file không đúng định dạng."""
    pass


# ============================================================
# BƯỚC 1: Đọc nội dung thô từ file (.txt hoặc .docx)
# ============================================================

def read_raw_text(file_path: str) -> str:
    if file_path.lower().endswith(".docx"):
        return _read_docx(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _read_docx(file_path: str) -> str:
    try:
        import docx  # thư viện python-docx
    except ImportError:
        raise RuntimeError(
            "Chưa cài thư viện python-docx. Chạy: pip install python-docx"
        )
    document = docx.Document(file_path)
    lines = [p.text for p in document.paragraphs]
    return "\n".join(lines)


# ============================================================
# BƯỚC 2: Tách văn bản thành từng KHỐI câu hỏi (cách nhau bởi dòng trống)
# ============================================================

def split_into_blocks(raw_text: str) -> list[str]:
    # Chuẩn hóa xuống dòng, bỏ dòng trắng thừa ở 2 đầu file
    raw_text = raw_text.strip()
    # 1 khối = 1 đoạn văn bản không có dòng trống ở giữa
    blocks = re.split(r"\n\s*\n", raw_text)
    return [b.strip() for b in blocks if b.strip()]


# ============================================================
# BƯỚC 3: Parse 1 khối văn bản -> dict dữ liệu thô
# ============================================================

def parse_block(block: str, block_index: int) -> dict:
    lines = [line.strip() for line in block.splitlines() if line.strip()]

    result = {"subject": None, "topic": None, "difficulty": None,
              "content": None, "options": [], "answer_letter": None}

    for line in lines:
        if line.upper().startswith("MÔN:"):
            result["subject"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("CHỦ ĐỀ:"):
            result["topic"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("MỨC ĐỘ:"):
            result["difficulty"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("CÂU:"):
            result["content"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("ĐÁP ÁN:"):
            result["answer_letter"] = line.split(":", 1)[1].strip().upper()
        else:
            # Dòng phương án dạng "A. nội dung" hoặc "A) nội dung"
            match = re.match(r"^([A-Za-z])[\.\)]\s*(.+)$", line)
            if match:
                letter, content = match.group(1).upper(), match.group(2).strip()
                result["options"].append((letter, content))

    # Kiểm tra đủ trường bắt buộc
    missing = [k for k in ("subject", "topic", "difficulty", "content", "answer_letter")
               if not result[k]]
    if missing:
        raise ImportError_(
            f"Khối câu hỏi #{block_index}: thiếu trường {missing}.\nNội dung khối:\n{block}"
        )
    if len(result["options"]) < 2:
        raise ImportError_(
            f"Khối câu hỏi #{block_index}: cần ít nhất 2 phương án (A, B,...).\nNội dung khối:\n{block}"
        )
    return result


# ============================================================
# BƯỚC 4: Chuyển dict thô -> object Question (tra cứu topic_id qua repo)
# ============================================================

def resolve_topic_id(repo: JsonDataRepository, subject_name: str, topic_name: str) -> str:
    subject = next((s for s in repo.list_subjects()
                     if s.name.strip().lower() == subject_name.strip().lower()), None)
    if subject is None:
        raise ImportError_(f"Không tìm thấy môn học '{subject_name}'. Hãy tạo môn này trước.")

    topic = next((t for t in repo.list_topics(subject.id)
                   if t.name.strip().lower() == topic_name.strip().lower()), None)
    if topic is None:
        raise ImportError_(
            f"Không tìm thấy chủ đề '{topic_name}' trong môn '{subject_name}'. Hãy tạo chủ đề này trước."
        )
    return topic.id


def resolve_difficulty(label: str) -> DifficultyLevel:
    normalized = label.strip().lower()
    if normalized in DIFFICULTY_LABELS:
        return DIFFICULTY_LABELS[normalized]
    # Cho phép gõ thẳng giá trị enum kiểu "de" hoặc "kho" cũng được chấp nhận
    try:
        return DifficultyLevel(normalized.replace(" ", "_"))
    except ValueError:
        raise ImportError_(
            f"Mức độ '{label}' không hợp lệ. Chỉ chấp nhận: "
            "Dễ, Khó"
        )


def build_question(repo: JsonDataRepository, raw: dict) -> Question:
    topic_id = resolve_topic_id(repo, raw["subject"], raw["topic"])
    difficulty = resolve_difficulty(raw["difficulty"])

    options = [Option.create(content, letter == raw["answer_letter"])
               for letter, content in raw["options"]]

    if not any(o.is_correct for o in options):
        valid_letters = [letter for letter, _ in raw["options"]]
        raise ImportError_(
            f"ĐÁP ÁN '{raw['answer_letter']}' không khớp với phương án nào "
            f"({valid_letters}). Câu hỏi: {raw['content']}"
        )

    return Question.create(topic_id, raw["content"], difficulty, options)


# ============================================================
# BƯỚC 5: Hàm tổng - import cả file, KHÔNG dừng giữa chừng khi 1 câu lỗi
# ============================================================

def import_questions_from_file(repo: JsonDataRepository, file_path: str) -> dict:
    """
    Trả về báo cáo:
        {"success": int, "failed": int, "errors": list[str]}
    Câu nào lỗi sẽ bị BỎ QUA (không làm hỏng cả file), lỗi được ghi lại
    để người dùng biết sửa câu nào.
    """
    raw_text = read_raw_text(file_path)
    blocks = split_into_blocks(raw_text)

    report = {"success": 0, "failed": 0, "errors": []}

    for i, block in enumerate(blocks, start=1):
        try:
            raw = parse_block(block, i)
            question = build_question(repo, raw)
            repo.add_question(question)
            report["success"] += 1
        except (ImportError_, ValueError) as e:
            report["failed"] += 1
            report["errors"].append(str(e))

    return report


# ============================================================
# CHẠY TRỰC TIẾP: python import_questions.py <đường_dẫn_file>
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python import_questions.py <đường_dẫn_file.txt hoặc .docx>")
        sys.exit(1)

    file_path = sys.argv[1]
    repo = JsonDataRepository(
        subjects_topics_path="data/subjects_topics.json",
        questions_path="data/questions.json",
    )

    result = import_questions_from_file(repo, file_path)

    print(f"Thành công: {result['success']} câu")
    print(f"Thất bại:   {result['failed']} câu")
    if result["errors"]:
        print("\n--- Chi tiết lỗi ---")
        for err in result["errors"]:
            print(f"- {err}\n")
