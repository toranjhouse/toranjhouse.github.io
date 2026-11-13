/* ارسی — تعامل‌های صفحه */
(function () {
  "use strict";
  const $ = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* --- سربرگ: پس‌زمینه پس از اسکرول --- */
  const head = $(".site-head");
  const onScroll = () => head.classList.toggle("is-scrolled", scrollY > 24);
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* --- منوی موبایل --- */
  const burger = $("#burger");
  const nav = $("#nav");
  const closeNav = () => {
    nav.classList.remove("is-open");
    burger.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
  };
  burger.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    burger.setAttribute("aria-expanded", String(open));
    document.body.style.overflow = open ? "hidden" : "";
  });
  $$("#nav a").forEach((a) => a.addEventListener("click", closeNav));
  addEventListener("keydown", (e) => { if (e.key === "Escape") closeNav(); });

  /* --- لینک فعال در ناوبری --- */
  const secs = $$("main section[id]");
  const navLinks = $$("#nav a");
  const hereIO = new IntersectionObserver((es) => {
    es.forEach((en) => {
      if (!en.isIntersecting) return;
      navLinks.forEach((a) => a.classList.toggle("is-here", a.getAttribute("href") === "#" + en.target.id));
    });
  }, { rootMargin: "-45% 0px -50% 0px" });
  secs.forEach((s) => hereIO.observe(s));

  /* --- ظهور تدریجی با کمی پله --- */
  const revealIO = new IntersectionObserver((es) => {
    es.forEach((en) => {
      if (!en.isIntersecting) return;
      const el = en.target;
      const sibs = $$(".reveal", el.parentElement).filter((n) => !n.classList.contains("in"));
      const i = Math.max(0, sibs.indexOf(el));
      el.style.transitionDelay = reduced ? "0s" : Math.min(i, 4) * 90 + "ms";
      el.classList.add("in");
      revealIO.unobserve(el);
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
  $$(".reveal").forEach((el) => revealIO.observe(el));

  /* --- پالایش منو --- */
  const tabs = $$(".tab");
  const dishes = $$("#menuGrid .dish");
  tabs.forEach((tab) => tab.addEventListener("click", () => {
    tabs.forEach((t) => { t.classList.toggle("is-on", t === tab); t.setAttribute("aria-pressed", String(t === tab)); });
    const cat = tab.dataset.cat;
    dishes.forEach((d) => {
      const show = cat === "all" || d.dataset.cat === cat;
      d.classList.toggle("is-hidden", !show);
      if (show && !reduced) {
        d.style.animation = "none";
        void d.offsetWidth;
        d.style.animation = "dishIn .5s var(--ease) both";
      }
    });
  }));
  const st = document.createElement("style");
  st.textContent = "@keyframes dishIn{from{opacity:0;transform:translateY(18px) scale(.98)}to{opacity:1;transform:none}}";
  document.head.appendChild(st);

  /* --- دکمهٔ روز/شب هیرو: یک عکس، گذار آرامِ نور --- */
  const hero = $("#hero");
  const dn = $("#daynight");
  const syncDn = () => {
    const on = hero.classList.contains("is-night");
    dn.setAttribute("aria-pressed", String(on));
    dn.querySelector(".dn-label").textContent = on ? "روز" : "شب";
    dn.setAttribute("aria-label", on
      ? "حالت روز: نور حیاط آرام روشن می‌شود"
      : "حالت شب: همان حیاط آرام به سمت شب می‌رود");
  };
  const setNight = (on) => {
    hero.classList.toggle("is-night", on);
    syncDn();
    try { localStorage.setItem("orsi-night", on ? "1" : "0"); } catch (e) {}
  };
  dn.addEventListener("click", () => setNight(!hero.classList.contains("is-night")));
  hero.classList.toggle("is-night", document.body.classList.contains("is-night"));
  syncDn();

  /* --- فرم رزرو (نمونهٔ نمایشی) --- */
  const form = $("#resForm");
  const note = $("#formNote");
  const dateIn = form.querySelector('input[name="date"]');
  dateIn.min = new Date().toISOString().slice(0, 10);
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const name = form.elements.namedItem("name").value.trim();
    const phone = form.elements.namedItem("phone").value.replace(/[\s-]/g, "");
    const okPhone = /^(?:\+98|0)?9\d{9}$/.test(phone);
    if (!name) return fail("لطفاً نام خود را بنویسید.");
    if (!okPhone) return fail("شمارهٔ تماس معتبر نیست؛ نمونه: ۰۹۱۲۳۴۵۶۷۸۹");
    if (!dateIn.value) return fail("تاریخ رفتن به خانهٔ ارسی را انتخاب کنید.");
    note.className = "form-note ok";
    note.textContent = "سپاس " + name + " عزیز! درخواست رزرو شما ثبت شد؛ میزبانِ خانه به‌زودی با شما تماس می‌گیرد. (این نسخه نمایشی است و درخواستی ارسال نمی‌شود.)";
    form.reset();
    function fail(msg) { note.className = "form-note err"; note.textContent = msg; return false; }
  });

  /* --- دکمهٔ بازگشت به سرصفحه (مدالیون شمسه) --- */
  const toTop = $("#toTop");
  if (toTop) {
    const tick = () => toTop.classList.toggle("show", window.scrollY > 520);
    addEventListener("scroll", tick, { passive: true });
    tick();
    toTop.addEventListener("click", () =>
      scrollTo({ top: 0, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }));
  }
})();
