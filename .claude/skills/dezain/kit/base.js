/* dezain kit / base.js — 依存なし（jQuery・GSAP不要）。</body> の直前に置く */
(function () {
  document.documentElement.classList.add('js');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  // スクロールで出る: 画面の下30%に入ったら一度だけ .is-in（見本の start 0.7 と同じ）
  var targets = document.querySelectorAll('.fx-up, .fx-left, .fx-right, .fx-fade, .fx-mask');
  if (reduce || !('IntersectionObserver' in window)) {
    targets.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -30% 0px' });
    targets.forEach(function (el) { io.observe(el); });
  }

  // FVの登場: .fv-in を書いた順に 0.8秒ずつずらす
  document.querySelectorAll('.fv-in').forEach(function (el, i) {
    setTimeout(function () { el.classList.add('is-in'); }, reduce ? 0 : 200 + i * 800);
  });

  // 横に流れる帯: 中身を複製して切れ目なく流す
  document.querySelectorAll('.marquee__track').forEach(function (t) {
    Array.prototype.slice.call(t.children).forEach(function (c) {
      var d = c.cloneNode(true); d.setAttribute('aria-hidden', 'true'); t.appendChild(d);
    });
  });

  // 続きを読む
  document.querySelectorAll('.fold').forEach(function (f) {
    var body = f.querySelector('.fold__body'), btn = f.querySelector('.fold__btn');
    if (!body || !btn) return;
    f.classList.add('is-closed');
    btn.addEventListener('click', function () {
      var h = body.scrollHeight; f.classList.remove('is-closed');
      body.style.height = '80px'; requestAnimationFrame(function () { body.style.height = h + 'px'; });
      body.addEventListener('transitionend', function () { body.style.height = 'auto'; }, { once: true });
    });
  });

  // 固定の申込ボタン: 1500px スクロールしたら出す
  var follow = document.querySelector('.follow');
  if (follow) {
    var onScroll = function () { follow.classList.toggle('is-on', window.scrollY > 1500); };
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }

  // ページ内リンクはなめらかに（上に40px余白）
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      var id = a.getAttribute('href'); if (id.length < 2) return;
      var t = document.querySelector(id); if (!t) return;
      ev.preventDefault();
      window.scrollTo({ top: t.getBoundingClientRect().top + window.scrollY - 40, behavior: reduce ? 'auto' : 'smooth' });
    });
  });
})();
