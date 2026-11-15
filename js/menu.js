/* برگهٔ منو: مسیریابی با هش و جابه‌جایی دسته‌ها بدون بارگذاری دوباره */
(function () {
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => [...document.querySelectorAll(s)];
  const tabs = $$(".m-tabs .tab");
  const views = $$(".view");
  const key = () => (location.hash || "#kabab").slice(1);
  const show = (k) => {
    if (!$("#view-" + k)) k = "kabab";
    views.forEach((v) => v.classList.toggle("is-on", v.id === "view-" + k));
    tabs.forEach((t) => {
      const on = t.dataset.view === k;
      t.classList.toggle("is-on", on);
      t.setAttribute("aria-pressed", String(on));
    });
  };
  tabs.forEach((t) => t.addEventListener("click", () => { location.hash = t.dataset.view; }));
  addEventListener("hashchange", () => { show(key()); scrollTo({ top: 0, behavior: "auto" }); });
  show(key());
})();
