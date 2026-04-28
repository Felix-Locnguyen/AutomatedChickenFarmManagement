### **Prompt: Thiết kế Floating Bottom Navigation Bar (FAB Style)**

**Role:** Expert Frontend Developer (UI/UX specialist).

**Context:** Tôi đang xây dựng một ứng dụng web/mobile web. Tôi cần thay thế thanh "Fixed Bottom Navigation" truyền thống bằng một thanh điều hướng dạng **Floating Action Button (FAB) Navigation**.

**Tech Stack:** 
- HTML5, CSS3 (ưu tiên Flexbox/Grid).
- FontAwesome 5/6 cho các Icon.
- Đảm bảo tính Responsive (chủ yếu cho Mobile).

**Yêu cầu thiết kế (UI):**
1. **Cấu trúc Floating:** Thanh điều hướng không dính sát đáy màn hình mà "nổi" lên trên với `border-radius` bo tròn mạnh (khoảng 30-50px) và có đổ bóng (`box-shadow`) sâu để tạo hiệu ứng lớp (layer).
2. **Nút Home (Center):** 
   - Nút Home nằm ở vị trí chính giữa thanh nav.
   - Được bao quanh bởi một hình tròn hoàn hảo, có màu nền nổi bật (ví dụ: Primary color).
   - Khi ấn vào nút Home, phải có hiệu ứng **"Press Effect"** (như nút vật lý bị lún xuống hoặc hiệu ứng Ripple/Scale nhẹ).
3. **Trạng thái Active (Các ô khác):**
   - Thay vì tô màu nền của ô (background highlight), hãy chuyển sang đổi màu trực tiếp của **Icon và Nhãn (Label)** sang màu Brand của hệ thống.
   - Các icon không được chọn sẽ có màu xám nhạt/trung tính.

**Yêu cầu kỹ thuật (Code):**
- Viết mã HTML sạch, sử dụng thẻ `<nav>`.
- Viết CSS (Vanilla CSS) tập trung vào:
    - `position: fixed` kết hợp với `bottom`, `left`, `right` và `margin` để tạo hiệu ứng nổi.
    - Sử dụng `transition` mượt mà cho hiệu ứng đổi màu icon.
    - Sử dụng `@keyframes` hoặc `:active` state để xử lý hiệu ứng nhấn cho nút Home.
- Cung cấp mã Javascript cơ bản để xử lý việc chuyển đổi class `active` khi người dùng click vào các item.
