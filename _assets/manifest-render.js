/**
 * manifest-render.js
 * 把 _assets/manifest.json（serve.py 动态生成）渲染到带 data-render 属性的容器里。
 *
 * 容器约定（在各 index.html 中使用）：
 *
 *   <ul data-render="insights" data-filter-audience="cross">
 *     <li class="placeholder">加载中…</li>
 *   </ul>
 *
 * 支持的 data-render 类别：
 *   insights | readings | frontier-deep | frontier-digest | oss | legacy
 *
 * 可选属性：
 *   data-limit="5"           只显示前 N 条（按日期倒序）
 *   data-filter-audience="…" 仅显示指定受众（tob/toc/cross）
 *   data-filter-vendor="…"   仅显示指定 vendor（frontier-* 用）
 *   data-style="recent"      用首页样式（recent-list class，简化 layout）
 *                "doc-list"  用子 index 页样式（默认）
 *                "entry"     卡片样式
 *
 * 路径前缀：
 *   data-href-prefix="../"   manifest 中 path 是相对站点根的；如果在子目录的页面里渲染，要拼前缀
 */
(function () {
  const MANIFEST_URLS = ["/_manifest.json"];

  // 记录本脚本自己的 URL —— 用于在 GitHub Pages 子路径部署下反推 manifest.json 位置
  const SELF_SRC = (document.currentScript && document.currentScript.src) || "";

  // 子页面 fallback：
  //   ① 从本 script (_assets/manifest-render.js) 的 src 直推同目录下的 manifest.json，
  //      与部署 base path 无关（能兼容 GitHub Pages 的 /<repo>/ 子路径）。
  //   ② 保留旧的深度探测做二次兜底（本地 serve.py / 站点根 = 服务器根 的场景）。
  function fallbackManifestUrls() {
    const urls = [];
    if (SELF_SRC) {
      urls.push(SELF_SRC.replace(/manifest-render\.js(\?.*)?$/, "manifest.json"));
    }
    const depth = (location.pathname.replace(/\/$/, "").match(/\//g) || []).length;
    const prefix = depth > 1 ? "../".repeat(depth - 1) : "";
    urls.push(prefix + "_assets/manifest.json");
    return urls;
  }

  const AUDIENCE_PILL = {
    tob: '<span class="pill pill-accent">ToB</span>',
    toc: '<span class="pill pill-warn">ToC</span>',
    cross: '<span class="pill pill-info">跨市场</span>',
  };

  // 把混合日期格式（2026-05-22 / 2026-05 / 2026-Q2）归一为可比较字符串。
  // 与 build_manifest.py 的 _date_sort_key 对齐。
  function dateSortKey(d) {
    if (!d) return "";
    const mq = /^(\d{4})-Q([1-4])$/i.exec(d);
    if (mq) {
      const qm = { "1": "01", "2": "04", "3": "07", "4": "10" }[mq[2]];
      return `${mq[1]}-${qm}-00`;
    }
    const mm = /^(\d{4})-(\d{2})$/.exec(d);
    if (mm) return `${d}-00`;
    return d;
  }
  function byDateDesc(a, b) {
    return dateSortKey(b.date).localeCompare(dateSortKey(a.date));
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function pillsFor(entry) {
    const pills = [];
    if (entry.audience && AUDIENCE_PILL[entry.audience]) {
      pills.push(AUDIENCE_PILL[entry.audience]);
    }
    if (entry.extra && entry.extra.vendor) {
      pills.push(`<span class="pill">${escapeHtml(entry.extra.vendor)}</span>`);
    }
    (entry.tags || []).forEach((t) => {
      pills.push(`<span class="pill">${escapeHtml(t)}</span>`);
    });
    return pills.join("");
  }

  function statusBadge(entry) {
    if (!entry.status) return "";
    if (entry.status === "草案" || entry.status === "记录中") {
      return ` <span style="font-size:.78rem;color:var(--text-muted);margin-left:.4em;">[${escapeHtml(entry.status)}]</span>`;
    }
    if (entry.status === "对内") {
      return ` <span style="font-size:.78rem;color:var(--text-muted);margin-left:.4em;">[对内]</span>`;
    }
    return "";
  }

  function renderRecent(entry, prefix) {
    return `<li data-audience="${escapeHtml(entry.audience || "all")}">
      <span class="recent-date">${escapeHtml(entry.date)}</span>
      <span class="recent-title"><a href="${escapeHtml(prefix + entry.path)}">${escapeHtml(entry.title)}</a>${statusBadge(entry)}</span>
      <span class="recent-tags">${pillsFor(entry)}</span>
    </li>`;
  }

  function renderDocList(entry, prefix) {
    return `<li data-audience="${escapeHtml(entry.audience || "all")}">
      <span class="doc-date">${escapeHtml(entry.date)}</span>
      <span class="doc-title"><a href="${escapeHtml(prefix + entry.path)}">${escapeHtml(entry.title)}</a>${statusBadge(entry)}</span>
      <span class="doc-tags">${pillsFor(entry)}</span>
    </li>`;
  }

  function renderEntry(entry, prefix) {
    const audienceStr = entry.audience ? `<span class="pill ${entry.audience === "tob" ? "pill-accent" : entry.audience === "cross" ? "pill-info" : ""}">${entry.audience === "tob" ? "ToB" : entry.audience === "toc" ? "ToC" : "跨市场"}</span>` : "";
    return `<li>
      <span class="entry-date">${escapeHtml(entry.date)}</span>
      <div class="entry-body">
        <h3><a href="${escapeHtml(prefix + entry.path)}">${escapeHtml(entry.title)}</a></h3>
        <div class="entry-tags">${audienceStr}${pillsFor(entry).replace(audienceStr, "")}</div>
      </div>
    </li>`;
  }

  // 类型 → 显示 label / 颜色
  const TYPE_META = {
    insight: { label: "洞察", dot: "type-insight" },
    oss: { label: "开源", dot: "type-oss" },
    "frontier-deep": { label: "厂商深度", dot: "type-frontier" },
    "frontier-digest": { label: "厂商动态", dot: "type-frontier" },
    legacy: { label: "归档", dot: "type-legacy" },
    readings: { label: "阅读材料", dot: "type-readings" },
  };

  function renderFeed(entry, prefix) {
    const t = TYPE_META[entry.category] || { label: entry.category, dot: "" };
    const audPill = entry.audience && AUDIENCE_PILL[entry.audience] ? AUDIENCE_PILL[entry.audience] : "";
    const tagPills = (entry.tags || [])
      .slice(0, 2)
      .map((s) => `<span class="pill">${escapeHtml(s)}</span>`)
      .join("");
    return `<li class="feed-row" data-audience="${escapeHtml(entry.audience || "all")}">
      <span class="feed-type ${t.dot}"><span class="feed-dot"></span>${escapeHtml(t.label)}</span>
      <span class="feed-date">${escapeHtml(entry.date)}</span>
      <a class="feed-title" href="${escapeHtml(prefix + entry.path)}">${escapeHtml(entry.title)}</a>
      <span class="feed-tags">${audPill}${tagPills}</span>
    </li>`;
  }

  const RENDERERS = {
    recent: renderRecent,
    "doc-list": renderDocList,
    entry: renderEntry,
    feed: renderFeed,
  };

  /** 类别 → manifest key */
  const CATEGORY_TO_KEY = {
    insights: "insights",
    "frontier-deep": "frontier_deep",
    "frontier-digest": "frontier_digest",
    oss: "oss",
    legacy: "legacy",
    readings: "readings",
  };

  /** 默认活动流来源（与首页 feed 一致；不含 legacy 归档） */
  const FEED_SOURCES = ["insights", "readings", "oss", "frontier-deep", "frontier-digest"];

  /** 合并活动流全部条目（跨类别） */
  function mergeFeed(manifest) {
    return FEED_SOURCES
      .map((c) => CATEGORY_TO_KEY[c])
      .filter(Boolean)
      .flatMap((k) => manifest[k] || []);
  }

  /** 一篇条目的可搜索文本：标题 / slug / 类型 / 受众 / 标签 / 状态 / vendor */
  function entrySearchText(e) {
    const slug = (e.path || "").split("/").pop().replace(/\.\w+$/, "");
    const catLabel = ((TYPE_META[e.category] || {}).label) || "";
    return [e.title, slug, catLabel, e.audience, ...(e.tags || []), e.status, (e.extra && e.extra.vendor) || ""]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
  }

  async function fetchManifest() {
    const urls = [...MANIFEST_URLS, ...fallbackManifestUrls()];
    let lastErr = null;
    for (const url of urls) {
      try {
        const res = await fetch(url, { cache: "no-store" });
        if (res.ok) return await res.json();
        lastErr = new Error("HTTP " + res.status);
      } catch (e) {
        lastErr = e;
      }
    }
    throw lastErr || new Error("manifest unreachable");
  }

  function renderContainer(container, manifest) {
    const category = container.dataset.render;
    let items;
    if (category === "feed") {
      // 统一活动流：默认合并洞察+开源+复盘+厂商+落地
      const defaultSources = FEED_SOURCES.join(",");
      const sources = (container.dataset.filterCategory || defaultSources)
        .split(",").map((s) => s.trim());
      const keys = sources.map((c) => CATEGORY_TO_KEY[c]).filter(Boolean);
      items = keys.flatMap((k) => manifest[k] || []);
      items.sort(byDateDesc);
    } else {
      const key = CATEGORY_TO_KEY[category];
      if (!key) {
        console.warn("Unknown data-render:", category);
        return;
      }
      items = (manifest[key] || []).slice();
    }

    const filterAudience = container.dataset.filterAudience;
    if (filterAudience) {
      items = items.filter((e) => e.audience === filterAudience);
    }
    const filterVendor = container.dataset.filterVendor;
    if (filterVendor) {
      items = items.filter((e) => e.extra && e.extra.vendor === filterVendor);
    }
    const filterCategoryAll = container.dataset.filterCategory;
    if (filterCategoryAll) {
      const wanted = filterCategoryAll.split(",").map((s) => s.trim());
      const keys = wanted.map((c) => CATEGORY_TO_KEY[c]).filter(Boolean);
      items = keys.flatMap((k) => manifest[k] || []);
      items.sort(byDateDesc);
    }

    const limit = parseInt(container.dataset.limit || "0", 10);
    if (limit > 0) items = items.slice(0, limit);

    const style = container.dataset.style || "doc-list";
    const renderer = RENDERERS[style] || renderDocList;
    const prefix = container.dataset.hrefPrefix || "";

    if (items.length === 0) {
      container.innerHTML = `<li class="empty" style="color:var(--text-muted);font-style:italic;padding:.6em 0;">（暂无内容）</li>`;
      return;
    }
    container.innerHTML = items.map((e) => renderer(e, prefix)).join("\n");
  }

  // ── Featured: 取最新一篇（默认从 insights + oss 合并）
  function renderFeatured(container, manifest) {
    const sources = (container.dataset.featuredSources || "insights,oss")
      .split(",")
      .map((s) => s.trim())
      .map((c) => CATEGORY_TO_KEY[c])
      .filter(Boolean);
    const merged = sources.flatMap((k) => manifest[k] || []);
    merged.sort(byDateDesc);
    const entry = merged[0];
    if (!entry) {
      container.innerHTML = "";
      return;
    }
    const prefix = container.dataset.hrefPrefix || "";
    const t = TYPE_META[entry.category] || { label: entry.category };
    const audPill = entry.audience && AUDIENCE_PILL[entry.audience] ? AUDIENCE_PILL[entry.audience] : "";
    const tags = (entry.tags || []).slice(0, 3).map((s) => `<span class="pill">${escapeHtml(s)}</span>`).join("");
    container.innerHTML = `
      <a class="featured-card" href="${escapeHtml(prefix + entry.path)}">
        <div class="featured-eyebrow">
          <span class="featured-badge">最新发布</span>
          <span class="featured-type">${escapeHtml(t.label)}</span>
        </div>
        <h3 class="featured-title">${escapeHtml(entry.title)}</h3>
        <div class="featured-meta">
          <span class="featured-date">${escapeHtml(entry.date)}</span>
          ${audPill}${tags}
        </div>
        <div class="featured-cta">阅读全文 <span class="featured-arrow">→</span></div>
      </a>`;
  }

  // ── Stats: 输出多个 stat chip
  function renderStats(container, manifest) {
    const allDocs = [
      ...(manifest.insights || []),
      ...(manifest.readings || []),
      ...(manifest.oss || []),
      ...(manifest.frontier_deep || []),
      ...(manifest.frontier_digest || []),
    ];
    const insightCount = (manifest.insights || []).length + (manifest.oss || []).length;
    const frontierCount = (manifest.frontier_deep || []).length + (manifest.frontier_digest || []).length;

    // 最新日期 → 距今天数
    const dates = allDocs.map((e) => e.date).filter((d) => /^\d{4}-\d{2}-\d{2}$/.test(d));
    dates.sort((a, b) => b.localeCompare(a));
    let daysAgoStr = "—";
    if (dates.length > 0) {
      const latest = new Date(dates[0] + "T00:00:00");
      const now = new Date();
      const days = Math.floor((now - latest) / (1000 * 60 * 60 * 24));
      daysAgoStr = days <= 0 ? "今天" : days === 1 ? "昨天" : `${days} 天前`;
    }

    container.innerHTML = `
      <span class="stat-item"><span class="stat-num">${insightCount}</span> 篇洞察 · 拆解</span>
      <span class="stat-sep" aria-hidden="true">·</span>
      <span class="stat-item"><span class="stat-num">${frontierCount}</span> 篇厂商深度</span>
      <span class="stat-sep" aria-hidden="true">·</span>
      <span class="stat-item">最近更新 <span class="stat-num">${daysAgoStr}</span></span>`;
  }

  function dispatchToContainer(container, manifest) {
    const cat = container.dataset.render;
    if (cat === "featured") return renderFeatured(container, manifest);
    if (cat === "stats") return renderStats(container, manifest);
    return renderContainer(container, manifest);
  }

  let _manifestCache = null;

  function bindHomeFeedAudienceFilter() {
    const bar = document.getElementById("filterBar");
    if (!bar || !_manifestCache) return;
    bar.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-filter]");
      if (!btn) return;
      bar.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const f = btn.dataset.filter;
      document.body.className = document.body.className.replace(/filter-\w+/g, "").trim();
      if (f !== "all") document.body.classList.add("filter-" + f);
      document.querySelectorAll('[data-render="feed"]').forEach((feed) => {
        if (f === "all") delete feed.dataset.filterAudience;
        else feed.dataset.filterAudience = f;
        dispatchToContainer(feed, _manifestCache);
      });
      // Re-apply search if active
      applySearch();
    });
  }

  // ── Search: title keyword filter for feed ──
  let _searchKeyword = "";

  function applySearch() {
    if (!_manifestCache) return;
    const active = !!_searchKeyword;
    const kw = _searchKeyword.toLowerCase();
    // 全局搜索：在全量活动流语料里匹配（标题 / slug / 类型 / 受众 / 标签 / 状态 / vendor），
    // 不受 feed 的 data-limit 与受众筛选限制
    const matches = active
      ? mergeFeed(_manifestCache)
          .filter((e) => entrySearchText(e).includes(kw))
          .sort(byDateDesc)
      : null;

    document.querySelectorAll('[data-render="feed"]').forEach((feed) => {
      if (!active) {
        // 无关键词：恢复正常 feed（尊重当前受众筛选与 limit）
        dispatchToContainer(feed, _manifestCache);
        return;
      }
      const prefix = feed.dataset.hrefPrefix || "";
      feed.innerHTML = matches.length
        ? matches.map((e) => renderFeed(e, prefix)).join("\n")
        : `<li class="feed-empty">没有匹配「${escapeHtml(_searchKeyword)}」的内容</li>`;
    });

    // 结果计数
    const meta = document.getElementById("searchMeta");
    if (meta) {
      meta.style.display = active ? "" : "none";
      if (active) meta.innerHTML = `共找到 <b>${matches.length}</b> 篇 · 关键词「${escapeHtml(_searchKeyword)}」`;
    }
    // 章节标题：搜索时切到「搜索结果」
    const dispH2 = document.querySelector(".disp-h2");
    if (dispH2) dispH2.textContent = active ? "搜索结果" : "前沿快报";
  }

  function bindSearch() {
    const input = document.getElementById("searchInput");
    const clearBtn = document.getElementById("searchClear");
    if (!input) return;
    let debounce = null;
    input.addEventListener("input", () => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        _searchKeyword = input.value.trim();
        clearBtn.style.display = _searchKeyword ? "" : "none";
        applySearch();
      }, 200);
    });
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        input.value = "";
        _searchKeyword = "";
        clearBtn.style.display = "none";
        applySearch();
        input.focus();
      });
    }
    // 顶栏搜索按钮：滚动到搜索框并聚焦
    const topSearch = document.getElementById("topSearch");
    if (topSearch && input) {
      topSearch.addEventListener("click", () => {
        input.scrollIntoView({ behavior: "smooth", block: "center" });
        setTimeout(() => input.focus({ preventScroll: true }), 350);
      });
    }
  }

  async function init() {
    const containers = document.querySelectorAll("[data-render]");
    if (containers.length === 0) return;
    try {
      const manifest = await fetchManifest();
      _manifestCache = manifest;
      containers.forEach((c) => dispatchToContainer(c, manifest));
      bindHomeFeedAudienceFilter();
      bindSearch();
      document.dispatchEvent(new CustomEvent("manifest:ready", { detail: { manifest } }));
    } catch (err) {
      console.warn("[manifest] fetch failed:", err);
      containers.forEach((c) => {
        if (c.querySelector(".placeholder")) {
          c.innerHTML = `<li style="color:var(--text-muted);font-style:italic;padding:.6em 0;">⚠ 无法加载 manifest（本地开发请用 <code>python3 serve.py</code>；线上部署请重跑 <code>python3 _assets/build_manifest.py</code> 生成静态快照后再发布）</li>`;
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
