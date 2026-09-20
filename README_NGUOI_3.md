# TÀI LIỆU BÀN GIAO — NGƯỜI 3: Chấm điểm & Thống kê (Grader)

> Tài liệu này dành cho **thành viên phụ trách phần "chấm điểm"** trong nhóm.
> Đây là bản SPEC/HƯỚNG DẪN — chưa có code sẵn, bạn (hoặc AI bạn nhờ) cần
> tự viết `grader.py` và test dựa theo tài liệu này. Có thể đọc trực tiếp
> để tự code, HOẶC đưa nguyên file này cho 1 AI (Claude, ChatGPT, Copilot...)
> kèm các file đính kèm bắt buộc (xem mục 3) — làm theo đúng hướng dẫn ở
> mục 5 để AI ra được code chạy đúng ngay lần đầu.

---

## 1. Giới thiệu nội dung Người 3 cần làm

### 1.1 Bối cảnh dự án
Đồ án gồm 4 phần việc:

```
Người 1 (đã xong)     Người 2 (đã xong)          Người 3 (BẠN)      Người 4
Quản lý dữ liệu   →   Sinh đề từ dữ liệu     →   Chấm điểm      →   Giao diện
(CRUD câu hỏi)        (sample + seed)            (theo Exam)        (Tkinter)
```

Người 2 đã tạo ra `Exam` — 1 đề thi cụ thể (danh sách câu hỏi đã chọn, đáp án đã trộn thứ tự). Việc của bạn là: **nhận lại câu trả lời của học sinh, so khớp với đáp án đúng, tính điểm, và thống kê xem học sinh mạnh/yếu ở chủ đề nào** — để Người 4 vẽ biểu đồ kết quả.

### 1.2 Bạn cần làm được 2 việc (đây là yêu cầu bắt buộc của đồ án)

1. **Chấm điểm** — so khớp đáp án học sinh chọn (`StudentAnswer`) với đáp án đúng của từng câu (`Option.is_correct`), tính ra điểm số tổng.
2. **Thống kê theo chủ đề** — với mỗi chủ đề xuất hiện trong đề thi, biết được học sinh làm đúng bao nhiêu / tổng bao nhiêu câu, để vẽ biểu đồ.

### 1.3 Thứ bạn KHÔNG cần làm
- Không cần lo lưu trữ/CRUD câu hỏi (Người 1 đã làm xong).
- Không cần tạo đề, không cần trộn câu/đáp án (Người 2 đã làm xong — bạn CHỈ NHẬN `Exam` đã tạo sẵn).
- Không cần giao diện thu thập câu trả lời học sinh hay vẽ biểu đồ (Người 4 làm) — bạn chỉ viết logic thuần Python, nhận input là danh sách câu trả lời, trả ra kết quả đã tính toán.

### 1.4 Yêu cầu về phong cách code — ĐỌC KỸ TRƯỚC KHI VIẾT

Đây là đồ án nhóm, code sẽ được người khác (giáo viên, thành viên khác) đọc và chấm. Vì vậy:

- **Ưu tiên dễ hiểu hơn ngắn gọn.** Code dài hơn 1 chút nhưng rõ ràng luôn tốt hơn code ngắn nhưng khó đọc.
- **Dùng vòng lặp `for` tường minh** thay vì list comprehension lồng nhau, dict comprehension phức tạp, hay các "mẹo" Python cô đọng (walrus operator, lambda ẩn, one-liner nhiều điều kiện...). Ví dụ: thà viết 4 dòng `for` rõ ràng còn hơn 1 dòng comprehension khó dò lỗi.
- **Đặt tên biến rõ nghĩa, tiếng Việt không dấu hoặc tiếng Anh đều được**, miễn dễ hiểu (`so_cau_dung`, `correct_count` đều ổn — tránh tên như `x`, `tmp`, `d`).
- **Thêm comment giải thích Ở NHỮNG CHỖ có logic không hiển nhiên** (đặc biệt: vì sao bỏ trống câu hỏi tính là sai, vì sao chia cho tổng số câu, vì sao thêm tham số `student_name`...). Không cần comment những dòng đã tự nói lên nó làm gì.
- **Tách hàm nhỏ nếu 1 hàm làm nhiều việc** — ví dụ có thể tách riêng 1 hàm phụ để so khớp 1 câu trả lời (đúng/sai), rồi gọi lại trong `grade()`, thay vì nhồi hết logic vào 1 khối lớn.
- Không cần tối ưu hiệu năng (không cần lo Big-O) — ngân hàng câu hỏi của đồ án nhỏ, ưu tiên tuyệt đối là **dễ đọc, dễ bảo trì, dễ giải thích khi bảo vệ đồ án**.

---

## 2. Các file Người 3 cần tạo

```
grader.py                 ← code chính (BẮT BUỘC — TỰ VIẾT, chưa có sẵn)
tests/test_grader.py      ← test (BẮT BUỘC — TỰ VIẾT, chưa có sẵn)
```

Quy tắc:
- **KHÔNG sửa** `base_models.py`, `data_repository.py`, `exam_generator.py` — đó là file của Người 1 và Người 2.
- File `grader.py` đặt **cùng thư mục gốc** với các file kia (không đặt trong thư mục con).
- File test đặt trong thư mục con `tests/`.

---

## 3. Nội dung liên quan lấy ở đâu

Để làm được việc này, bạn **cần xin từ nhóm các file sau** (chưa có sẵn trong tay bạn — phải lấy từ Người 1/Người 2):

| File | Vai trò | Bạn dùng để làm gì |
|---|---|---|
| `base_models.py` | Định nghĩa `Grader`, `Exam`, `Question`, `StudentAnswer`, `ExamResult` | Biết chính xác cấu trúc dữ liệu mình sẽ thao tác — đây là "hợp đồng" bắt buộc phải bám theo |
| `data_repository.py` | Truy vấn câu hỏi thật | Dùng khi viết test, KHÔNG bắt buộc dùng trong `grade()` (xem mục 4) |
| `exam_generator.py` | Tạo ra `Exam` thật | Không bắt buộc — chỉ cần khi bạn muốn demo/test bằng đề thi thật thay vì tự dựng `Exam` giả bằng tay |

Bạn **không nhất thiết cần `exam_generator.py`** để viết `grader.py`, vì hàm `grade()` chỉ nhận vào 1 object `Exam` đã có sẵn (ai đưa vào cũng được, không quan tâm nó được tạo ra như thế nào) — nhưng có nó sẽ giúp bạn test bằng dữ liệu thật, gần với thực tế hơn.

Ngoài ra, thư mục `data/` (do Người 1 tạo sẵn) chứa **dữ liệu mẫu thật** (`data/subjects_topics.json`, `data/questions.json`) — dùng khi cần test với dữ liệu thật.

**Nếu bạn đưa việc này cho AI làm:** đính kèm tối thiểu `base_models.py`. Nên đính kèm thêm `data_repository.py` và `exam_generator.py` nếu muốn AI viết được demo/test sát thực tế.

---

## 4. Sử dụng dữ liệu liên quan như thế nào

### 4.1 Cấu trúc dữ liệu bạn sẽ thao tác (từ `base_models.py`)

```python
Exam(id, subject_id, title, seed, question_ids: list[str], shuffled_options: dict, created_at)
Question(id, topic_id, content, difficulty, options: list[Option], created_at)
Option(id, content, is_correct)
StudentAnswer(question_id: str, selected_option_ids: list[str])
ExamResult(id, exam_id, student_name, answers: list[StudentAnswer], score: float,
           topic_stats: dict, created_at)
```

⚠️ **Lưu ý bắt buộc:**
- Mỗi `Question` luôn có **đúng 4 phương án**, và **đúng 1 đáp án đúng** (Người 1 đã ép cứng ở `Question.is_valid()`). Bạn có thể yên tâm dùng `question.correct_option_ids()` — hàm này luôn trả về list có **đúng 1 phần tử**.
- `StudentAnswer.selected_option_ids` là **list** (không phải 1 giá trị đơn) — dù hệ thống chỉ single choice, việc này vẫn giữ dạng list cho nhất quán với thiết kế chung. Học sinh chọn đúng 1 phương án thì list có 1 phần tử; nếu học sinh bỏ trống câu đó thì đơn giản là **không có `StudentAnswer` nào cho `question_id` đó** trong danh sách `answers` truyền vào — không phải truyền `selected_option_ids=[]`.

### 4.2 Hàm bạn cần implement (chữ ký đã khai báo sẵn trong `base_models.py`)

```python
class Grader(ABC):
    def grade(self, exam: Exam, questions: list[Question],
              answers: list[StudentAnswer]) -> ExamResult: ...

    def topic_statistics(self, result: ExamResult) -> dict:
        """Trả về dict {topic_id: {'correct': int, 'total': int, 'percent': float}}"""
        ...
```

`grade()` nhận vào:
- `exam` — đề thi đã tạo (có `question_ids` là danh sách id câu hỏi theo đúng thứ tự trong đề)
- `questions` — danh sách đầy đủ `Question` tương ứng (bạn tự lấy qua `repo.get_question(qid)` cho từng `qid` trong `exam.question_ids`, rồi truyền vào — `grade()` không tự gọi `repo`)
- `answers` — danh sách `StudentAnswer` học sinh đã chọn

⚠️ **Vấn đề bạn cần xử lý:** chữ ký gốc `grade(exam, questions, answers)` **không có tham số `student_name`**, nhưng `ExamResult` bắt buộc phải có `student_name`. Cách xử lý ĐÃ CHỐT cho nhóm (làm đúng theo cách này, không tự đổi):

- Thêm `student_name: str = ""` làm tham số **có giá trị mặc định** vào cuối hàm `grade()`. Cách này không phá vỡ hợp đồng gốc — ai gọi `grade(exam, questions, answers)` kiểu cũ (3 tham số) vẫn chạy bình thường, chỉ là `student_name` sẽ rỗng nếu không truyền vào. Người 4 (GUI) khi gọi hàm này **sẽ luôn truyền `student_name`** vào (vì GUI có sẵn tên học sinh từ màn hình làm bài), nên trong thực tế trường hợp rỗng gần như không xảy ra.

### 4.3 Dữ liệu mẫu để tự dựng test

Ví dụ luồng dữ liệu bạn sẽ cần chuẩn bị khi viết test (không phải code hoàn chỉnh, chỉ minh hoạ luồng):

```python
from data_repository import JsonDataRepository
from exam_generator import RandomExamGenerator
from base_models import ExamMatrixItem, DifficultyLevel, StudentAnswer

repo = JsonDataRepository("data/subjects_topics.json", "data/questions.json")
generator = RandomExamGenerator(repo)
topics = repo.list_topics()

# Tạo 1 đề nhỏ để test nhanh
matrix = [ExamMatrixItem(topics[0].id, DifficultyLevel.DE, 4)]
exam = generator.generate_exam(topics[0].subject_id, "Đề demo", matrix, seed=7)

# Lấy đầy đủ Question tương ứng — grade() cần bạn truyền list Question này vào
questions = [repo.get_question(qid) for qid in exam.question_ids]

# Giả lập 1 câu trả lời đúng
first_question = questions[0]
correct_id = first_question.correct_option_ids()[0]
answers = [StudentAnswer(question_id=first_question.id, selected_option_ids=[correct_id])]
```

---

## 5. Trình bày để AI khác hoàn thành hiệu quả (và code chạy được ngay)

Nếu bạn không tự code mà nhờ AI, làm theo đúng quy trình sau:

### Bước 1 — Đính kèm vào cuộc trò chuyện với AI
1. Nguyên văn file `base_models.py` (bắt buộc)
2. Nguyên văn file `data_repository.py` (khuyến nghị, để AI viết test sát thực tế)
3. Nguyên văn file `exam_generator.py` (khuyến nghị, cùng lý do trên)
4. Toàn bộ tài liệu này (`README_NGUOI_3.md`)

### Bước 2 — Dùng prompt mẫu sau (copy nguyên văn, sửa lại nếu cần)

```
Tôi đính kèm base_models.py, data_repository.py, exam_generator.py và
README_NGUOI_3.md. Hãy đọc kỹ các file .py trước, CHỈ dùng đúng các
class/hàm đã có sẵn — không tự đổi tên, không tự định nghĩa lại bất kỳ
class nào đã có.

Nhiệm vụ: viết MỚI file grader.py theo ĐÚNG spec trong README_NGUOI_3.md
(mục 6 và 7, hiện CHƯA có code, bạn phải tự viết từ đầu) — implement
1 class TÊN CHÍNH XÁC LÀ "ExamResultGrader" (subclass đúng theo
base_models.py) với 2 hàm grade() và topic_statistics(), giữ đúng chữ
ký hàm. BẮT BUỘC đặt đúng tên class này - Người 4 (GUI) sẽ import
đúng tên "ExamResultGrader" từ file grader.py của bạn, đặt tên khác
sẽ làm GUI báo lỗi import. Với tham số student_name còn
thiếu (mục 4.2), làm đúng theo cách đã chốt sẵn trong README (thêm tham
số có giá trị mặc định), không tự nghĩ cách khác.

YÊU CẦU VỀ PHONG CÁCH CODE (xem chi tiết mục 1.4 của README) - RẤT QUAN
TRỌNG, ưu tiên ngang với việc code chạy đúng:
- Ưu tiên dễ hiểu hơn ngắn gọn, chấp nhận code dài hơn nếu đổi lại dễ đọc.
- Dùng vòng lặp for tường minh, KHÔNG dùng list/dict comprehension phức
  tạp, không dùng các mẹo Python cô đọng khó đọc.
- Đặt tên biến rõ nghĩa, có comment ở chỗ logic không hiển nhiên.
- Tách hàm nhỏ nếu 1 hàm đang làm nhiều việc.
- Code này sẽ được người mới học lập trình đọc và giáo viên chấm - viết
  như đang giải thích cho người khác hiểu, không viết để khoe kỹ thuật.

Sau khi viết xong, hãy TỰ CHẠY THỬ code (không chỉ đưa code):
1. Viết phần demo trong grader.py (if __name__ == "__main__":), chạy thử,
   đảm bảo không lỗi, điểm số tính ra hợp lý.
2. Viết và chạy tests/test_grader.py với toàn bộ test case ở mục 8 của
   README, đảm bảo PASS hết.
3. Thử với 1 trường hợp học sinh bỏ trống 1 câu (không có StudentAnswer
   cho câu đó) - xác nhận câu đó bị tính SAI chứ không bị bỏ qua khỏi
   thống kê.
Chỉ báo hoàn thành sau khi cả 3 bước trên chạy sạch không lỗi.
```

### Bước 3 — Sau khi nhận code, tự kiểm tra lại bằng checklist ở mục 9

---

## 6. Thiết kế chi tiết — `grade()`

### 6.1 Tên class và chữ ký hàm

⚠️ **Tên class BẮT BUỘC là `ExamResultGrader`** (không đặt tên khác) — đây là "hợp đồng" với Người 4, GUI sẽ `import` đúng tên này từ `grader.py`.

```python
class ExamResultGrader(Grader):

    def grade(self, exam: Exam, questions: list[Question],
              answers: list[StudentAnswer], student_name: str = "") -> ExamResult:
```

### 6.2 Thuật toán — mô tả từng bước (đây là SPEC, bạn tự viết code Python theo đúng logic này)

```
BƯỚC 1: Dựng 2 bảng tra cứu nhanh (tránh vòng lặp lồng nhau O(n²))
    - question_map: tra cứu Question theo question_id
    - answer_map: tra cứu selected_option_ids theo question_id

BƯỚC 2: Duyệt qua TỪNG câu hỏi trong đề (theo đúng thứ tự exam.question_ids)
    Với mỗi câu hỏi:
    - Lấy question tương ứng từ question_map
    - Lấy selected_ids học sinh đã chọn từ answer_map — nếu KHÔNG có
      (học sinh bỏ trống), coi selected_ids là danh sách rỗng
    - Lấy correct_ids = question.correct_option_ids() (luôn có đúng 1 phần tử)
    - Xác định is_correct: ĐÚNG khi và chỉ khi học sinh chọn ĐÚNG 1 phương án
      VÀ phương án đó trùng với correct_ids[0]
    - Cộng dồn is_correct vào tổng số câu đúng
    - Cộng dồn thống kê theo topic_id của câu này: tăng "tổng số câu" của
      chủ đề đó lên 1; nếu đúng thì tăng thêm "số câu đúng" của chủ đề đó lên 1

BƯỚC 3: Tính điểm tổng (thang điểm 10)
    score = (số câu đúng / tổng số câu trong đề) * 10, làm tròn hợp lý
    Xử lý trường hợp tổng số câu = 0 (đề rỗng) để tránh lỗi chia cho 0

BƯỚC 4: Tạo và trả về ExamResult
    - Tạo ExamResult mới với exam.id và student_name
    - Gán answers, score, và topic_stats (dạng {topic_id: (số đúng, tổng số)}
      đúng theo comment sẵn có trong base_models.py) vào ExamResult
    - Trả về ExamResult
```

### 6.3 Quy tắc chấm điểm cần nhớ
- **Bỏ trống câu hỏi = tính SAI**, không phải bỏ qua không tính vào thống kê. Câu đó vẫn cộng vào "tổng" của chủ đề, chỉ là không cộng vào "đúng".
- Vì hệ thống chỉ single choice, học sinh chọn **nhiều hơn 1** phương án cho 1 câu (nếu GUI lỡ cho phép) cũng phải tính là **SAI** — điều kiện "chọn đúng 1 phương án" ở Bước 2 sẽ tự động xử lý đúng trường hợp này nếu bạn code đúng logic.
- Thang điểm dùng **thang 10** (không phải phần trăm) — nếu nhóm muốn đổi thang điểm khác (ví dụ thang 100), chỉ cần đổi công thức ở Bước 3, không ảnh hưởng gì phần còn lại.

---

## 7. Thiết kế chi tiết — `topic_statistics()`

### 7.1 Mục đích
`result.topic_stats` (từ `grade()`) đang lưu ở dạng gọn `{topic_id: (đúng, tổng)}` — hàm này **định dạng lại** cho dễ dùng hơn phía GUI (Người 4 vẽ Canvas biểu đồ), tính thêm cột phần trăm.

### 7.2 Thuật toán — mô tả từng bước

```
Với mỗi (topic_id, (correct, total)) trong result.topic_stats:
    - Tính percent = (correct / total) * 100, làm tròn hợp lý
    - Xử lý trường hợp total = 0 để tránh lỗi chia cho 0
    - Gom vào dict kết quả: {topic_id: {"correct": ..., "total": ..., "percent": ...}}

Trả về dict kết quả.
```

Đây chỉ là **định dạng lại dữ liệu**, không tính toán lại từ đầu (không duyệt lại `answers`) — vì `grade()` đã tính sẵn số liệu thô rồi.

---

## 8. Test bắt buộc phải viết (`tests/test_grader.py`)

Dùng `unittest`. Trong `setUp`, tự tạo sẵn 1 subject, 2 chủ đề (A, B), mỗi chủ đề 2 câu hỏi (gợi ý: đặt đáp án đúng luôn là phương án đầu tiên để dễ kiểm soát khi viết test), và **tự dựng 1 object `Exam` bằng tay** (gán `exam.question_ids` trực tiếp) — không bắt buộc phải gọi qua `ExamGenerator` thật.

| # | Test case | Kiểm tra gì |
|---|---|---|
| 1 | `test_grade_all_correct_gives_score_10` | Học sinh làm đúng hết → điểm = 10.0 |
| 2 | `test_grade_all_wrong_gives_score_0` | Học sinh làm sai hết → điểm = 0.0 |
| 3 | `test_grade_half_correct_gives_score_5` | Đúng 2/4 câu → điểm = 5.0 |
| 4 | `test_grade_skipped_question_counts_as_wrong` | Bỏ trống 1 câu (không có trong `answers`) vẫn tính SAI, không bị loại khỏi thống kê — **test quan trọng, dễ code sai nhất** |
| 5 | `test_grade_stores_student_name` | `result.student_name` lưu đúng tên truyền vào |
| 6 | `test_grade_works_without_student_name_default` | Gọi `grade(exam, questions, answers)` kiểu cũ (không truyền `student_name`) vẫn chạy không lỗi — xác nhận giữ tương thích interface gốc |
| 7 | `test_topic_statistics_structure_and_values` | Với dữ liệu 2 chủ đề, mỗi chủ đề đúng/sai khác nhau → `topic_statistics()` trả đúng cấu trúc `{'correct', 'total', 'percent'}` với số liệu chính xác |
| 8 | `test_topic_statistics_percent_rounded` | Trường hợp chia không tròn số (ví dụ 1/3) → `percent` vẫn ra số hợp lý, không lỗi chia hoặc số thập phân dài vô tận |

---

## 9. Checklist nghiệm thu trước khi nộp/báo cáo nhóm

- [ ] `python grader.py` chạy demo không lỗi, in ra điểm số và thống kê hợp lý
- [ ] `python -m unittest tests.test_grader -v` toàn bộ PASS
- [ ] Test #4 (bỏ trống câu hỏi) chắc chắn phải pass — đây là lỗi phổ biến nhất khi chấm trắc nghiệm (nhầm giữa "không trả lời" và "bỏ qua không tính")
- [ ] Đã xử lý trường hợp `total_count = 0` (đề rỗng) không bị lỗi chia cho 0
- [ ] Không tự ý gọi `repo` bên trong `grade()`/`topic_statistics()` — 2 hàm này chỉ làm việc với dữ liệu được truyền vào qua tham số, không tự đi lấy dữ liệu
- [ ] Code không dùng list/dict comprehension phức tạp hay mẹo Python cô đọng — ưu tiên vòng lặp `for` rõ ràng, biến đặt tên dễ hiểu, có comment ở chỗ logic không hiển nhiên (đúng tinh thần mục 1.4)
- [ ] Đọc thử lại `grader.py` như thể bạn chưa từng viết nó — nếu có đoạn phải đọc 2-3 lần mới hiểu, nên viết lại đơn giản hơn

---

## 10. Bàn giao tiếp cho Người 4

- **Người 4 (GUI)** sẽ:
  - Thu thập câu trả lời của học sinh qua giao diện làm bài → dựng `list[StudentAnswer]`
  - Gọi `grader.grade(exam, questions, answers, student_name=...)` → nhận về `ExamResult`
  - Gọi `grader.topic_statistics(result)` → dùng dict trả về để vẽ Canvas biểu đồ (mỗi chủ đề 1 cột/1 phần, thể hiện `percent`)
  - Hiển thị `result.score` làm điểm tổng

**Chữ ký hàm ở mục 6.1 và 7.2 là "hợp đồng" cuối cùng** — nếu cần đổi (ví dụ đổi thang điểm, đổi cấu trúc `topic_statistics()` trả về), phải báo Người 4 trước, vì GUI sẽ code trực tiếp dựa trên cấu trúc dict này để vẽ biểu đồ.
