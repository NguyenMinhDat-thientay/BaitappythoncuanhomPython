# TÀI LIỆU BÀN GIAO — NGƯỜI 4: Giao diện Tkinter (GUI)

> Tài liệu này dành cho **thành viên phụ trách phần "giao diện"** trong nhóm.
> Đây là bản SPEC/HƯỚNG DẪN — chưa có code sẵn, bạn (hoặc AI bạn nhờ) cần
> tự viết toàn bộ giao diện dựa theo tài liệu này. Có thể đọc trực tiếp để
> tự code, HOẶC đưa nguyên file này cho 1 AI (Claude, ChatGPT, Copilot...)
> kèm các file đính kèm bắt buộc (xem mục 3) — làm theo đúng hướng dẫn ở
> mục 5 để AI ra được code chạy đúng ngay lần đầu.

---

## 1. Giới thiệu nội dung Người 4 cần làm

### 1.1 Bối cảnh dự án

```
Người 1 (đã xong)     Người 2 (đã xong)          Người 3            Người 4 (BẠN)
Quản lý dữ liệu   →   Sinh đề từ dữ liệu     →   Chấm điểm      →   Giao diện
(CRUD câu hỏi)        (sample + seed)            (theo Exam)        (Tkinter)
```

Bạn là người **duy nhất** trong nhóm mà người dùng cuối (giáo viên/học sinh) nhìn thấy. Cả 3 phần kia là logic thuần chạy ngầm — nhiệm vụ của bạn là **lắp ráp chúng lại thành 1 ứng dụng Tkinter chạy được**, gọi đúng hàm của 3 người kia, không tự viết lại logic nghiệp vụ.

### 1.2 Các việc bắt buộc phải làm (bám sát đề bài đồ án)

| # | Việc | Bắt buộc? |
|---|---|---|
| 1 | Treeview hiển thị danh sách câu hỏi | Bắt buộc |
| 2 | Text hiển thị nội dung chi tiết 1 câu hỏi | Bắt buộc |
| 3 | Form tạo đề (chọn mức độ, cố định 20 câu, seed tự sinh) | Bắt buộc |
| 4 | Màn hình làm bài (chọn đáp án bằng chuột, điều hướng qua lại giữa các câu) | Bắt buộc (nhóm tự thống nhất thêm, đề bài không nói tên riêng nhưng cần để tạo dữ liệu cho Người 3 chấm) |
| 5 | Canvas vẽ biểu đồ kết quả theo chủ đề | Bắt buộc |
| 6 | Custom QuestionEditor (thêm/sửa câu hỏi qua giao diện) | Nâng cao |
| 7 | Xuất đề + đáp án ra file | Nâng cao |

### 1.3 Thứ bạn KHÔNG cần làm
- Không tự viết logic CRUD câu hỏi (gọi hàm của Người 1).
- Không tự viết logic chọn câu/trộn đáp án (gọi hàm của Người 2).
- Không tự viết logic chấm điểm/thống kê (gọi hàm của Người 3).
- Bạn chỉ lo: hiển thị dữ liệu, nhận thao tác người dùng, gọi đúng hàm, hiển thị kết quả trả về.

### 1.4 Yêu cầu về phong cách code — ĐỌC KỸ TRƯỚC KHI VIẾT

Đây là đồ án nhóm, code sẽ được người khác (giáo viên, thành viên khác) đọc và chấm:

- **Ưu tiên dễ hiểu hơn ngắn gọn.** Code dài hơn 1 chút nhưng rõ ràng luôn tốt hơn code ngắn nhưng khó đọc — với GUI thì điều này càng quan trọng vì đã có nhiều widget, layout, callback đan xen sẵn.
- **Dùng vòng lặp `for` tường minh**, tránh comprehension phức tạp, tránh lambda ẩn nhiều tầng trong callback nếu có thể thay bằng hàm đặt tên rõ ràng.
- **Mỗi nút bấm gọi 1 hàm xử lý riêng, đặt tên rõ chức năng** (ví dụ `xu_ly_nut_tao_de()`, `xu_ly_nut_nop_bai()`) thay vì viết lambda dài dòng ngay trong `command=`.
- **Tách phần "logic thuần" (không phụ thuộc Tkinter) ra khỏi phần "vẽ giao diện"** khi có thể — ví dụ hàm "chia đều 20 câu ra các chủ đề" nên là 1 hàm Python bình thường, nhận vào danh sách chủ đề + mức độ, trả ra `list[ExamMatrixItem]`, KHÔNG đụng gì tới Tkinter bên trong. Lý do: phần logic thuần này **test được bằng `unittest`**, còn phần vẽ giao diện thì không — tách riêng giúp nhóm kiểm thử được nhiều hơn.
- **Thêm comment ở những chỗ có logic không hiển nhiên** (vì sao lưu tạm đáp án vào dict, vì sao random seed mỗi lần làm lại...).
- Không cần tối ưu hiệu năng — ưu tiên tuyệt đối là **dễ đọc, dễ bảo trì, dễ giải thích khi bảo vệ đồ án**.

---

## 2. Các file Người 4 cần tạo

```
gui_app.py              ← cửa sổ chính: Treeview, Text, form tạo đề, màn hình làm bài, Canvas
question_editor.py      ← Custom QuestionEditor (phần nâng cao, tách riêng)
exporter.py             ← implement ExamExporter, xuất đề/đáp án ra file (phần nâng cao, tách riêng)
tests/test_exporter.py  ← test cho exporter.py (BẮT BUỘC — đây là phần duy nhất test tự động được)
```

**Vì sao tách 3 file `.py` riêng thay vì gộp 1 file khổng lồ:**
- `question_editor.py` và `exporter.py` là 2 phần "nâng cao" đề bài liệt kê riêng — tách ra giúp báo cáo dễ trình bày, dễ chấm điểm riêng từng phần.
- `exporter.py` **không phụ thuộc Tkinter** (chỉ đọc dữ liệu và ghi file) — tách riêng để **test được bằng `unittest`** như 3 người kia, không mất công dựng cửa sổ GUI mới test được.
- `gui_app.py` sẽ `import` cả `question_editor.py` và `exporter.py` để dùng.

⚠️ **Lưu ý về `gui_app.py`:** phần vẽ giao diện (Treeview, Text, Canvas, các cửa sổ...) **không viết unit test tự động được** theo cách thông thường (Tkinter cần cửa sổ hiển thị thật, tự động hóa việc "bấm nút" rất phức tạp so với quy mô đồ án). Phần này dùng **checklist kiểm thử thủ công** (mục 7.2) thay vì `unittest`.

---

## 3. Nội dung liên quan lấy ở đâu

Bạn cần xin từ nhóm các file sau (chưa có sẵn trong tay bạn):

| File | Từ ai | Vai trò | Bạn dùng để làm gì |
|---|---|---|---|
| `base_models.py` | Người 1 | Định nghĩa toàn bộ cấu trúc dữ liệu chung + interface `ExamExporter` | Biết chính xác class/field mình thao tác |
| `data_repository.py` | Người 1 | CRUD câu hỏi thật (đọc/ghi JSON) | Đổ dữ liệu vào Treeview, làm QuestionEditor |
| `exam_generator.py` | Người 2 | Tạo `Exam` (rút câu theo ma trận, trộn theo seed) | Form tạo đề gọi hàm này |
| `grader.py` | Người 3 | Chấm điểm + thống kê theo chủ đề | Màn hình làm bài gọi sau khi nộp bài |

⚠️ **Nếu `grader.py` của Người 3 CHƯA hoàn thành khi bạn bắt đầu code GUI:** không cần chờ. Tự viết 1 class giả (gọi là "stub") implement đúng interface `Grader` trong `base_models.py`, trả về dữ liệu giả cố định (ví dụ điểm số giả, thống kê giả) — đủ để bạn code và test được giao diện độc lập. Khi Người 3 xong, chỉ cần đổi lại import từ class giả sang `grader.py` thật, không phải sửa gì trong `gui_app.py` (vì bạn vẫn gọi đúng `grade()`/`topic_statistics()` như đã định nghĩa).

Ngoài ra, thư mục `data/` (do Người 1 tạo sẵn) chứa **dữ liệu mẫu thật** để chạy thử app ngay: `data/subjects_topics.json`, `data/questions.json`.

**Nếu bạn đưa việc này cho AI làm:** đính kèm tối thiểu `base_models.py`, `data_repository.py`, `exam_generator.py`. Nếu `grader.py` thật đã có thì đính kèm luôn; nếu chưa, nói AI tự viết stub như hướng dẫn trên.

---

## 4. Sử dụng dữ liệu liên quan như thế nào

### 4.1 Cấu trúc dữ liệu bạn sẽ thao tác

```python
# Từ base_models.py
Subject(id, name, description, created_at)
Topic(id, subject_id, name, created_at)
Question(id, topic_id, content, difficulty, options: list[Option], created_at)
Option(id, content, is_correct)
DifficultyLevel        # enum: DE (Dễ), KHO (Khó) — chỉ 2 giá trị
ExamMatrixItem(topic_id: str, difficulty: DifficultyLevel, num_questions: int)
Exam(id, subject_id, title, seed, question_ids: list[str], shuffled_options: dict, created_at)
StudentAnswer(question_id: str, selected_option_ids: list[str])
ExamResult(id, exam_id, student_name, answers, score: float, topic_stats: dict, created_at)
ExamExporter(ABC)      # interface bạn implement trong exporter.py
```

### 4.2 Các hàm bạn được phép gọi

```python
# Từ data_repository.py (Người 1)
repo.list_subjects() -> list[Subject]
repo.list_topics(subject_id=None) -> list[Topic]
repo.list_questions(topic_id=None, difficulty=None) -> list[Question]
repo.get_question(question_id) -> Optional[Question]
repo.add_question(question) / update_question(id, question) / delete_question(id)
repo.get_question_bank_summary() -> dict

# Từ exam_generator.py (Người 2)
generator.generate_exam(subject_id, title, matrix: list[ExamMatrixItem], seed: int) -> Exam

# Từ grader.py (Người 3)
grader.grade(exam, questions, answers, student_name="...") -> ExamResult
grader.topic_statistics(result) -> dict   # {topic_id: {'correct', 'total', 'percent'}}
```

### 4.3 Luồng dữ liệu tổng thể khi làm bài (để hiểu trước khi code)

```
1. Người dùng chọn Môn học + Mức độ (Dễ/Khó) trên form tạo đề
2. GUI lấy danh sách Chủ đề thuộc môn đó: repo.list_topics(subject_id)
3. GUI tự chia đều 20 câu ra các chủ đề đó (xem thuật toán mục 6.4)
   → tạo ra list[ExamMatrixItem]
4. GUI tự sinh 1 seed ngẫu nhiên (KHÔNG hỏi người dùng)
5. GUI gọi generator.generate_exam(subject_id, title, matrix, seed) -> exam
6. GUI lấy chi tiết từng câu hỏi trong đề:
   questions = []
   for question_id in exam.question_ids:
       questions.append(repo.get_question(question_id))
7. GUI hiển thị từng câu, dùng exam.shuffled_options[question_id] để biết
   thứ tự 4 phương án cần hiển thị cho câu đó (không dùng question.options
   trực tiếp vì đó là thứ tự CHƯA trộn)
8. Người dùng chọn đáp án, GUI lưu tạm vào 1 dict:
   {question_id: option_id_da_chon}
9. Khi nộp bài, GUI chuyển dict trên thành list[StudentAnswer]:
   answers = []
   for question_id, option_id in cau_tra_loi_tam.items():
       answers.append(StudentAnswer(question_id=question_id, selected_option_ids=[option_id]))
10. GUI gọi grader.grade(exam, questions, answers, student_name) -> result
11. GUI gọi grader.topic_statistics(result) -> dict thống kê
12. GUI vẽ Canvas biểu đồ từ dict thống kê, hiển thị result.score
```

⚠️ **Điểm dễ nhầm nhất:** ở bước 7, phương án hiển thị cho học sinh PHẢI lấy theo thứ tự `exam.shuffled_options[question_id]` (danh sách `option_id` đã trộn), rồi mới tra ngược lại nội dung từng `option_id` đó qua `question.options` — KHÔNG hiển thị `question.options` theo thứ tự gốc, vì như vậy sẽ làm mất tác dụng "trộn đáp án" mà Người 2 đã làm.

---

## 5. Trình bày để AI khác hoàn thành hiệu quả (và code chạy được ngay)

### Bước 1 — Đính kèm vào cuộc trò chuyện với AI
1. Nguyên văn `base_models.py` (bắt buộc)
2. Nguyên văn `data_repository.py` (bắt buộc)
3. Nguyên văn `exam_generator.py` (bắt buộc)
4. Nguyên văn `grader.py` nếu đã có, hoặc nói rõ để AI tự viết stub (xem mục 3)
5. Toàn bộ tài liệu này (`README_NGUOI_4.md`)

### Bước 2 — Dùng prompt mẫu sau (copy nguyên văn, sửa lại nếu cần)

```
Tôi đính kèm base_models.py, data_repository.py, exam_generator.py
(và grader.py nếu có — nếu không có, hãy tự viết 1 class stub tên
StubGrader implement đúng interface Grader trong base_models.py, trả
điểm/thống kê giả cố định) và README_NGUOI_4.md.

Hãy đọc kỹ các file .py trước, CHỈ dùng đúng các class/hàm đã có sẵn -
không tự đổi tên, không tự định nghĩa lại bất kỳ class nào đã có.

Nhiệm vụ: viết MỚI 3 file theo ĐÚNG spec trong README_NGUOI_4.md:
1. gui_app.py - cửa sổ Tkinter chính, đủ: Treeview câu hỏi, Text nội
   dung, form tạo đề (chọn mức độ, cố định 20 câu, seed tự sinh ngẫu
   nhiên), màn hình làm bài (Radiobutton chọn đáp án, có nút "Câu
   trước"/"Câu sau" giữ lại lựa chọn đã chọn khi quay lại), Canvas vẽ
   biểu đồ kết quả theo chủ đề (mục 6.1 đến 6.6).
2. question_editor.py - Custom QuestionEditor, TÊN CLASS BẮT BUỘC LÀ
   "QuestionEditor", form thêm/sửa câu hỏi qua giao diện (mục 6.7).
3. exporter.py - implement ExamExporter, TÊN CLASS BẮT BUỘC LÀ
   "TxtExamExporter", xuất đề và đáp án ra file .txt (mục 6.8), và
   tests/test_exporter.py test bằng unittest.
Đặt ĐÚNG các tên class trên, không tự đổi tên khác - mục 9 của README
đã viết sẵn các dòng import dựa theo đúng tên class này.

YÊU CẦU VỀ PHONG CÁCH CODE (xem chi tiết mục 1.4 của README) - RẤT
QUAN TRỌNG:
- Ưu tiên dễ hiểu hơn ngắn gọn, chấp nhận code dài hơn nếu đổi lại dễ đọc.
- Dùng vòng lặp for tường minh, tránh comprehension phức tạp.
- Mỗi nút bấm gọi 1 hàm xử lý riêng có tên rõ ràng, không viết lambda
  dài trong command=.
- TÁCH RIÊNG phần logic thuần (không đụng Tkinter, ví dụ hàm chia đều
  20 câu ra các chủ đề) thành hàm Python độc lập, để test được bằng
  unittest mà không cần mở cửa sổ GUI thật.
- Code sẽ được người mới học lập trình đọc và giáo viên chấm - viết
  như đang giải thích cho người khác hiểu.

Sau khi viết xong, hãy TỰ CHẠY THỬ những phần chạy thử được (không chỉ
đưa code):
1. Chạy thử `python -c "import gui_app"` - đảm bảo không lỗi cú pháp/
   import (không cần mở được cửa sổ thật nếu môi trường không có màn
   hình - miễn không lỗi khi import module).
2. Nếu tách được hàm logic thuần (ví dụ hàm chia 20 câu ra các chủ đề)
   thành hàm riêng không đụng Tkinter, hãy viết thêm 1-2 test nhỏ cho
   hàm đó và chạy thử, xác nhận chia đúng tổng = 20.
3. Viết và chạy tests/test_exporter.py, đảm bảo PASS hết - đây là
   phần BẮT BUỘC phải test được đầy đủ vì không phụ thuộc Tkinter.
4. Dùng dữ liệu mẫu thật trong thư mục data/ để thử tạo 1 đề, xác nhận
   luồng gọi hàm không lỗi (generate_exam -> lấy questions -> gọi
   grade với dữ liệu StudentAnswer giả).
Báo rõ phần nào chạy thử được, phần nào cần người có màn hình thật tự
bấm thử (đính kèm checklist kiểm thử thủ công theo mục 7.2 của README).
```

### Bước 3 — Sau khi nhận code, tự kiểm tra lại bằng checklist ở mục 8, và **tự bấm thử toàn bộ ứng dụng** theo checklist thủ công ở mục 7.2 (AI không thể tự bấm nút giúp bạn được)

---

## 6. Thiết kế chi tiết từng thành phần

### 6.1 Cấu trúc tổng thể ứng dụng

Gợi ý dùng `ttk.Notebook` (giao diện dạng tab) với các tab:
- **Tab "Ngân hàng câu hỏi"** — chứa Treeview + Text (mục 6.2, 6.3) + nút mở QuestionEditor (mục 6.7)
- **Tab "Làm bài kiểm tra"** — chứa form tạo đề (mục 6.4) + màn hình làm bài (mục 6.5)
- **Tab "Kết quả"** — chứa Canvas biểu đồ (mục 6.6) + nút xuất file (mục 6.8)

Không bắt buộc đúng 3 tab này, nhưng nên tách rõ ràng theo luồng nghiệp vụ, tránh nhồi hết vào 1 màn hình.

### 6.2 Treeview câu hỏi

- Widget: `ttk.Treeview`, các cột gợi ý: "Nội dung" (rút gọn, có thể cắt bớt ký tự nếu quá dài), "Chủ đề", "Mức độ".
- Phía trên Treeview: 2 dropdown lọc — chọn Môn học (đổ từ `repo.list_subjects()`), chọn Chủ đề (đổ từ `repo.list_topics(subject_id)` theo môn đã chọn), chọn Mức độ (Dễ/Khó/Tất cả).
- Khi thay đổi bộ lọc, gọi lại `repo.list_questions(topic_id=..., difficulty=...)` và nạp lại dữ liệu vào Treeview.
- Sự kiện `<<TreeviewSelect>>`: khi người dùng click chọn 1 dòng, lấy `question_id` tương ứng, gọi `repo.get_question(question_id)`, cập nhật khung Text (mục 6.3).

### 6.3 Text nội dung

- Widget: `tk.Text` (hoặc nhiều `Label`), đặt cạnh hoặc bên dưới Treeview.
- Hiển thị: nội dung câu hỏi đầy đủ, 4 phương án (đánh số A/B/C/D theo thứ tự lưu trong `question.options`), đánh dấu rõ phương án đúng (ví dụ tô màu chữ khác, hoặc thêm chữ "(Đáp án đúng)" phía sau).
- Đặt `state="disabled"` sau khi ghi nội dung để người dùng không gõ chỉnh sửa trực tiếp vào đây (sửa câu hỏi phải qua QuestionEditor, mục 6.7).

### 6.4 Form tạo đề (đã đơn giản hoá theo yêu cầu: cố định 20 câu, chỉ 1 mức độ)

**Các control cần có:**
- Dropdown chọn Môn học.
- Radio/dropdown chọn Mức độ: **Dễ** hoặc **Khó** (chỉ chọn 1, không cho chọn cả 2 hay để trống).
- Không có ô nhập số câu — **luôn cố định 20**, có thể hiển thị dòng chữ tĩnh "Đề gồm 20 câu" để người dùng biết, không cho sửa.
- Nút **"Bắt đầu làm bài"**.

**Thuật toán "chia đều 20 câu ra các chủ đề thuộc mức độ đã chọn"** (mô tả từng bước, bạn tự viết thành hàm Python riêng, KHÔNG đụng Tkinter trong hàm này — để test được độc lập):

```
Input: danh sách các Topic thuộc môn đã chọn, 1 DifficultyLevel đã chọn
Output: list[ExamMatrixItem], tổng num_questions cộng lại = 20

BƯỚC 1: Tính số câu cơ bản mỗi chủ đề = 20 chia nguyên cho số chủ đề
    Ví dụ 3 chủ đề: 20 // 3 = 6 (chia nguyên, không lấy phần dư)

BƯỚC 2: Tính số dư = 20 trừ đi (số câu cơ bản nhân số chủ đề)
    Ví dụ: 20 - 6*3 = 2 (còn dư 2 câu chưa phân bổ)

BƯỚC 3: Duyệt qua từng chủ đề theo thứ tự, chủ đề nào rơi vào các vị
    trí đầu tiên (số lượng đúng bằng số dư ở BƯỚC 2) thì được cộng
    thêm 1 câu so với số cơ bản, các chủ đề còn lại giữ nguyên số cơ bản
    Ví dụ 3 chủ đề, dư 2: 2 chủ đề đầu tiên = 6+1 = 7 câu mỗi chủ đề,
    chủ đề còn lại = 6 câu. Tổng: 7+7+6 = 20 (khớp)

BƯỚC 4: Với mỗi chủ đề và số câu đã tính, tạo 1 ExamMatrixItem
    (topic_id của chủ đề đó, mức độ đã chọn, số câu đã tính)
    Gom tất cả ExamMatrixItem lại thành 1 list, đây chính là kết quả trả về
```

⚠️ **Trường hợp cần xử lý:** nếu tổng số câu có sẵn trong ngân hàng (ở mức độ đã chọn, cộng dồn tất cả chủ đề) **nhỏ hơn 20**, `generate_exam()` của Người 2 sẽ tự báo lỗi `ValueError` rõ ràng — GUI cần **bắt lỗi này và hiển thị thông báo dễ hiểu** cho người dùng (ví dụ hộp thoại `messagebox.showerror`), không để chương trình crash.

**Seed tự sinh ngẫu nhiên:** dùng `random.randint(...)` (module `random` chuẩn của Python, không phải tự nghĩ thuật toán random riêng) để tự sinh 1 số nguyên làm seed mỗi lần bấm "Bắt đầu làm bài" — **không có ô nhập seed cho người dùng**.

### 6.5 Màn hình làm bài

**Các control cần có:**
- 1 khu vực hiển thị: số thứ tự câu hiện tại / tổng số câu (ví dụ "Câu 5/20"), nội dung câu hỏi, 4 `Radiobutton` cho 4 phương án.
- Biến `variable` dùng chung cho 4 `Radiobutton` của 1 câu — đây là cách Tkinter đảm bảo chỉ chọn được 1 trong 4 (đúng yêu cầu single choice).
- 2 nút **"◀ Câu trước"** và **"Câu sau ▶"** để di chuyển giữa các câu (không phải cuộn/duyệt tuần tự bắt buộc, người dùng có thể quay lại sửa đáp án bất kỳ lúc nào trước khi nộp bài).
- 1 nút **"Nộp bài"** (chỉ hiện rõ hoặc luôn có sẵn, tùy thiết kế).

**Cách lưu tạm đáp án khi di chuyển qua lại giữa các câu (quan trọng, đọc kỹ):**
- Dùng 1 `dict` Python thường (không phải widget) để lưu: `{question_id: option_id_da_chon}`.
- Mỗi khi người dùng chọn 1 `Radiobutton`, cập nhật ngay vào dict này (không đợi tới lúc bấm "Câu sau" mới lưu).
- Mỗi khi hiển thị lại 1 câu (do bấm "Câu trước"/"Câu sau"/bấm số câu), **kiểm tra trong dict xem câu đó đã có đáp án chưa**, nếu có thì set sẵn `variable` của `Radiobutton` về đúng giá trị đã lưu — để người dùng thấy lại đúng lựa chọn cũ của mình, không bị mất.
- Câu chưa trả lời thì đơn giản không có key tương ứng trong dict — khi nộp bài, những câu này sẽ không có `StudentAnswer` (đúng theo thiết kế của Người 3, xem README_NGUOI_3.md mục 4.1).

**(Tùy chọn nâng cao, không bắt buộc):** 1 lưới nhỏ 20 ô đánh số 1-20, ô nào đã có đáp án trong dict thì đổi màu nền khác, bấm vào số nào thì nhảy thẳng tới câu đó — giúp trải nghiệm giống ứng dụng thi thật.

### 6.6 Canvas biểu đồ kết quả

- Widget: `tk.Canvas`, **vẽ tay** bằng `create_rectangle()` (vẽ cột) và `create_text()` (ghi số phần trăm, tên chủ đề) — đề bài yêu cầu đúng Canvas, không dùng thư viện vẽ biểu đồ ngoài (như matplotlib).
- Dữ liệu vẽ lấy từ `grader.topic_statistics(result)` — với mỗi chủ đề, vẽ 1 cột, **chiều cao cột tỉ lệ với `percent`** (ví dụ percent=80 thì cột cao 80% chiều cao tối đa đã định trước cho Canvas).
- Ghi kèm tên chủ đề bên dưới mỗi cột, và số `percent` bên trên mỗi cột.
- Hiển thị thêm `result.score` (điểm tổng) ở đâu đó rõ ràng, ví dụ 1 `Label` phía trên Canvas.

**Thuật toán vẽ (mô tả từng bước):**
```
BƯỚC 1: Lấy dict thống kê từ grader.topic_statistics(result)
BƯỚC 2: Định trước: chiều rộng mỗi cột, khoảng cách giữa các cột,
        chiều cao tối đa của Canvas (ứng với 100%)
BƯỚC 3: Duyệt qua từng chủ đề trong dict thống kê, với mỗi chủ đề:
    - Tính chiều cao cột thực tế = (percent / 100) * chiều cao tối đa
    - Tính vị trí x của cột này (cột thứ mấy tính từ trái, nhân với
      chiều rộng + khoảng cách đã định ở BƯỚC 2)
    - Vẽ hình chữ nhật (create_rectangle) từ đáy Canvas lên đúng chiều
      cao vừa tính
    - Ghi tên chủ đề bên dưới cột (create_text)
    - Ghi số percent bên trên cột (create_text)
```

### 6.7 Custom QuestionEditor (nâng cao)

⚠️ **Tên class BẮT BUỘC là `QuestionEditor`** (đặt trong `question_editor.py`) — khớp với dòng import ở mục 9.

- Tạo 1 cửa sổ con (`tk.Toplevel`), mở khi bấm nút "Thêm câu hỏi mới" (Treeview) hoặc "Sửa" (khi đang chọn 1 dòng trong Treeview).
- Control cần có: ô nhập nội dung câu hỏi, 4 ô nhập nội dung 4 phương án, 1 nhóm `Radiobutton` chọn phương án nào là đáp án đúng (chỉ 1), dropdown chọn Chủ đề, dropdown chọn Mức độ (Dễ/Khó).
- Nếu đang SỬA (không phải thêm mới): nạp sẵn dữ liệu hiện có của câu hỏi vào các ô trên.
- Nút "Lưu": dựng lại object `Question` (dùng `Question.create(...)` nếu thêm mới, hoặc gán lại field nếu sửa) rồi gọi `repo.add_question(question)` hoặc `repo.update_question(question_id, question)`.
- **Bắt lỗi từ `is_valid()`:** hàm `add_question()`/`update_question()` của Người 1 sẽ raise `ValueError` nếu dữ liệu không hợp lệ (thiếu đáp án đúng, không đủ 4 phương án...) — bọc lệnh gọi trong `try/except ValueError as e`, hiển thị nội dung lỗi `str(e)` ra `messagebox.showerror`, KHÔNG để chương trình crash hay đóng cửa sổ đột ngột.
- Sau khi lưu thành công: đóng cửa sổ `Toplevel`, nạp lại dữ liệu Treeview để thấy câu hỏi mới/đã sửa.

### 6.8 Xuất đề + đáp án ra file (nâng cao)

⚠️ **Tên class BẮT BUỘC là `TxtExamExporter`** (đặt trong `exporter.py`) — khớp với dòng import ở mục 9.

Implement interface `ExamExporter` (đã có sẵn trong `base_models.py`):

```python
class TxtExamExporter(ExamExporter):
    def export_exam(self, exam: Exam, questions: list[Question], file_path: str) -> None: ...
    def export_answer_key(self, exam: Exam, questions: list[Question], file_path: str) -> None: ...
```

**Định dạng file đề xuất: `.txt`** (đơn giản, không cần cài thêm thư viện, đủ để nộp báo cáo):

- `export_exam()`: ghi ra file `.txt` — với mỗi câu trong `exam.question_ids` (theo đúng thứ tự), ghi nội dung câu hỏi, rồi 4 phương án theo đúng thứ tự đã trộn (`exam.shuffled_options[question_id]`), đánh số A/B/C/D — **KHÔNG được ghi kèm đáp án đúng** trong file này.
- `export_answer_key()`: ghi ra file `.txt` riêng — với mỗi câu, ghi số thứ tự câu và chữ cái (A/B/C/D) tương ứng với đáp án đúng, theo đúng thứ tự đã trộn của đề đó (phải tra đúng theo `exam.shuffled_options`, không phải thứ tự gốc trong `question.options` — nếu không đáp án sẽ bị lệch chữ cái so với đề đã xuất).
- Gắn 2 nút "Xuất đề" và "Xuất đáp án" ở Tab "Kết quả" hoặc Tab "Làm bài kiểm tra", dùng `filedialog.asksaveasfilename()` để người dùng chọn nơi lưu file.

---

## 7. Kiểm thử

### 7.1 Phần test tự động được — `tests/test_exporter.py`

Vì `exporter.py` không phụ thuộc Tkinter (chỉ nhận `Exam`, `list[Question]`, `file_path` rồi ghi file), viết test bằng `unittest` bình thường:

| # | Test case | Kiểm tra gì |
|---|---|---|
| 1 | `test_export_exam_creates_file` | Sau khi gọi `export_exam()`, file tồn tại trên đĩa |
| 2 | `test_export_exam_does_not_contain_correct_answer` | Mở file đề đã xuất, xác nhận **không** có dấu hiệu nào lộ đáp án đúng (ví dụ không có chữ đúng của phương án đúng được đánh dấu riêng) |
| 3 | `test_export_answer_key_matches_shuffled_order` | Đáp án ghi trong file đáp án khớp đúng theo thứ tự `exam.shuffled_options`, không phải thứ tự gốc |
| 4 | `test_export_all_questions_included` | File đề có đủ số câu bằng `len(exam.question_ids)`, không thiếu/thừa câu nào |

### 7.2 Checklist kiểm thử thủ công (tự bấm thử toàn bộ ứng dụng)

- [ ] Mở app, Treeview hiện đủ danh sách câu hỏi từ dữ liệu mẫu
- [ ] Lọc theo Môn/Chủ đề/Mức độ, Treeview cập nhật đúng
- [ ] Click 1 dòng trong Treeview, khung Text hiện đúng nội dung + 4 phương án, đáp án đúng được đánh dấu rõ
- [ ] Vào form tạo đề, chọn Môn + Mức độ, bấm "Bắt đầu làm bài" → vào được màn hình làm bài với đúng 20 câu
- [ ] Chọn đáp án bằng cách bấm vào nút tròn — chọn được
- [ ] Chọn đáp án bằng cách bấm vào **dòng chữ** (không bấm đúng nút tròn) — vẫn chọn được (đúng hành vi mặc định của `Radiobutton`)
- [ ] Bấm "Câu sau" nhiều lần tới câu 20 — không bị lỗi tràn/crash
- [ ] Bấm "Câu trước" quay lại 1 câu đã chọn đáp án trước đó — **đáp án cũ vẫn hiển thị đúng**, không bị mất
- [ ] Bỏ trống 1 vài câu, bấm "Nộp bài" — không bị bắt buộc phải trả lời hết mới nộp được
- [ ] Sau khi nộp, Canvas hiện biểu đồ, điểm số hiển thị đúng, cột cao thấp hợp lý theo % đúng từng chủ đề
- [ ] Làm lại 1 đề mới (bấm "Bắt đầu làm bài" lần 2, cùng Môn + Mức độ) — **thứ tự câu/đáp án khác lần trước** (do seed tự sinh ngẫu nhiên mỗi lần)
- [ ] Mở QuestionEditor, thêm 1 câu hỏi mới hợp lệ — lưu thành công, Treeview cập nhật thấy câu mới
- [ ] Mở QuestionEditor, cố tình để trống nội dung hoặc không chọn đáp án đúng — bấm Lưu phải hiện thông báo lỗi rõ ràng, KHÔNG crash app
- [ ] Xuất file đề — mở file `.txt` ra xem, không thấy đáp án đúng bị lộ
- [ ] Xuất file đáp án — đối chiếu tay 1-2 câu, đáp án ghi đúng theo thứ tự đã hiển thị lúc làm bài

---

## 8. Checklist nghiệm thu trước khi nộp/báo cáo nhóm

- [ ] `python gui_app.py` mở được ứng dụng, không lỗi ngay khi khởi động
- [ ] `python -m unittest tests.test_exporter -v` toàn bộ PASS
- [ ] Toàn bộ checklist thủ công ở mục 7.2 đã tự bấm thử và đạt
- [ ] Đã xử lý các trường hợp lỗi (ngân hàng không đủ 20 câu, QuestionEditor nhập thiếu dữ liệu...) bằng `messagebox`, không để app crash trực tiếp (đóng sập không rõ lý do)
- [ ] Code không dùng comprehension/mẹo phức tạp — ưu tiên `for` rõ ràng, tên hàm/biến dễ hiểu (đúng tinh thần mục 1.4)
- [ ] Phần logic thuần (chia 20 câu ra các chủ đề) đã tách thành hàm riêng không đụng Tkinter, và có test riêng cho hàm đó

---

## 9. Tổng kết luồng tích hợp cả 4 người (để bạn hình dung bức tranh chung khi ráp `gui_app.py`)

```python
# Phần import ở đầu gui_app.py — ráp đủ cả 4 người lại với nhau
from base_models import ExamMatrixItem, DifficultyLevel, StudentAnswer
from data_repository import JsonDataRepository        # Người 1
from exam_generator import RandomExamGenerator          # Người 2
from grader import ExamResultGrader                     # Người 3 (hoặc stub tạm nếu chưa có)
from question_editor import QuestionEditor               # Bạn tự viết
from exporter import TxtExamExporter                     # Bạn tự viết

repo = JsonDataRepository("data/subjects_topics.json", "data/questions.json")
generator = RandomExamGenerator(repo)
grader = ExamResultGrader()
```

Đây là 5 dòng đầu tiên bạn cần có trong `gui_app.py` — toàn bộ phần còn lại của ứng dụng chỉ là gọi qua lại các object `repo`, `generator`, `grader` này theo đúng luồng đã mô tả ở mục 4.3.
