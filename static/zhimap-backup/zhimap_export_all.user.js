// ==UserScript==
// @name         ZhiMap 全量导出（JSON + FreeMind .mm）
// @namespace    zhimap-export-all
// @version      1.0
// @description  登录 zhimap.com 后，自动导出名下所有思维导图。每张图保存 .json 源数据和 .mm(FreeMind) 两种格式。
// @match        https://zhimap.com/*
// @grant        GM_download
// @run-at       document-idle
// ==/UserScript==

(function () {
  'use strict';

  console.log('[ZhiMap] 油猴脚本已加载，正在等待注入按钮…');
  const API = 'https://zhimap.com/restful';

  // ---------- 工具 ----------
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function stripHtml(html) {
    const t = (html || '')
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<\/p>/gi, '\n')
      .replace(/<[^>]+>/g, '')
      .replace(/&nbsp;/g, ' ')
      .replace(/&lt;/g, '<').replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
    return t.replace(/\s+/g, ' ').trim();
  }

  function safeName(s) {
    return String(s || 'untitled')
      .replace(/[\r\n\t]+/g, ' ')
      .replace(/[\\/:*?"<>|\u200b]/g, '_')
      .slice(0, 60);
  }

  function xmlEscape(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&apos;');
  }

  // ---------- 导图 JSON -> FreeMind .mm ----------
  function nodeToMM(node) {
    const text = xmlEscape(stripHtml(node.title));
    const note = stripHtml(node.content);
    const children = node.children || [];
    let s = `<node TEXT="${text}"`;
    if (node.folded) s += ' FOLDED="true"';
    if (node.link) s += ` LINK="${xmlEscape(node.link)}"`;
    s += '>';
    if (note) s += `<richcontent TYPE="NOTE"><html><body>${xmlEscape(note).replace(/\n/g, '<br/>')}</body></html></richcontent>`;
    for (const c of children) s += nodeToMM(c);
    s += '</node>';
    return s;
  }

  // ---------- 根节点标题（比 mindMap.title 更有意义） ----------
  function rootTitle(mindMap) {
    const tree = mindMap.trees && mindMap.trees[0];
    return stripHtml((tree && tree.title) || mindMap.title) || 'untitled';
  }

  function toFreemind(mindMap) {
    const tree = mindMap.trees && mindMap.trees[0];
    const title = rootTitle(mindMap) || 'Root';
    return `<?xml version="1.0" encoding="UTF-8"?>\n<map version="1.0.1">\n${nodeToMM({ title: title, children: tree ? tree.children || [] : [] })}\n</map>`;
  }

  // ---------- 用 a 标签触发下载（更可靠，不用 GM_download） ----------
  function downloadBlob(content, filename, mime) {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 3000);
  }

  // ---------- 导出单张图 ----------
  async function exportMap(uuid, log) {
    const r = await fetch(`${API}/pub/mindmap/load_v?uuid=${uuid}`, { credentials: 'include' });
    const j = await r.json();
    if (j.code !== 0 || !j.data) throw new Error('获取数据失败: ' + (j.message || j.code));
    const mm = j.data.mindMap;
    const base = safeName(rootTitle(mm)) + '__' + uuid;

    // 1) 原始 JSON
    downloadBlob(JSON.stringify(j, null, 2), base + '.json', 'application/json');
    await sleep(300);
    // 2) FreeMind .mm
    downloadBlob(toFreemind(mm), base + '.mm', 'application/xml;charset=utf-8');
    await sleep(300);
    log('✓ ' + (rootTitle(mm) || uuid));
  }

  // ---------- 检查登录态 ----------
  async function checkLogin() {
    const r = await fetch(`${API}/sec/usrdir/list`, { credentials: 'include' });
    const j = await r.json();
    if (j.code === 2000 || j.code === 2100) return false;
    return true;
  }

  // ---------- 遍历目录树，收集所有目录 uuid（含根） ----------
  function collectDirs(node, out) {
    if (!node) return;
    if (node.uuid) out.add(node.uuid);
    (node.children || []).forEach(c => collectDirs(c, out));
  }

  // ---------- 拉取某个目录下所有导图 uuid（自动翻页） ----------
  async function listDirMaps(directoryUuid, log) {
    const uuids = [];
    let page = 0;
    const size = 50;
    for (;;) {
      const r = await fetch(`${API}/sec/dir_mindmap?directoryUuid=${directoryUuid}&page=${page}&size=${size}`, { credentials: 'include' });
      const j = await r.json();
      if (j.code !== 0) throw new Error('目录列表失败: ' + (j.message || j.code));
      const pageData = j.data || {};
      const content = pageData.content || [];
      content.forEach(c => {
        if (c && c.publicationInfo && c.publicationInfo.uuid) uuids.push(c.publicationInfo.uuid);
        else if (c && c.mindMap && c.mindMap.uuid) uuids.push(c.mindMap.uuid);
        else if (c && c.uuid) uuids.push(c.uuid);
      });
      const total = pageData.totalPages || 1;
      page++;
      if (page >= total) break;
      await sleep(200);
    }
    return uuids;
  }

  // ---------- 汇总全部个人导图 uuid ----------
  async function collectAllMine(log) {
    // 1) 目录树（含根"我的导图"）
    const r = await fetch(`${API}/sec/usrdir/list`, { credentials: 'include' });
    const j = await r.json();
    if (j.code !== 0) throw new Error('获取目录失败: ' + (j.message || j.code));
    const dirs = new Set();
    collectDirs(j.data, dirs);
    log(`目录树: ${dirs.size} 个目录`);

    // 2) 每个目录翻页拉导图
    const all = [];
    for (const d of dirs) {
      try {
        const list = await listDirMaps(d, log);
        log(`目录 ${d.slice(0, 8)}…: ${list.length} 张`);
        all.push(...list);
      } catch (e) {
        console.error('目录拉取失败:', d, e);
      }
    }
    // 去重
    return Array.from(new Set(all));
  }

  // ---------- 批量导出 ----------
  async function exportAll() {
    const btn = document.getElementById('zm-export-all-btn');
    const log = document.getElementById('zm-export-all-log');
    btn.disabled = true; btn.textContent = '导出中…';
    log.textContent = '';

    try {
      // 0) 登录态检查
      const logged = await checkLogin();
      if (!logged) {
        log.textContent = '未检测到登录态。请先刷新页面并确认右上角有头像（已登录），再点本按钮。';
        return;
      }

      // 1) 通过目录树汇总个人全部导图 uuid
      let uuids = await collectAllMine((m) => { log.textContent = m; });
      if (uuids.length === 0) {
        log.textContent = '没有找到任何导图。请确认当前账号在 ZhiMap 里有导图。';
        return;
      }
      log.textContent = `共找到 ${uuids.length} 张导图，开始导出…`;

      // 2) 逐个导出
      let okCount = 0, failCount = 0;
      for (let i = 0; i < uuids.length; i++) {
        try {
          await exportMap(uuids[i], (m) => { log.textContent = `[${i + 1}/${uuids.length}] ${m}`; });
          okCount++;
        } catch (e) {
          failCount++;
          console.error('导出失败:', uuids[i], e);
          log.textContent += `\n[失败] ${uuids[i]}: ${e.message}`;
        }
        await sleep(400); // 不要太快，避免触发限流
      }
      log.textContent += `\n✅ 完成！成功 ${okCount} / 共 ${uuids.length}。若浏览器弹出"允许多次下载"，请选择允许。`;
    } catch (e) {
      console.error(e);
      log.textContent = '出错: ' + e.message;
    } finally {
      btn.disabled = false; btn.textContent = '一键导出全部导图';
    }
  }

  // ---------- 注入按钮 ----------
  function injectUI() {
    if (document.getElementById('zm-export-all-btn')) return;
    const div = document.createElement('div');
    div.style.cssText = 'position:fixed;right:20px;bottom:20px;z-index:99999;font-family:system-ui;text-align:right;';
    div.innerHTML = `
      <div id="zm-export-all-log" style="max-width:420px;background:#fff;border:1px solid #ddd;border-radius:8px;padding:8px 12px;margin-bottom:6px;font-size:13px;color:#333;white-space:pre-wrap;text-align:left;display:none;box-shadow:0 2px 12px rgba(0,0,0,.15);"></div>
      <button id="zm-export-all-btn" style="background:#07c160;color:#fff;border:none;padding:12px 20px;border-radius:8px;font-size:15px;cursor:pointer;box-shadow:0 2px 12px rgba(0,0,0,.25);">一键导出全部导图</button>`;
    document.body.appendChild(div);
    document.getElementById('zm-export-all-btn').addEventListener('click', exportAll);
    document.getElementById('zm-export-all-log').style.display = 'block';
  }

  const t = setInterval(() => {
    if (document.body) { injectUI(); clearInterval(t); }
  }, 800);
})();
