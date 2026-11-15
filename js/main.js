/* ترنج — تعامل‌های صفحه */
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
    head.classList.remove("menu-open");
    document.body.style.overflow = "";
  };
  burger.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    burger.setAttribute("aria-expanded", String(open));
    head.classList.toggle("menu-open", open);
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

/* --- دکمه‌ی روز/شب هیرو: یک عکس، گذار آرامِ نور --- */
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
    document.body.classList.toggle("is-night", on);
    syncDn();
    try { localStorage.setItem("toranj-night", on ? "1" : "0"); } catch (e) {}
  };
  if (dn && hero) {
    dn.addEventListener("click", () => setNight(!hero.classList.contains("is-night")));
    let saved = null;
    try { saved = localStorage.getItem("toranj-night"); } catch (e) {}
    if (saved === "0") document.body.classList.remove("is-night");
    hero.classList.toggle("is-night", document.body.classList.contains("is-night"));
    syncDn();
  }

  /* --- فرم رزرو: تاریخ شمسی + ارسال به واتس‌اپ --- */
  const WA_NUM = "989194678237";
  const WA_HELLO = "سلام، از سایت ترنج پیام می‌دم.";
  const form = $("#resForm");
  if (form) {
    const note = $("#formNote");
    const fail = (msg) => { note.className = "form-note err"; note.textContent = msg; return false; };
    const deDig = (s) => String(s).replace(/[۰-۹]/g, (d) => "۰۱۲۳۴۵۶۷۸۹".indexOf(d));
    const faDig = (s) => String(s).replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[d]);
    const F_MDY = new Intl.DateTimeFormat("fa-IR-u-ca-persian", { day: "numeric", month: "numeric", year: "numeric" });
    const F_LONG = new Intl.DateTimeFormat("fa-IR-u-ca-persian", { day: "numeric", month: "long", year: "numeric" });
    const J_MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"];
    const toJ = (d) => {
      const p = {};
      F_MDY.formatToParts(d).forEach((x) => { p[x.type] = deDig(x.value); });
      return { jy: +p.year, jm: +p.month, jd: +p.day };
    };
    const addD = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
    const day0 = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());
    const minG = day0(new Date());
    const maxG = addD(minG, 120);
    const btn = $("#jdateBtn"), cal = $("#jcal"), hid = $("#jdateIn");
    const grid = cal.querySelector(".jcal-grid"), title = cal.querySelector(".jc-title");
    let g1 = null, curJ = null, chosenTxt = "";
    const setG1 = (d) => { const j = toJ(d); g1 = addD(day0(d), -(j.jd - 1)); curJ = j; return j; };
    setG1(new Date());
    const monthLen = () => {
      for (let L = 29; L <= 31; L++) { const j = toJ(addD(g1, L)); if (j.jm !== curJ.jm || j.jy !== curJ.jy) return L; }
      return 31;
    };
    const open = () => { cal.hidden = false; btn.setAttribute("aria-expanded", "true"); render(); };
    const close = () => { cal.hidden = true; btn.setAttribute("aria-expanded", "false"); };
    function render() {
      const len = monthLen();
      title.textContent = J_MONTHS[curJ.jm - 1] + " " + faDig(curJ.jy);
      grid.innerHTML = "";
      const off = (g1.getDay() + 1) % 7;
      for (let i = 0; i < off; i++) grid.appendChild(document.createElement("span"));
      for (let d = 1; d <= len; d++) {
        const g = addD(g1, d - 1);
        const b = document.createElement("button");
        b.type = "button"; b.textContent = faDig(d);
        if (g < minG || g > maxG) b.disabled = true;
        if (chosenTxt && F_LONG.format(g) === chosenTxt) b.classList.add("is-sel");
        if (day0(g).getTime() === minG.getTime()) b.classList.add("is-today");
        b.addEventListener("click", () => {
          chosenTxt = F_LONG.format(g);
          const j = toJ(g);
          hid.value = faDig(j.jy) + "/" + faDig(String(j.jm).padStart(2, "0")) + "/" + faDig(String(j.jd).padStart(2, "0"));
          btn.querySelector(".jd-txt").textContent = chosenTxt;
          close();
        });
        grid.appendChild(b);
      }
    }
    btn.addEventListener("click", () => (cal.hidden ? open() : close()));
    cal.querySelectorAll(".jc-nav").forEach((nv) => nv.addEventListener("click", () => {
      const anchor = Number(nv.dataset.d) < 0 ? addD(g1, -1) : addD(g1, monthLen());
      setG1(anchor); render();
    }));
    document.addEventListener("click", (ev) => {
      if (!cal.hidden && !cal.contains(ev.target) && !btn.contains(ev.target)) close();
    });

    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const name = form.elements.namedItem("name").value.trim();
      const phone = form.elements.namedItem("phone").value.replace(/[\s-]/g, "");
      const okPhone = /^(?:\+98|0)?9\d{9}$/.test(phone);
      if (!name) return fail("لطفاً نام خود را بنویسید.");
      if (!okPhone) return fail("شماره‌ی تماس معتبر نیست؛ نمونه: ۰۹۲۳۴۵۶۷۸۹");
      if (!hid.value) return fail("تاریخ رفتن به خانه‌ی ترنج را از گاه‌شماری شمسی انتخاب کنید.");
      const guests = form.elements.namedItem("guests").value;
      const space = form.elements.namedItem("space").value;
      const time = form.elements.namedItem("time").value;
      const noteTx = form.elements.namedItem("note").value.trim();
      const msg = WA_HELLO + "\nدرخواست رزرو میز از سایت ترنج:" +
        "\nنام: " + name +
        "\nشماره‌ی تماس: " + phone +
        "\nتاریخ: " + chosenTxt +
        "\nساعت: " + time +
        "\nتعداد مهمان: " + guests +
        "\nفضای نشستن: " + space +
        (noteTx ? "\nتوضیح: " + noteTx : "");
      const url = "https://wa.me/" + WA_NUM + "?text=" + encodeURIComponent(msg);
      window.open(url, "_blank", "noopener");
      note.className = "form-note ok";
      note.textContent = "";
      note.appendChild(document.createTextNode("سپاس " + name + " عزیز! فرم رزرو شما در واتس‌اپ باز شد؛ فقط دکمه‌ی ارسال را بزنید. "));
      const a = document.createElement("a");
      a.href = url; a.target = "_blank"; a.rel = "noopener"; a.textContent = "بازکردن دوباره‌ی واتس‌اپ";
      note.appendChild(a);
      form.reset();
      chosenTxt = ""; hid.value = "";
      btn.querySelector(".jd-txt").textContent = "انتخاب تاریخ";
    });
  }

  /* --- دکمه‌ی بازگشت به سرصفحه (مدالیون شمسه) --- */
  const toTop = $("#toTop");
  if (toTop) {
    const tick = () => toTop.classList.toggle("show", window.scrollY > 520);
    addEventListener("scroll", tick, { passive: true });
    tick();
    toTop.addEventListener("click", () =>
      scrollTo({ top: 0, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }));
  }
})();
