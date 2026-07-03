/**
 * insight.js — 共享交互逻辑
 * 包含：主题切换 · Mermaid 初始化 · TOC 自动生成与 scroll spy · 移动端 drawer
 *
 * 使用方式（每个 HTML 文件）：
 *   <script src="..(_relative path).._assets/insight.js"></script>
 * 或直接内联（复制到 <script> 块中）。
 *
 * 约定：
 *   - localStorage key: site-theme
 *   - <html data-theme="dark|light">
 *   - TOC 目标：article h2, article h3（有 id 属性）
 *   - #toc / #drawerToc：桌面/移动端 TOC 容器
 *   - #themeBtn：主题切换按钮
 *   - #tocBtn / #drawer / #drawerOverlay：移动端 drawer
 */
(function () {
  /* ── Theme toggle ──────────────────────────────── */
  const themeBtn = document.getElementById('themeBtn');
  const savedTheme = localStorage.getItem('site-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', initialTheme);
  if (themeBtn) themeBtn.textContent = initialTheme === 'dark' ? '☼' : '◐';

  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const cur = document.documentElement.getAttribute('data-theme') || 'light';
      const next = cur === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('site-theme', next);
      themeBtn.textContent = next === 'dark' ? '☼' : '◐';
      if (typeof initMermaid === 'function') initMermaid(next);
      else window.__mermaidTheme = next;
    });
  }

  /* ── Mermaid init ──────────────────────────────── */
  window.initMermaid = function initMermaid(theme) {
    if (typeof mermaid === 'undefined') return;
    const dark = theme === 'dark';
    mermaid.initialize({
      startOnLoad: false,
      theme: dark ? 'dark' : 'default',
      themeVariables: dark ? {
        primaryColor: '#2a2440',
        primaryTextColor: '#ececf0',
        primaryBorderColor: '#a78bfa',
        lineColor: '#888892',
        secondaryColor: '#1f1f26',
        tertiaryColor: '#15151a',
        background: '#1f1f26',
      } : {
        primaryColor: '#ede9fe',
        primaryTextColor: '#1c1c1e',
        primaryBorderColor: '#4338ca',
        lineColor: '#888',
        background: '#ffffff',
      },
      flowchart: { curve: 'basis', useMaxWidth: true },
      timeline: { useMaxWidth: true },
    });
    document.querySelectorAll('.mermaid').forEach((el) => {
      if (el.dataset.original) {
        el.innerHTML = el.dataset.original;
      } else {
        el.dataset.original = el.innerHTML;
      }
      el.removeAttribute('data-processed');
    });
    mermaid.run({ nodes: document.querySelectorAll('.mermaid') });
  };

  /* Run mermaid if already loaded (inline script) */
  if (typeof mermaid !== 'undefined') {
    window.initMermaid(initialTheme);
  } else {
    /* If mermaid loads asynchronously via CDN, init after load */
    document.addEventListener('DOMContentLoaded', function () {
      if (typeof mermaid !== 'undefined') window.initMermaid(initialTheme);
    });
  }

  /* ── TOC build + scroll spy ────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    const toc = document.getElementById('toc');
    const drawerToc = document.getElementById('drawerToc');
    const headings = document.querySelectorAll('article h2[id], article h3[id]');

    if ((toc || drawerToc) && headings.length) {
      headings.forEach(h => {
        const li = document.createElement('li');
        if (h.tagName === 'H3') li.classList.add('sub');
        const a = document.createElement('a');
        a.href = '#' + h.id;
        // 标题文本：克隆后移除序号与锚点，避免 textContent 把「一」和标题粘在一起
        const clone = h.cloneNode(true);
        clone.querySelectorAll('.sec-num, .anchor').forEach(function (el) { el.remove(); });
        const titleText = clone.textContent.replace(/#$/, '').trim();
        const numEl = h.querySelector('.sec-num');
        if (numEl && numEl.textContent.trim()) {
          const ns = document.createElement('span');
          ns.className = 'toc-sec-num';
          ns.textContent = numEl.textContent.trim();
          a.appendChild(ns);
          a.appendChild(document.createTextNode(titleText));
        } else {
          a.textContent = titleText;
        }
        li.appendChild(a);
        if (toc) toc.appendChild(li.cloneNode(true));
        if (drawerToc) drawerToc.appendChild(li);
      });

      const allTocLinks = document.querySelectorAll('#toc a, #drawerToc a');
      // 激活带顶部对齐 CSS 中 --anchor-offset（减一点点留 buffer），
      // 这样点击锚点跳到对应位置后，正好那个标题被高亮，而不是下一个。
      const anchorOffset =
        parseInt(getComputedStyle(document.documentElement).getPropertyValue('--anchor-offset')) || 88;
      const topMargin = -(anchorOffset - 16); // 比 scroll-padding 稍宽松，让目标稳进激活带
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            allTocLinks.forEach(a => {
              a.classList.toggle('active', a.getAttribute('href') === '#' + id);
            });
          }
        });
      }, { rootMargin: `${topMargin}px 0px -70% 0px`, threshold: 0 });
      headings.forEach(h => observer.observe(h));
    }

    /* ── Mobile drawer ───────────────────────────── */
    const tocBtn = document.getElementById('tocBtn');
    const drawer = document.getElementById('drawer');
    const drawerOverlay = document.getElementById('drawerOverlay');
    if (tocBtn && drawer && drawerOverlay) {
      const closeDrawer = () => {
        drawer.classList.remove('open');
        drawerOverlay.classList.remove('open');
      };
      tocBtn.addEventListener('click', () => {
        drawer.classList.add('open');
        drawerOverlay.classList.add('open');
      });
      drawerOverlay.addEventListener('click', closeDrawer);
      drawer.addEventListener('click', (e) => { if (e.target.tagName === 'A') closeDrawer(); });
    }

    /* ── Reveal on scroll：自动给 .reveal 元素加 .in（触发动效）── */
    var reveals = document.querySelectorAll('.reveal');
    if (reveals.length) {
      if (!('IntersectionObserver' in window)) {
        reveals.forEach(function (el) { el.classList.add('in'); });
      } else {
        var revealIO = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) {
            if (en.isIntersecting) { en.target.classList.add('in'); revealIO.unobserve(en.target); }
          });
        }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
        reveals.forEach(function (el) { revealIO.observe(el); });
      }
    }
  });
})();
