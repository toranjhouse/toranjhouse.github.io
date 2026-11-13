#!/usr/bin/env bash
# انتشار سریع: همهٔ تغییرات را کامیت و به گیت‌هاب push می‌کند؛
# GitHub Pages خودش حدود یک دقیقه بعد به‌روز می‌شود.
# کاربرد:  ./push.sh  «پیام کامیت»
set -e
cd "$(dirname "$0")"
msg="${1:-به‌روزرسانی $(date +%Y-%m-%d_%H:%M)}"
git add -A
git commit -q -m "$msg" || echo "تغییر جدیدی برای کامیت نبود؛ فقط push می‌شود."
git push origin main
echo "✔ push شد؛ Pages تا ~۱ دقیقه دیگر به‌روز است."
