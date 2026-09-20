# TÀI LIỆU BÀN GIAO — NGƯỜI 2: Tạo đề thi (Exam Generator)

> Tài liệu này dành cho **thành viên phụ trách phần "tạo đề"** trong nhóm.
> Bạn có thể đọc trực tiếp để tự code, HOẶC đưa nguyên file này cho 1 AI
> (Claude, ChatGPT, Copilot...) kèm 2 file đính kèm bắt buộc (xem mục 3)
> và yêu cầu AI code hộ — làm theo đúng hướng dẫn ở mục 5 để AI ra được
> code chạy đúng ngay lần đầu, không cần đoán mò.

---

## 1. Giới thiệu nội dung Người 2 cần làm

### 1.1 Bối cảnh dự án
Đồ án gồm 4 phần việc, chia cho 4 thành viên:

```
Người 1 (đã xong)     Người 2 (BẠN)              Người 3            Người 4
Quản lý dữ liệu   →   Sinh đề từ dữ liệu     →   Chấm điểm      →   Giao diện
(CRUD câu hỏi)        (sample + seed)            (theo Exam)        (Tkinter)
```

Người 1 đã hoàn thành phần "ngân hàng câu hỏi" — lưu trữ Môn học / Chủ đề / Câu hỏi, kiểm tra dữ liệu hợp lệ. Việc của bạn là **biến ngân hàng câu hỏi đó thành 1 đề thi cụ thể**: chọn ngẫu nhiên đúng số câu theo yêu cầu, xáo trộn để mỗi lần thi khác nhau, nhưng vẫn "phát lại" được y hệt khi cần.

### 1.2 Bạn cần làm được 3 việc (đây là yêu cầu bắt buộc của đồ án)

1. **Lấy N câu ngẫu nhiên theo ma trận, dùng `random.sample()`** — người dùng khai báo cần bao nhiêu câu ở mỗi (chủ đề, mức độ), hệ thống chọn ngẫu nhiên không trùng lặp, đúng số lượng. Ví dụ thực tế nhóm đang dùng: **đề 20 câu**.
2. **Trộn thứ tự đáp án theo seed** — mỗi câu trong đề có 4 phương án (A, B, C, D), phải bị xáo trộn vị trí, và việc xáo trộn phải **tái lập được** nếu dùng lại đúng `seed`.
3. **Tái lập đề từ seed cũ** — cho lại `seed` của 1 đề đã tạo trước, hệ thống phải sinh lại **y hệt** thứ tự câu và đáp án như lần đầu.

### 1.3 Thứ bạn KHÔNG cần làm
- Không cần lo phần lưu trữ/CRUD câu hỏi (Người 1 đã làm xong).
- Không cần chấm điểm (Người 3 làm).
- Không cần giao diện (Người 4 làm). Bạn chỉ viết logic thuần Python, có thể chạy độc lập bằng `python exam_generator.py`.

---

## 2. Các file Người 2 cần tạo

```
exam_generator.py              ← code chính (BẮT BUỘC)
tests/test_exam_generator.py   ← test (BẮT BUỘC)
```

Quy tắc:
- **KHÔNG sửa** `base_models.py` hay `data_repository.py` — đó là file của Người 1. Nếu thấy thiếu hàm gì, ghi chú lại để báo nhóm, không tự ý sửa hay mở file JSON trực tiếp.
- File `exam_generator.py` đặt **cùng thư mục gốc** với `base_models.py` và `data_repository.py` (không đặt trong thư mục con).
- File test đặt trong thư mục con `tests/`.

---

## 3. Nội dung liên quan lấy ở đâu

Để làm được việc này, bạn **cần được cung cấp 2 file sau** (xin từ Người 1 hoặc lấy từ kho code chung của nhóm):

| File | Vai trò | Bạn dùng để làm gì |
|---|---|---|
| `base_models.py` | Định nghĩa toàn bộ cấu trúc dữ liệu chung (`Question`, `Exam`, `ExamMatrixItem`, `DifficultyLevel`...) | Biết chính xác các class/field mình sẽ thao tác, KHÔNG tự định nghĩa lại |
| `data_repository.py` | Nơi lưu trữ và truy vấn câu hỏi thật (đọc từ file JSON) | Gọi hàm từ đây để lấy câu hỏi, không tự mở file JSON |

Ngoài ra, thư mục `data/` (do Người 1 tạo sẵn) chứa **dữ liệu mẫu thật**:
```
data/subjects_topics.json   ← danh sách Môn học, Chủ đề
data/questions.json          ← 90 câu hỏi mẫu (3 chủ đề × 2 mức độ × 15 câu/tổ hợp)
```
→ Bạn dùng thẳng dữ liệu này để test, không cần tự tạo dữ liệu giả.

**Nếu bạn đưa việc này cho AI làm:** phải đính kèm nguyên văn `base_models.py` và `data_repository.py` vào cuộc trò chuyện với AI — thiếu 2 file này AI sẽ phải đoán chữ ký hàm và rất dễ code sai lệch, không khớp được với phần của Người 1.

---

## 4. Sử dụng dữ liệu liên quan như thế nào

### 4.1 Cấu trúc dữ liệu bạn sẽ thao tác (từ `base_models.py`)

```python
DifficultyLevel        # enum: DE (Dễ), KHO (Khó) — CHỈ 2 giá trị, không phải 4
Question(id, topic_id, content, difficulty, options: list[Option], created_at)
Option(id, content, is_correct)
ExamMatrixItem(topic_id: str, difficulty: DifficultyLevel, num_questions: int)
Exam(id, subject_id, title, seed, question_ids: list[str], shuffled_options: dict, created_at)
```

⚠️ **Lưu ý bắt buộc:** `Question.is_valid()` (phía Người 1) đã ép cứng **mỗi câu hỏi có ĐÚNG 4 phương án**. Nghĩa là mọi câu bạn lấy ra từ `repo` luôn có sẵn đúng 4 phương án — bạn không cần tự đếm/kiểm tra lại.

### 4.2 Các hàm bạn được phép gọi (từ `data_repository.py`)

```python
from data_repository import JsonDataRepository

repo = JsonDataRepository("data/subjects_topics.json", "data/questions.json")

repo.list_questions(topic_id=None, difficulty=None) -> list[Question]
# Lọc câu hỏi theo chủ đề và/hoặc mức độ. Đây là hàm CHÍNH bạn dùng để lấy
# "ứng viên" trước khi random.sample().

repo.count_questions(topic_id, difficulty) -> int
# Đếm nhanh số câu có sẵn — dùng để kiểm tra đủ câu TRƯỚC KHI sample(),
# tránh lỗi khó hiểu từ thư viện random.

repo.get_question(question_id) -> Optional[Question]
# Lấy chi tiết 1 câu hỏi (bao gồm 4 phương án) theo id — dùng khi cần
# trộn thứ tự phương án của từng câu đã chọn.

repo.get_question_bank_summary() -> dict
# Thống kê tổng quan ngân hàng câu hỏi (không bắt buộc dùng, tham khảo thêm).
```

**Nguyên tắc:** bạn CHỈ đọc dữ liệu qua `repo`, tuyệt đối không tự `open()`/`json.load()` file JSON — vì cách lưu trữ bên trong có thể đổi (ví dụ nhóm có bản thay thế bằng SQL), nhưng các hàm trên vẫn giữ nguyên chữ ký, code của bạn sẽ không bị vỡ.

### 4.3 Ví dụ dữ liệu thật để test thử ngay

```python
repo = JsonDataRepository("data/subjects_topics.json", "data/questions.json")
topics = repo.list_topics()   # có sẵn 3 chủ đề mẫu

# Kiểm tra nhanh số câu có sẵn mỗi mức độ
for topic in topics:
    print(topic.name, "- Dễ:", repo.count_questions(topic.id, DifficultyLevel.DE),
          "- Khó:", repo.count_questions(topic.id, DifficultyLevel.KHO))
# Kết quả: mỗi chủ đề có 15 câu Dễ + 15 câu Khó => đủ để rút đề 20 câu
```

---

## 5. Trình bày để AI khác hoàn thành hiệu quả (và code chạy được ngay)

Nếu bạn không tự code mà nhờ AI, làm theo đúng quy trình sau để đảm bảo AI code ra kết quả **khớp 100%** với phần của Người 1 và **chạy được ngay lần đầu**:

### Bước 1 — Đính kèm đúng 3 thứ vào cuộc trò chuyện với AI
1. Nguyên văn file `base_models.py`
2. Nguyên văn file `data_repository.py`
3. Toàn bộ tài liệu này (`README_NGUOI_2.md`)

### Bước 2 — Dùng prompt mẫu sau (copy nguyên văn, sửa lại nếu cần)

```
Tôi đính kèm 3 file: base_models.py, data_repository.py, và README_NGUOI_2.md.
Hãy đọc kỹ base_models.py và data_repository.py trước, CHỈ dùng đúng các
class/hàm đã có sẵn trong 2 file đó — không tự đổi tên, không tự thêm
tham số, không tự định nghĩa lại bất kỳ class nào đã có.

Nhiệm vụ: viết file exam_generator.py theo ĐÚNG spec trong README_NGUOI_2.md
(mục 6 và 7) — implement class RandomExamGenerator(ExamGenerator) với 2 hàm
generate_exam() và rebuild_exam(), giữ đúng chữ ký hàm.

Sau khi viết xong, hãy TỰ CHẠY THỬ code (không chỉ đưa code):
1. Chạy demo trong exam_generator.py, đảm bảo không lỗi.
2. Viết và chạy tests/test_exam_generator.py với toàn bộ 9 test case ở mục 8
   của README, đảm bảo PASS hết.
3. Thử tạo 1 đề 20 câu thật bằng dữ liệu mẫu có sẵn trong data/, in ra để
   xác nhận: đủ 20 câu, không trùng câu, rebuild_exam() ra kết quả y hệt
   bản gốc.
Chỉ báo hoàn thành sau khi cả 3 bước trên chạy sạch không lỗi.
```

### Bước 3 — Sau khi nhận code từ AI, tự kiểm tra lại bằng checklist ở mục 9 trước khi nộp cho nhóm

**Vì sao phải làm đúng quy trình này:** nếu chỉ đưa README mà không đính kèm `base_models.py`/`data_repository.py`, AI sẽ phải TỰ ĐOÁN chữ ký hàm dựa theo đoạn code ví dụ trong README — dễ đoán sai chi tiết nhỏ (thứ tự tham số, tên biến trong constructor...), khiến code của bạn không gọi được hàm của Người 1, phải sửa lại từ đầu.

---

## 6. Thiết kế chi tiết — `generate_exam()`

### 6.1 Chữ ký hàm (bắt buộc giữ nguyên)

```python
def generate_exam(self, subject_id: str, title: str,
                   matrix: list[ExamMatrixItem], seed: int) -> Exam:
```

### 6.2 Input mẫu — ma trận cho đề 20 câu

```python
# Trộn cả 2 mức độ:
matrix = [
    ExamMatrixItem(topic_id="topic_abc", difficulty=DifficultyLevel.DE, num_questions=5),
    ExamMatrixItem(topic_id="topic_abc", difficulty=DifficultyLevel.KHO, num_questions=5),
    ExamMatrixItem(topic_id="topic_xyz", difficulty=DifficultyLevel.DE, num_questions=5),
    ExamMatrixItem(topic_id="topic_xyz", difficulty=DifficultyLevel.KHO, num_questions=5),
]

# Hoặc TOÀN BỘ 1 mức độ duy nhất (không bắt buộc phải trộn Dễ/Khó):
matrix = [
    ExamMatrixItem(topic_id="topic_abc", difficulty=DifficultyLevel.DE, num_questions=7),
    ExamMatrixItem(topic_id="topic_def", difficulty=DifficultyLevel.DE, num_questions=7),
    ExamMatrixItem(topic_id="topic_xyz", difficulty=DifficultyLevel.DE, num_questions=6),
]
# Tổng num_questions của toàn bộ matrix PHẢI = 20 (hoặc bất kỳ tổng số câu cần)
```

### 6.3 Thuật toán — làm theo ĐÚNG thứ tự bước sau

```
BƯỚC 1: Tạo bộ sinh số ngẫu nhiên RIÊNG cho hàm này
    rng = random.Random(seed)
    # QUAN TRỌNG: KHÔNG dùng random.seed(seed) + random.sample() (hàm global).
    # Random toàn cục có thể bị code khác trong app (GUI, phần khác) làm
    # thay đổi state, khiến kết quả sample() không tái lập chính xác được.
    # Luôn tạo instance random.Random(seed) riêng, chỉ dùng rng trong hàm này.

BƯỚC 2: Với TỪNG ExamMatrixItem trong matrix — đây là bước dùng sample():
    2.1. Lấy danh sách câu hỏi ứng viên:
         candidates = repo.list_questions(topic_id=item.topic_id, difficulty=item.difficulty)
    2.2. Kiểm tra đủ số lượng trước khi sample (tránh lỗi khó hiểu từ random):
         if len(candidates) < item.num_questions:
             raise ValueError(
                 f"Không đủ câu hỏi: chủ đề '{item.topic_id}' mức '{item.difficulty}' "
                 f"chỉ có {len(candidates)} câu, cần {item.num_questions} câu"
             )
    2.3. Chọn ngẫu nhiên KHÔNG TRÙNG LẶP bằng sample():
         selected = rng.sample(candidates, item.num_questions)
    2.4. Gom id các câu đã chọn vào 1 danh sách chung all_question_ids

BƯỚC 3: Trộn THỨ TỰ CÁC CÂU xuất hiện trong đề
    rng.shuffle(all_question_ids)   # đổi thứ tự câu 1,2,3,... không đổi nội dung câu

BƯỚC 4: TRỘN THỨ TỰ ĐÁP ÁN — với MỖI câu hỏi đã chọn (đây là yêu cầu #2 ở mục 1.2)
    shuffled_options = {}   # dict: {question_id: [option_id đã trộn thứ tự,...]}
    for question_id in all_question_ids:
        question = repo.get_question(question_id)
        option_ids = [opt.id for opt in question.options]   # luôn có đúng 4 phần tử
        rng.shuffle(option_ids)
        shuffled_options[question_id] = option_ids

BƯỚC 5: Tạo object Exam và trả về
    exam = Exam.create(subject_id, title, seed)
    exam.question_ids = all_question_ids
    exam.shuffled_options = shuffled_options
    return exam
```

### 6.4 Lỗi thường gặp cần tránh
- Dùng `random.seed()` global thay vì `random.Random(seed)` riêng → kết quả không ổn định.
- Gọi `sample()`/`shuffle()` sai thứ tự BƯỚC 2 → 3 → 4 → cùng seed nhưng ra kết quả khác (mỗi lần gọi `rng` đều tiêu thụ trạng thái ngẫu nhiên tiếp theo, đảo thứ tự lệnh gọi là đảo luôn kết quả).
- Quên kiểm tra đủ số lượng (bước 2.2) → lỗi gốc `Sample larger than population` khó hiểu, nên tự raise lỗi rõ ràng trước.
- Xin quá số câu ngân hàng đang có (dữ liệu mẫu: 15 câu/tổ hợp chủ đề×mức độ, tối đa 45 câu/mức độ toàn ngân hàng) → báo lỗi là ĐÚNG, không phải bug.

---

## 7. Thiết kế chi tiết — `rebuild_exam()` (yêu cầu #3 ở mục 1.2)

### 7.1 Mục đích
Cho lại **đúng object `Exam` đã lưu trước đó** (có sẵn `question_ids` từ lần tạo đầu), hàm này sinh lại **y hệt** thứ tự câu và thứ tự đáp án như lần đầu — chỉ cần dựa vào `exam.seed`.

### 7.2 Thuật toán

Vì `exam.question_ids` đã lưu sẵn đúng danh sách câu đã chọn (từ BƯỚC 2 ở mục 6.3), **không cần chạy lại `sample()`** — chỉ cần chạy lại BƯỚC 3 và BƯỚC 4 (phần shuffle) trên chính `exam.question_ids`:

```python
def rebuild_exam(self, exam: Exam) -> Exam:
    rng = random.Random(exam.seed)

    question_ids = list(exam.question_ids)   # lấy lại đúng câu đã chọn, KHÔNG sample lại
    rng.shuffle(question_ids)                # đúng BƯỚC 3

    shuffled_options = {}
    for question_id in question_ids:
        question = repo.get_question(question_id)
        option_ids = [opt.id for opt in question.options]
        rng.shuffle(option_ids)              # đúng BƯỚC 4
        shuffled_options[question_id] = option_ids

    exam.question_ids = question_ids
    exam.shuffled_options = shuffled_options
    return exam
```

⚠️ Cách này chỉ đúng nếu `generate_exam()` lưu `exam.question_ids` là danh sách **SAU BƯỚC 2 (đã chọn xong bằng sample), TRƯỚC BƯỚC 3 (chưa shuffle)**.

**Giới hạn cần nêu trong báo cáo:** cách này giả định ngân hàng câu hỏi không bị xóa/sửa câu đã dùng trong đề sau khi tạo — nếu 1 câu trong `question_ids` bị xóa khỏi ngân hàng, `rebuild_exam()` sẽ lỗi khi gọi `repo.get_question()`.

---

## 8. Test bắt buộc phải viết (`tests/test_exam_generator.py`)

Dùng `unittest`, theo mẫu `tests/test_data_repository.py` đã có (setUp tạo `repo` test riêng bằng đường dẫn file JSON tạm, tearDown dọn dẹp file test sau mỗi lần chạy).

Chuẩn bị trong `setUp`: tạo sẵn 1 subject, 1 topic, và **ít nhất 5 câu hỏi cùng topic/difficulty**, mỗi câu đủ 4 phương án.

| # | Test case | Kiểm tra gì |
|---|---|---|
| 1 | `test_generate_exam_correct_question_count` | Tổng số câu trong đề = tổng `num_questions` trong matrix |
| 2 | `test_generate_exam_no_duplicate_questions` | `len(set(exam.question_ids)) == len(exam.question_ids)` |
| 3 | `test_generate_exam_respects_difficulty` | Mỗi câu trong đề đúng topic/difficulty đã khai trong matrix |
| 4 | `test_generate_exam_raises_when_not_enough_questions` | matrix yêu cầu nhiều hơn số câu có sẵn → raise `ValueError` |
| 5 | `test_same_seed_produces_same_exam` | Gọi `generate_exam()` 2 lần cùng `seed` → `question_ids` và `shuffled_options` giống hệt |
| 6 | `test_different_seed_produces_different_order` | Cùng matrix, seed khác nhau → thứ tự câu khác nhau |
| 7 | `test_rebuild_exam_matches_original` | `generate_exam()` rồi `rebuild_exam()` cùng exam đó → giống hệt bản gốc — **test quan trọng nhất cho yêu cầu #3** |
| 8 | `test_each_question_has_exactly_4_shuffled_options` | Mỗi câu trong `shuffled_options` có đúng 4 phần tử, tập hợp giống hệt tập `option_id` gốc — **test cho yêu cầu #2** |
| 9 | `test_generate_exam_with_single_difficulty_only` | Ma trận chỉ dùng 1 mức độ duy nhất (toàn `DE` hoặc toàn `KHO`) rải đều nhiều chủ đề, vẫn ra đúng tổng số câu |

---

## 9. Checklist nghiệm thu trước khi nộp/báo cáo nhóm

- [ ] `python exam_generator.py` chạy demo không lỗi
- [ ] `python -m unittest tests.test_exam_generator -v` toàn bộ PASS
- [ ] Test #5 và #7 chắc chắn phải pass — chứng minh đúng yêu cầu "trộn theo seed" và "tái lập đề theo seed"
- [ ] Đã thử với ma trận tổng = 20 câu thật (dùng đúng dữ liệu mẫu trong `data/`), cả trường hợp trộn 2 mức lẫn chỉ 1 mức độ
- [ ] Không import trực tiếp file JSON, chỉ qua `repo`
- [ ] Không dùng `random.seed()` global, chỉ dùng `random.Random(seed)` cục bộ
- [ ] Đã viết đoạn giải thích trong báo cáo: thuật toán rebuild dựa trên `question_ids` đã lưu sẵn, không sample lại — nêu rõ giới hạn nếu câu hỏi bị xóa sau khi tạo đề

---

## 10. Bàn giao tiếp cho Người 3 và Người 4

- **Người 3 (Grader)** sẽ nhận object `Exam` bạn tạo ra (có `question_ids`, `shuffled_options`) để chấm điểm — họ không cần biết thuật toán sinh đề bên trong `exam_generator.py`.
- **Người 4 (GUI)** sẽ gọi `generate_exam()` từ **form tạo đề**: người dùng nhập ma trận qua giao diện (chọn chủ đề, chọn Dễ/Khó, nhập số câu mỗi dòng) → GUI dựng `list[ExamMatrixItem]` → gọi hàm của bạn → nhận về `Exam` → hiển thị.

**Chữ ký hàm ở mục 6.1 và 7.2 là "hợp đồng" cuối cùng** — nếu thấy cần đổi (thêm tham số, đổi tên...), phải báo cả nhóm trước khi sửa, vì Người 3 và Người 4 sẽ code dựa trên đúng chữ ký này.
