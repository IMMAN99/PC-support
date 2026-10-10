#!/usr/bin/env python3
"""
Regression audit for the offline bundle of پشتیبان پی‌سی.

Renders the generated offline HTML in headless Chromium and prints a PASS/FAIL report.
Run from the repository root: python3 tools/audit.py
Input/output paths are resolved relative to this script. Install development requirements and Chromium first; see README.md.
"""
import asyncio, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_HTML = ROOT / "پشتیبان_رایانه.html"
OFFLINE_HTML = ROOT / "پیش‌نمایش_آفلاین.html"
FILE = OFFLINE_HTML.as_uri()
ok, bad, info = [], [], []

def check(cond, label, detail=""):
    (ok if cond else bad).append(f"{label}{(' — ' + detail) if detail else ''}")

def note(label, detail):
    info.append(f"{label} — {detail}")


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        pg = await ctx.new_page()
        await pg.goto(FILE, wait_until="load")
        await pg.wait_for_timeout(800)

        # ---------- F-01: diagnostic engine routing ----------
        r = await pg.evaluate("""() => ['صفحه آبی می‌ده','لپ‌تاپم آب ریخت روش'].map(t => {
            const h = runLocalIntelligentEngine('text', t).split('\\n')[0];
            return {q: t, bsod: h.includes('رم') || h.includes('حافظه') || h.includes('درایور'),
                    water: h.includes('مایعات')};
        })""")
        check(r[0]["bsod"] and not r[0]["water"],
              "F-01  «صفحه آبی» → تشخیص صفحه آبی/رم (نه مایعات)", f"got: bsod={r[0]['bsod']} water={r[0]['water']}")
        check(r[1]["water"],
              "F-01  «آب ریخت» هنوز مایعات تشخیص داده می‌شود", f"water={r[1]['water']}")

        # ---------- F-02: calendar header order (RTL) ----------
        await pg.evaluate("openBookingModal(); goToBookingStep(2)")
        await pg.wait_for_timeout(500)
        cal = await pg.evaluate("""() => {
            const m = document.getElementById('calCurrentMonthYear');
            const chip = m.parentElement.querySelector('span:not(#calCurrentMonthYear)');
            const mr = m.getBoundingClientRect(), cr = chip.getBoundingClientRect();
            return {monthX: Math.round(mr.x), chipX: Math.round(cr.x),
                    monthText: m.textContent.trim()};
        }""")
        check(cal["monthX"] > cal["chipX"], "F-02  برچسب ماه در جای درست RTL (راست‌تر از چیپ)",
              f"month.x={cal['monthX']} chip.x={cal['chipX']} «{cal['monthText']}»")
        await pg.evaluate("closeBookingModal()")

        # ---------- F-03 / REMOTE-01: legacy local schedule logic + neutral availability copy ----------
        info_hours = await pg.evaluate("""() => ({
            shop: (typeof SHOP_HOURS !== 'undefined') ? SHOP_HOURS : null,
            remote: (typeof REMOTE_SUPPORT !== 'undefined') ? REMOTE_SUPPORT : null,
            contact: (typeof SITE_CONTACT !== 'undefined') ? SITE_CONTACT : null,
            cal: typeof renderCalendarDays === 'function' ? renderCalendarDays.toString() : '',
            modalCopy: (document.getElementById('bookingModal') || {}).textContent || ''
        })""")
        shop, remote = info_hours["shop"] or {}, info_hours["remote"] or {}
        # These legacy local values still drive UI behavior; they are not verified business hours.
        check(shop.get("intake", {}).get("to") == 17 and shop.get("intake", {}).get("from") == 10
              and len(shop.get("weekdays", [])) == 5
              and "weekdayIdx === 5 || weekdayIdx === 6" in info_hours["cal"]
              and "زمان پذیرش حضوری اعلام نشده" in info_hours["modalCopy"],
              "F-03  منطق تقویم محلی حفظ است و مودال ساعت/دسترسی را اعلام نمی‌کند",
              f"intake={shop.get('intake')} weekdays={len(shop.get('weekdays', []))}")
        # Shift values remain internal UI logic, not a public coverage or response-time promise.
        shifts = remote.get("shifts", [])
        coverage_ok = (len(shifts) >= 3 and all(len(x.get("days", [])) == 7 for x in shifts))
        check(coverage_ok and remote.get("responseTargetMin") is None
              and "اعلام نشده" in str(remote.get("coverageLabel", "")),
              "REMOTE-01  قواعد زمانی داخلی حفظ‌اند و پوشش/زمان پاسخ‌گوییِ کسب‌وکار اعلام نمی‌شود",
              f"{len(shifts)} local shifts, target={remote.get('responseTargetMin')}, label={remote.get('coverageLabel')}")

        # Exercise the deterministic local indicator without treating it as actual staffing/availability.
        hours_check = await pg.evaluate("""() => {
            const Real = Date, out = [];
            const probes = ['2026-10-07T00:30:00Z','2026-10-07T05:00:00Z','2026-10-07T09:30:00Z',
                            '2026-10-07T14:00:00Z','2026-10-07T19:00:00Z','2026-10-07T22:30:00Z'];
            for (const iso of probes) {
                class FakeDate extends Real { constructor(...a){ if(a.length) super(...a); else super(iso); }
                                              static now(){ return new Real(iso).getTime(); } }
                window.Date = FakeDate;
                const p = renderPresence();
                window.Date = Real;
                out.push({ iso, count: p.count, online: p.online,
                           badge: (document.getElementById('shopHoursStatusText')||{}).textContent.trim() });
            }
            return out;
        }""")
        local_flags = all(isinstance(r["online"], bool) and r["count"] > 0 for r in hours_check)
        neutral_labels = all("اعلام نشده" in r["badge"] for r in hours_check)
        check(local_flags and neutral_labels,
              "REMOTE-01  نشانگر محلی در شش زمان آزمون اجرا می‌شود؛ متن وضعیت همچنان نامشخص است",
              "; ".join(f"{r['iso'][11:16]}Z→{r['count']} / {r['badge']}" for r in hours_check))

        # The local manual override must not change the neutral user-facing status copy.
        offline_mode = await pg.evaluate("""() => {
            const keep = REMOTE_SUPPORT.manualOverride;
            REMOTE_SUPPORT.manualOverride = 'offline';
            const p = renderPresence();
            const badge = (document.getElementById('shopHoursStatusText')||{}).textContent.trim();
            REMOTE_SUPPORT.manualOverride = keep;
            renderPresence();
            return { online: p.online, count: p.count, badge };
        }""")
        check((not offline_mode["online"]) and offline_mode["count"] == 0
              and "اعلام نشده" in offline_mode["badge"],
              "REMOTE-01  override محلیِ offline وضعیت تجاریِ تأییدنشده‌ای نمایش نمی‌دهد",
              f"badge=«{offline_mode['badge'][:40]}»")

        # remote request form: fields exist, idempotent accept-path saves a ticket
        form_ok = await pg.evaluate("""() => {
            openRemoteModal();
            const need = ['remoteNameInput','remotePhoneInput','remoteOsSelect','remoteCategorySelect',
                          'remoteToolSelect','remoteProblemInput','remoteChannelSelect','remoteConsentCheck'];
            const missing = need.filter(id => !document.getElementById(id));
            return { missing, hasForm: !!document.getElementById('remoteFormView'),
                     hasSuccess: !!document.getElementById('remoteSuccessView') };
        }""")
        check(not form_ok["missing"] and form_ok["hasForm"] and form_ok["hasSuccess"],
              "REMOTE-04  فرم درخواست ریموت کامل است (۸ فیلد + نمای موفقیت)",
              f"missing={form_ok['missing']}")

        submit_ok = await pg.evaluate("""() => {
            localStorage.removeItem('poshtiban_tickets');
            document.getElementById('remoteNameInput').value = 'کاربر آزمایشی';
            document.getElementById('remotePhoneInput').value = '09000000000';
            document.getElementById('remoteConsentCheck').checked = true;
            handleRemoteSubmit({ preventDefault(){} });
            const code = document.getElementById('remoteSuccessCode').textContent.trim();
            const tickets = JSON.parse(localStorage.getItem('poshtiban_tickets') || '{}');
            const t = tickets[code] || null;
            const visible = !document.getElementById('remoteSuccessView').classList.contains('hidden');
            closeRemoteModal();
            return { code, saved: !!t, type: t && t.type, status: t && t.status, visible, next: t && t.step };
        }""")
        check(submit_ok["saved"] and submit_ok["type"] == "remote" and submit_ok["visible"]
              and submit_ok["code"].startswith("RM-"),
              "REMOTE-04  ثبت درخواست: کد RM + ذخیره در همان انبار پیگیری + نمایش کد",
              f"code={submit_ok['code']} status=«{(submit_ok['status'] or '')[:34]}»")

        # invalid phone must be rejected (Persian digits normalised)
        reject = await pg.evaluate("""() => {
            openRemoteModal();
            document.getElementById('remoteNameInput').value = 'x';
            document.getElementById('remotePhoneInput').value = '۰۹۱۲';
            document.getElementById('remoteConsentCheck').checked = true;
            handleRemoteSubmit({ preventDefault(){} });
            const stillForm = !document.getElementById('remoteFormView').classList.contains('hidden');
            closeRemoteModal();
            return stillForm;
        }""")
        check(reject, "REMOTE-04  شمارهٔ نامعتبر رد می‌شود (فرم بسته نمی‌شود)")

        # seamless tracking: the request code opens in the existing tracking modal
        track_ok = await pg.evaluate("""() => {
            const code = Object.keys(JSON.parse(localStorage.getItem('poshtiban_tickets')||'{}'))[0];
            openTrackingModalWithCode(code);
            const title = (document.getElementById('trackDeviceTitle')||{}).textContent || '';
            const badge = (document.getElementById('trackStatusBadge')||{}).textContent || '';
            closeTrackingModal();
            return { title, badge };
        }""")
        check("ریموت" in track_ok["title"] or "ریموت" in track_ok["badge"],
              "REMOTE-04  درخواست ریموت در ماژول پیگیری قابل رهگیری است",
              f"«{track_ok['title'][:30]}» / «{track_ok['badge'][:28]}»")

        # ==================== Round 2 — the shop's list (image-1 / image-2) ====================
        r2 = await pg.evaluate("""() => {
            const nav = [...document.querySelectorAll('nav a')].map(a => a.textContent.trim());
            const heroCtas = [...document.querySelectorAll('#overview > div.mt-8 a, #overview > div.mt-8 button')]
                                 .map(b => b.textContent.replace(/\\s+/g, ' ').trim());
            const sections = [...document.querySelectorAll('section[id]')].map(s => s.id);
            const headerBtn = [...document.querySelectorAll('header button')].map(b => b.textContent.trim());
            const footerFirst = ((document.querySelector('footer a') || {}).textContent || '').trim();
            const faqFirst = ((document.querySelector('#faq button[aria-expanded]') || {}).textContent || '').trim();
            const h1 = document.querySelector('h1').textContent.replace(/\\s+/g, ' ').trim();
            const heroText = document.getElementById('overview').textContent.replace(/\\s+/g, ' ');
            const badge = document.getElementById('shopHoursStatusText');
            const badgeLong = document.getElementById('shopHoursStatusTextLong');
            const navRemote = [...document.querySelectorAll('nav a')].find(a => a.textContent.includes('راهنمایی از راه دور'));
            const strip = document.getElementById('heroStatusStrip');
            const boxes = strip ? [...strip.children].map(el => ({
                tone: el.getAttribute('data-tone') || '',
                bg: getComputedStyle(el).backgroundColor, border: getComputedStyle(el).borderColor,
                text: el.textContent.replace(/\\s+/g, ' ').trim() })) : [];
            const launcher = document.getElementById('aiFloatingLauncherBtn');
            return { nav, heroCtas, sections, headerBtn, footerFirst, faqFirst, h1, heroText,
                     badge: badge ? badge.textContent.trim() : '(missing)',
                     badgeTitle: badge ? (badge.getAttribute('title') || badge.getAttribute('aria-label') || '') : '',
                     navRemoteText: navRemote ? navRemote.textContent.trim() : '(missing)',
                     navRemoteDot: !!(navRemote && navRemote.querySelector('span.bg-emerald-500')),
                     boxes,
                     launcherOnclick: launcher ? (launcher.getAttribute('onclick') || '') : '',
                     staleIds: ['heroPresenceDot', 'heroPresenceText', 'heroPresenceChip']
                                 .filter(id => document.getElementById(id)) };
        }""")

        # item 1 — the H1 carries no comma / full stop any more
        check(not re.search(r"[،.]", r2["h1"]),
              "R2-01  تیتر اصلی بدون «،» و «.» انتهایی", f"«{r2['h1']}»")
        # item 2 — the indicator may retain its local color logic, but its text no longer
        # asserts a live count or response-time promise.
        check(r2["badge"] == "اعلام نشده" and "اعلام نشده" in r2["badgeTitle"]
              and "۱۵ دقیقه" not in r2["heroText"] and not r2["staleIds"],
              "R2-02  وضعیت پاسخ‌گویی و زمان آن اعلام‌نشده است؛ شناسه‌های قدیمی هیرو برنگشته‌اند",
              f"badge=«{r2['badge']}» title=«{r2['badgeTitle'][:40]}…» stale={r2['staleIds']}")
        # item 3 — neutral navigation/CTA labels distinguish the guidance section and its action.
        check(r2["navRemoteText"] == "راهنمایی از راه دور" and not r2["navRemoteDot"]
              and any("درخواست راهنمایی از راه دور" in t for t in r2["headerBtn"]),
              "R2-03  لینک راهنمایی از راه دور بدون نقطه و CTA هدر با برچسب خنثی",
              f"nav=«{r2['navRemoteText']}» greenDot={r2['navRemoteDot']}")
        # item 4 — AI first: nav, hero CTA, header action, launcher, footer, FAQ, section order
        ai_first = (bool(r2["nav"]) and "راهنمای عیب‌یابی اولیه" in r2["nav"][0]
                    and bool(r2["heroCtas"]) and "عیب‌یابی" in r2["heroCtas"][0]
                    and bool(r2["headerBtn"]) and "مشاور" in r2["headerBtn"][0]
                    and "toggleAiDrawer" in r2["launcherOnclick"]
                    and "راهنمای عیب‌یابی اولیه" in r2["footerFirst"]
                    and "ابزار راهنمایی" in r2["faqFirst"]
                    and r2["sections"].index("ai-diagnostic") < r2["sections"].index("remote-support"))
        check(ai_first,
              "R2-04  راهنمای اولیه در ناوبری، CTA، هدر، دکمهٔ شناور، فوتر و FAQ در اولویت است",
              f"nav[0]=«{r2['nav'][0] if r2['nav'] else ''}» · heroCta[0]=«{r2['heroCtas'][0] if r2['heroCtas'] else ''}» · "
              f"header[0]=«{r2['headerBtn'][0][:20] if r2['headerBtn'] else ''}» · launcher=«{r2['launcherOnclick'][:22]}» · "
              f"sections={r2['sections'][:2]}")
        # item 6 — no unverified business hours are printed in the visible page copy.
        body_text = await pg.evaluate("() => document.body.textContent")
        time_claims = ("۹:۳۰", "09:30", "۱۰:۰۰", "10:00", "۱۷:۰۰", "17:00")
        check(not any(token in body_text for token in time_claims)
              and "زمان پذیرش حضوری اعلام نشده" in body_text
              and "زمان پاسخ‌گویی اعلام نشده" in body_text,
              "R2-06  متن دیداری ساعت/زمان پاسخ را اعلام‌نشده نشان می‌دهد و ساعت کسب‌وکار نمی‌سازد",
              f"timeClaims={[token for token in time_claims if token in body_text]}")
        # item 7 — the hero status row remains two separate, visually differentiated information boxes.
        boxed = (len(r2["boxes"]) == 2
                 and {b["tone"] for b in r2["boxes"]} == {"intake", "remote"}
                 and r2["boxes"][0]["border"] != r2["boxes"][1]["border"]
                 and any("پذیرش حضوری" in b["text"] for b in r2["boxes"])
                 and any("از راه دور" in b["text"] for b in r2["boxes"])
                 and all(b["bg"].startswith("rgba") for b in r2["boxes"]))
        check(boxed, "R2-07  نوار هیرو دو باکس اطلاعاتیِ رنگ‌مایه‌دار و مستقل دارد",
              " · ".join(f"«{b['text'][:24]}» {b['border']}" for b in r2["boxes"]))
        # item 8 — the remote form uses the bottleneck dropdown component (no native selects)
        dd = await pg.evaluate("""() => {
            openRemoteModal();
            const label0 = document.getElementById('remoteOsSelect-label').textContent.trim();
            const trigger = document.getElementById('remoteOsSelect-trigger');
            trigger.click();
            const opened = !document.getElementById('remoteOsSelect-menu').classList.contains('hidden')
                           && trigger.getAttribute('aria-expanded') === 'true';
            const optCount = document.querySelectorAll('.remoteOsSelect-opt').length;
            selectModalDropdownOption('remoteOsSelect', 'لینوکس', 'لینوکس');
            const after = { label: document.getElementById('remoteOsSelect-label').textContent.trim(),
                            value: document.getElementById('remoteOsSelect').value,
                            closed: document.getElementById('remoteOsSelect-menu').classList.contains('hidden'),
                            expanded: trigger.getAttribute('aria-expanded') };
            const sim = document.getElementById('simCpu-trigger');
            const sameLook = trigger.className.includes('rounded-xl')
                             && getComputedStyle(trigger).borderRadius === getComputedStyle(sim).borderRadius;
            document.getElementById('remoteNameInput').value = 'آزمون راند ۲';
            document.getElementById('remotePhoneInput').value = '09000000000';
            document.getElementById('remoteConsentCheck').checked = true;
            handleRemoteSubmit({ preventDefault(){} });
            const code = document.getElementById('remoteSuccessCode').textContent.trim();
            const t = JSON.parse(localStorage.getItem('poshtiban_tickets') || '{}')[code] || {};
            closeRemoteModal();
            return { label0, opened, optCount, after, sameLook, ticketDevice: t.device || '', ticketTool: t.tool || '', nativeSelects: document.querySelectorAll('select').length };
        }""")
        check(dd["opened"] and dd["after"]["label"] == "لینوکس" and dd["after"]["value"] == "لینوکس"
              and dd["after"]["closed"] and dd["after"]["expanded"] == "false"
              and dd["optCount"] == 5 and dd["sameLook"] and "لینوکس" in dd["ticketDevice"]
              and dd["nativeSelects"] == 0,
              "R2-08  منوهای مودال ریموت مثل منوی «تست گلوگاه» باز/انتخاب می‌شوند و مقدار در تیکت ثبت می‌شود",
              f"«{dd['label0']}» → «{dd['after']['label']}» · options={dd['optCount']} · ticket.device=«{dd['ticketDevice']}» · native selects={dd['nativeSelects']}")

        # messenger hand-off is wired but intentionally dormant until SITE_CONTACT is filled
        note("REMOTE-04  تحویل درخواست به پیام‌رسان",
             "کد آماده است؛ با پر کردن SITE_CONTACT.whatsapp/telegram دکمه در پیام موفقیت ظاهر می‌شود (تنها مسیر واقعی رسیدن درخواست بدون بک‌اند)")

        # ---------- F-04: Persian digits + consistent separators ----------
        d = await pg.evaluate("""() => {
            openBookingModal(); goToBookingStep(3);
            const modal = document.getElementById('bookingModal');
            const out = {
                count: document.getElementById('bookSelectedCountText').textContent.trim(),
                summary: document.getElementById('bookSummaryServiceCount').textContent.trim(),
                latinSep: /[\u06F0-\u06F9],[\u06F0-\u06F9]/.test(modal.innerHTML),
                faSep: /[\u06F0-\u06F9]\u066C[\u06F0-\u06F9]/.test(modal.innerHTML)
            };
            closeBookingModal();
            return out;
        }""")
        latin = [v for k, v in d.items() if isinstance(v, str) and re.search(r"[0-9]", v)]
        # The booking flow has no disclosed amounts, so check Persian digits and absence of currency values.
        no_price = await pg.evaluate(r"""() => {
            openBookingModal();
            const modal = document.getElementById('bookingModal');
            const txt = modal.textContent.replace(/\s+/g, ' ');
            const priceWords = ['تومان', 'ريال', 'ریال', 'برآورد اجرت', 'جمع برآورد'];
            const hit = priceWords.filter(w => txt.includes(w) && w !== 'برآورد اجرت');
            const step3 = (() => { goToBookingStep(3);
                return document.getElementById('bookingModal').textContent.replace(/\s+/g, ' '); })();
            closeBookingModal();
            return { hit, step3HasPrice: /تومان|ريال|ریال/.test(step3),
                     step3Note: (document.getElementById('bookSummaryPriceText') || {}).textContent || '' };
        }""")
        check(not latin and not d["latinSep"] and not no_price["hit"] and not no_price["step3HasPrice"],
              "F-04  اعداد فارسی در جریان رزرو و بدون مبلغ یا واحد پولی",
              f"latin={latin} latinSep={d['latinSep']} priceWords={no_price['hit']} step3=«{no_price['step3Note']}»")

        # ---------- F-05: landmarks ----------
        lm = await pg.evaluate("""() => {
            const a = document.querySelector('a[href^="#main"], a[href^="#content"]');
            let visible = null;
            if (a) { a.focus(); const r = a.getBoundingClientRect();
                     visible = r.width > 20 && r.height > 10; }
            return {main: document.querySelectorAll('main').length, skip: !!a, visible,
                    nav: document.querySelectorAll('nav').length};
        }""")
        check(lm["main"] >= 1 and lm["skip"] and lm["visible"],
              "F-05  <main> + لینک پرش که با فوکوس دیده می‌شود",
              f"main={lm['main']} skip={lm['skip']} visibleOnFocus={lm['visible']}")

        # ---------- F-06 / F-07: keyboard-reachable interactive elements ----------
        k = await pg.evaluate("""() => ({
            divOnclick: document.querySelectorAll('div[onclick], span[onclick]').length,
            serviceCardsBtn: [...document.querySelectorAll('[id^=serviceCard_]')].filter(e => e.tagName === 'BUTTON').length,
            uploadLabel: !!document.querySelector('label[for="aiImageFileInput"]') ||
                         (() => { const z = document.getElementById('dropZoneArea');
                                  return !!z && z.getAttribute('role') === 'button' && z.tabIndex >= 0; })(),
            unlabeled: [...document.querySelectorAll('input:not([type=hidden]), select, textarea')]
                        .filter(e => !e.labels?.length && !e.getAttribute('aria-label') && !e.getAttribute('aria-labelledby')).length
        })""")
        check(k["divOnclick"] == 0, "F-06  هیچ div[onclick] باقی نمانده", f"remaining={k['divOnclick']}")
        check(k["serviceCardsBtn"] >= 4, "F-06  کارت‌های خدمات دکمهٔ واقعی هستند", f"buttons={k['serviceCardsBtn']}")
        check(k["uploadLabel"], "F-07  ناحیهٔ بارگذاری تصویر با label/button قابل‌دسترس")
        check(k["unlabeled"] == 0, "F-07  هیچ فیلد بدون برچسب نمانده", f"unlabeled={k['unlabeled']}")

        # ---------- F-08: chat drawer focus + live region ----------
        dr = await pg.evaluate("""() => { toggleAiDrawer(true); return new Promise(res => setTimeout(() => {
            res({focused: document.activeElement?.id || document.activeElement?.tagName,
                 live: !!document.querySelector('#aiChatHistoryContainer[aria-live]')}); }, 500)); }""")
        check(dr["focused"] == "aiChatDrawerInput", "F-08  فوکوس خودکار در فیلد چت", f"activeElement={dr['focused']}")
        check(dr["live"], "F-08  تاریخچهٔ چت aria-live دارد")
        await pg.evaluate("toggleAiDrawer(false)")

        # ---------- F-09: focus visibility ----------
        fo = await pg.evaluate("""() => {
            const all = [...document.querySelectorAll('button, a[href], [role=button]')];
            const cls = all.filter(e => /(^|\\s)(focus|focus-visible):/.test(e.className)).length;
            const global = [...document.styleSheets].some(s => { try {
                return [...s.cssRules].some(r => /:focus-visible/.test(r.selectorText || '')); } catch(e){ return false; } });
            return {total: all.length, withClass: cls, global};
        }""")
        check(fo["global"] or fo["withClass"] / max(fo["total"], 1) > 0.9,
              "F-09  حالت فوکوس برای همهٔ عناصر تعاملی",
              f"{fo['withClass']}/{fo['total']} کلاس focus، قاعدهٔ سراسری={fo['global']}")

        # ---------- F-10: calendar contrast ----------
        ct = await pg.evaluate("""() => {
            openBookingModal(); goToBookingStep(2);
            const parse = c => (c.match(/[\\d.]+/g) || []).map(Number);
            const comp = (fg, bg) => { const [r,g,b,a=1] = fg;
                return [r*a + bg[0]*(1-a), g*a + bg[1]*(1-a), b*a + bg[2]*(1-a)]; };
            const lum = ([r,g,b]) => { const f = v => { v /= 255;
                return v <= .03928 ? v/12.92 : Math.pow((v+.055)/1.055, 2.4); };
                return .2126*f(r) + .7152*f(g) + .0722*f(b); };
            const ratio = (a, b) => { const L1 = lum(a), L2 = lum(b);
                return (Math.max(L1,L2)+.05) / (Math.min(L1,L2)+.05); };
            const white = [255,255,255], out = {};
            const dis = document.querySelector('.cal-day-cell-disabled');
            const off = document.querySelector('.cal-day-cell-off');
            if (dis) out.disabled = Math.round(ratio(comp(parse(getComputedStyle(dis).color), white), white)*100)/100;
            if (off) out.off      = Math.round(ratio(comp(parse(getComputedStyle(off).color), white), white)*100)/100;
            closeBookingModal();
            return out;
        }""")
        worst = min(v for v in ct.values()) if ct else 0
        check(worst >= 4.5, "F-10  کنتراست تاریخ‌های غیرفعال/تعطیل ≥ ۴.۵:۱ (ترکیب‌شده روی پس‌زمینه)",
              f"disabled={ct.get('disabled')}:1  off={ct.get('off')}:1")

        # ---------- F-06: keyboard operation of cards + drop zone ----------
        kbd = await pg.evaluate("""() => {
            const card = document.getElementById('serviceCard_ram');
            openBookingModal(); goToBookingStep(1);
            card.focus();
            const focused = document.activeElement === card;
            const before = card.getAttribute('aria-pressed');
            card.click();
            const after = card.getAttribute('aria-pressed');
            card.click();
            closeBookingModal();
            const z = document.getElementById('dropZoneArea');
            return {isButton: card.tagName === 'BUTTON', focused, before, after,
                    zone: {tag: z.tagName, role: z.getAttribute('role'), tab: z.tabIndex,
                           label: !!z.getAttribute('aria-label'), forAttr: z.getAttribute('for')}};
        }""")
        check(kbd["isButton"] and kbd["focused"] and kbd["before"] == "false" and kbd["after"] == "true",
              "F-06  کارت خدمات با کیبورد فوکوس و فعال می‌شود (aria-pressed هم‌زمان عوض می‌شود)",
              f"<{kbd.get('isButton') and 'button'}> focused={kbd['focused']} aria-pressed {kbd['before']}→{kbd['after']}")
        check(kbd["zone"]["role"] == "button" and kbd["zone"]["tab"] == 0
              and kbd["zone"]["label"] and kbd["zone"]["forAttr"] == "aiImageFileInput",
              "F-06  ناحیهٔ بارگذاری تصویر: role=button، در ترتیب Tab، با برچسب و for",
              f"{kbd['zone']}")

        # ---------- F-13: FAQ accordion semantics + open/close behaviour ----------
        faq = await pg.evaluate("""() => {
            const btns = [...document.querySelectorAll('#faq button[aria-expanded]')];
            const b = btns[0];
            const answer = document.getElementById(b.getAttribute('aria-controls'));
            const before = b.getAttribute('aria-expanded');
            const wasHidden = answer.classList.contains('hidden');
            b.click();
            const after = b.getAttribute('aria-expanded');
            const nowHidden = answer.classList.contains('hidden');
            const rotated = b.querySelector('.faq-icon').classList.contains('rotate-180');
            b.click();
            const closedAgain = b.getAttribute('aria-expanded') === 'false' && !answer.classList.contains('rotate-180');
            return {count: btns.length, before, after, wasHidden, nowHidden, rotated, closedAgain};
        }""")
        check(faq["count"] == 6 and faq["before"] == "false" and faq["after"] == "true"
              and faq["wasHidden"] and not faq["nowHidden"] and faq["rotated"] and faq["closedAgain"],
              "F-13  آکاردئون FAQ: aria-expanded/aria-controls باز و بسته می‌شود (۶ مورد)",
              f"count={faq['count']} aria {faq['before']}→{faq['after']} rotated={faq['rotated']}")

        # An element only counts as "covering text" if it is actually perceptible:
        # display/visibility/opacity are checked, and the launcher's own box must be on screen.
        VIS_JS = """const __vis = el => { const cs = getComputedStyle(el);
            return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.05; };
          const __launcher = () => { const el = document.getElementById('aiFloatingLauncherBtn');
            if (!el || !__vis(el)) return null;
            const a = el.getBoundingClientRect();
            return (a.bottom <= 0 || a.top >= innerHeight) ? null : a; };"""
        OVERLAP_JS = "() => { " + VIS_JS + """
          const a = __launcher(); if (!a) return [];
          return [...document.querySelectorAll('h2, h3, p, li, span, b, code')].filter(e => {
            if (!__vis(e)) return false;
            const r = e.getBoundingClientRect();
            if (!r.width || !r.height || r.height > 200) return false;
            if (document.getElementById('aiFloatingLauncherBtn').contains(e)) return false;
            if (!(r.top < innerHeight && r.bottom > 0)) return false;
            return a.left < r.right && a.right > r.left && a.top < r.bottom && a.bottom > r.top;
          }).map(e => e.textContent.trim().slice(0, 24)).slice(0, 3); }"""
        AWAY_JS = "() => { " + VIS_JS + """ return __launcher() === null; }"""

        # ---------- F-11 (desktop): same overlap probe at 1440px ----------
        desktop_overlap, desktop_idle = [], []
        for sel in ("#bottleneck", "#plans", "#speed-booster", "footer"):
            await pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'start'}})")
            await pg.wait_for_timeout(1300)            # page uses scroll-smooth + a 450ms reveal
            hits = await pg.evaluate(OVERLAP_JS)
            if hits:
                desktop_idle.append(f"{sel}: {hits}")
            if hits:
                desktop_overlap.append(f"{sel}: {hits}")

        # ---------- F-11 / F-12: mobile ----------
        # عمداً بدون «کاهش حرکت»: منطق کنار‌رفتن دکمهٔ شناور در حالت کاهش حرکت خودش خاموش می‌شود (رفتار موردانتظار)
        m = await b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        await m.goto(FILE, wait_until="load"); await m.wait_for_timeout(700)
        # mobile: while the page is moving the launcher must be out of the way,
        # and once it settles it must not sit on top of any text either
        overlap_hits, idle_hits, away_fail = [], [], []
        for sel in ("#speed-booster", "#bottleneck", "#plans", "footer"):
            for block in ("start", "center"):
                await m.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'{block}'}})")
                await m.wait_for_timeout(250)          # still mid-scroll (the page animates scrolls)
                # two samples inside the same scroll animation (the page animates scrolls for ~700ms)
                mid_hits = await m.evaluate(OVERLAP_JS)
                await m.wait_for_timeout(250)
                mid = {"hits": mid_hits + await m.evaluate(OVERLAP_JS), "away": await m.evaluate(AWAY_JS)}
                if mid["hits"]:
                    overlap_hits.append(f"{sel}[{block}]: {mid['hits']}")
                if not mid["away"]:
                    away_fail.append(f"{sel}[{block}]")
                await m.wait_for_timeout(1000)         # settled
                hits = await m.evaluate(OVERLAP_JS)
                if hits:
                    idle_hits.append(f"{sel}[{block}]: {hits}")
        mo = await m.evaluate("""() => {
            const badge = document.getElementById('liveWorkStatusBadge');
            const aiBtn = [...document.querySelectorAll('button')].find(b => /toggleAiDrawer/.test(b.getAttribute('onclick')||'') && /2xl:flex/.test(b.className));
            return {badgeVisible: badge ? getComputedStyle(badge).display !== 'none' : false,
                    aiHeaderVisible: aiBtn ? getComputedStyle(aiBtn).display !== 'none' : false,
                    overflow: document.documentElement.scrollWidth > window.innerWidth + 1};
        }""")
        check(not desktop_overlap and not desktop_idle,
              "F-11  دسکتاپ: دکمهٔ شناور در گاتر می‌نشیند و روی متن نمی‌افتد (ثابت و متحرک)",
              f"overlaps: moving={len(desktop_overlap)} idle={len(desktop_idle)}"
              + (f" · {desktop_idle[0]}" if desktop_idle else ""))
        check(not overlap_hits and not away_fail,
              "F-11  موبایل: هنگام اسکرول کنار می‌رود (جای خالی روی متن نمی‌گذارد)",
              f"mid-scroll overlaps={len(overlap_hits)} · still-visible-during-scroll={len(away_fail)}"
              + (f" · {overlap_hits[0]}" if overlap_hits else "")
              + (f" · visible@ {away_fail[0]}" if away_fail else ""))
        check(not idle_hits,
              "F-11  موبایل: حتی بعد از توقف اسکرول هم روی متن نمی‌افتد",
              f"idle overlaps={len(idle_hits)}" + (f" · {idle_hits[0]}" if idle_hits else ""))
        check(mo["badgeVisible"] or mo["aiHeaderVisible"],
              "F-12  نشانگر اطلاعاتیِ خنثی یا دسترسی به راهنمای عیب‌یابی در موبایل دیده می‌شود",
              f"badge={mo['badgeVisible']} aiHeader={mo['aiHeaderVisible']}")
        check(not mo["overflow"], "F-12  بدون سرریز افقی در ۳۹۰px")

        # F-11 (round 2): at the very top of the page the launcher may sit over decorative
        # chrome on a phone, but it must never cover *reading* text (checked at 390 and 360)
        top_hits = {}
        for w in (390, 360):
            if w != 390:
                await pg.set_viewport_size({"width": w, "height": 844})
                await pg.wait_for_timeout(300)
            await pg.evaluate("window.scrollTo(0, 0)")
            await pg.wait_for_timeout(500)
            top_hits[w] = await pg.evaluate(r"""() => {
                const wrap = document.getElementById('aiFloatingLauncher');
                if (getComputedStyle(wrap).opacity === '0') return [];
                const a = document.getElementById('aiFloatingLauncherBtn').getBoundingClientRect();
                return [...document.querySelectorAll('h1,h2,h3,h4,p,li,b,strong,code')].filter(e => {
                    if (e.closest('#aiFloatingLauncher')) return false;
                    const r = e.getBoundingClientRect();
                    return r.width > 0 && r.height > 0 && r.top < innerHeight && r.bottom > 0
                        && r.left < innerWidth && r.right > 0
                        && !(r.right <= a.left || r.left >= a.right || r.bottom <= a.top || r.top >= a.bottom);
                }).map(e => e.tagName + ':' + e.textContent.replace(/\s+/g, ' ').trim().slice(0, 26));
            }""")
        await pg.set_viewport_size({"width": 390, "height": 844})
        check(not top_hits[390] and not top_hits[360],
              "F-11  در بالای صفحه (۳۹۰ و ۳۶۰px) هم روی متن خواندنی نمی‌افتد",
              f"390={top_hits[390][:3]} · 360={top_hits[360][:3]}")

        # ==================== Round 3 — header, no prices, smart AI, generic services ============
        r3 = await pg.evaluate(r"""() => {
            const txt = el => (el ? el.textContent.replace(/\s+/g, ' ').trim() : '');
            const bar = document.querySelector('header > div');
            const vis = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
            const nav = [...document.querySelectorAll('nav a')].map(a => txt(a));
            const headerAll = [...bar.querySelectorAll('a,button')].filter(vis).map(txt);
            const pageText = document.body.textContent.replace(/\s+/g, ' ');
            // No numeric/currency prices are disclosed; keep a guard against currency nodes.
            const priceNodes = [...document.querySelectorAll('body *')]
                .filter(e => !e.children.length && e.textContent.includes('تومان'))
                .map(e => ({ txt: txt(e).slice(0, 20), inPlans: !!e.closest('#plans') }));
            return {
                nav, headerAll, pageText,
                priceNodes: priceNodes,
                catalog: typeof SERVICES_CATALOG === 'object' ? Object.keys(SERVICES_CATALOG) : [],
                priceProps: Object.values(SERVICES_CATALOG || {}).filter(v => 'price' in v).length,
                otherCard: !!document.getElementById('serviceCard_other'),
                otherWrap: !!document.getElementById('bookOtherServiceWrap'),
                intakeDot: !!document.getElementById('intakeHoursDot'),
                dotMention: !!document.querySelector('#overview #intakeHoursText'),
                engineName: typeof runLocalKnowledgeEngine === 'function',
                greeting: txt(document.querySelector('#aiChatHistoryContainer div:last-child')),
                greetingHasPrice: /قیمت/.test(txt(document.querySelector('#aiChatHistoryContainer'))),
                themeLast: (() => { const kids = [...document.querySelector('header > div').children]
                        .flatMap(k => k.tagName === 'DIV' ? [...k.children] : [k]);
                    const ctrls = kids.filter(e => e.matches('button,div') && vis(e));
                    let last = ctrls[ctrls.length - 1];
                    if (last && last.id === 'themeControl') last = last.querySelector('#themeToggleBtn');
                    return last ? (last.id || last.tagName) : ''; })()
            };
        }""")
        check(r3["nav"] and any("مقایسهٔ حافظه SSD" in t for t in r3["nav"])
              and any("درخواست راهنمایی از راه دور" in t for t in r3["headerAll"])
              and r3["themeLast"] == "themeToggleBtn",
              "R3-01  ناوبری، CTA راهنمایی از راه دور و کنترل تم در ترتیب مورد انتظارند",
              f"nav={r3['nav']} · last={r3['themeLast']}")
        check(not r3["priceNodes"] and r3["priceProps"] == 0,
              "R3-02  مبلغ عددی یا ویژگی قیمتِ تأییدنشده در صفحه/کاتالوگ خدمات درج نشده است",
              f"price-nodes={len(r3['priceNodes'])} priceProps={r3['priceProps']}")
        check(not r3["greetingHasPrice"],
              "R3-03  دستیار هوشمند از ابتدا موضوع قیمت را مطرح نمی‌کند",
              f"greeting=«{r3['greeting'][:44]}…»")

        ai = await pg.evaluate(r"""() => {
            const out = {};
            const run = q => runLocalIntelligentEngine('text', q);
            const asks = a => /یک نشانه بگو/.test(a);
            const diag = a => a.includes('###') && !asks(a);
            let a = run('سیستمم یه مشکلی داره');                       // مبهم → باید بپرسد
            out.vague = { asks: asks(a), chips: document.querySelectorAll('#aiQuickChips button').length };
            a = run('گرافیک');                                          // امتیاز کم ولی جهت‌دار → پرسش با نزدیک‌ترین حدس
            out.hinted = { asks: asks(a), mentions: /گرافیک|آرتیفکت/.test(a), chips: document.querySelectorAll('#aiQuickChips button').length };
            const yes = run('بله');                                     // تأیید حدس همان گفت‌وگو
            out.yes = { diag: diag(yes), head: yes.split('\n')[0].slice(0, 46) };
            run('سیستمم یه مشکلی داره');                                 // گفت‌وگوی تازه → پرسش
            const pick = run('۲');                                      // پاسخ کوتاه عددی
            out.shortAnswer = { diag: diag(pick), head: pick.split('\n')[0].slice(0, 46) };
            const clear = run('لپ‌تاپ من بعد از نیم ساعت بازی داغ می‌کنه و صدای فنش بلند شده');
            out.specific = { diag: diag(clear), head: clear.split('\n')[0].slice(0, 52) };
            const haz = run('آب ریخت روی لپ‌تاپم');
            out.hazard = { warn: haz.includes('اقدام فوری') && haz.includes('روشن نکن') };
            const price = run('هزینه تعمیر چقدره؟ قیمت خدمات چنده؟');
            out.price = { hasMoney: /تومان|ریال/.test(price), hasAmount: /[۰-۹]{3,}/.test(price),
                          head: price.split('\n')[0].slice(0, 40) };
            out.chipsReset = document.querySelectorAll('#aiQuickChips button').length;
            return out;
        }""")
        check(ai["vague"]["asks"] and ai["vague"]["chips"] >= 3,
              "R3-04 الف  ورودی مبهم → دستیار به‌جای حدس زدن پرسش روشنگر با گزینه‌های آماده می‌پرسد",
              f"asks={ai['vague']['asks']} chips={ai['vague']['chips']}")
        check(ai["hinted"]["asks"] and ai["hinted"]["mentions"],
              "R3-04 ب  ورودی جهت‌دار ولی کم‌جزئیات → نزدیک‌ترین احتمال را نشان می‌دهد و می‌پرسد",
              f"asks={ai['hinted']['asks']} names-guess={ai['hinted']['mentions']} chips={ai['hinted']['chips']}")
        check(ai["yes"]["diag"] and ai["shortAnswer"]["diag"] and ai["specific"]["diag"],
              "R3-04 پ  «بله» و پاسخ کوتاه «۲» به همان گفت‌وگو وصل می‌شوند و نشانهٔ دقیق مستقیم تشخیص می‌گیرد",
              f"بله→«{ai['yes']['head']}» · ۲→«{ai['shortAnswer']['head']}» · دقیق→«{ai['specific']['head']}»")
        check(ai["hazard"]["warn"], "R3-04 ت  نشانهٔ خطرناک هشدار ایمنی فوری می‌گیرد")
        check(not ai["price"]["hasMoney"] and not ai["price"]["hasAmount"],
              "R3-04 ث  پاسخ هوش مصنوعی دربارهٔ هزینه، هیچ مبلغی نمی‌سازد",
              f"«{ai['price']['head']}»")
        check(ai["chipsReset"] >= 3, "R3-04 ج  چیپ‌های پیشنهادی بعد از تشخیص به حالت پیش‌فرض برمی‌گردند",
              f"chips={ai['chipsReset']}")

        bk = await pg.evaluate(r"""() => {
            openBookingModal();
            const cards = [...document.querySelectorAll('[id^=serviceCard_]')].filter(e => e.tagName === 'BUTTON').map(e => e.id);
            toggleBookingService('other');                    // انتخاب «سایر خدمات»
            const wrap = document.getElementById('bookOtherServiceWrap');
            const opened = !!wrap && !wrap.classList.contains('hidden');
            [['checkIntakeCharger'], ['checkIntakeBackup'], ['checkIntakePassword']].forEach(([id]) => {
                const c = document.getElementById(id); if (c) c.checked = true;
            });
            document.getElementById('bookNameInput').value = 'آزمون راند ۳';
            document.getElementById('bookPhoneInput').value = '09000000000';
            const before = document.getElementById('bookingStep4').classList.contains('hidden');
            confirmBooking({ preventDefault(){} });           // بدون شرح → باید رد شود
            const blocked = document.getElementById('bookingStep4').classList.contains('hidden');
            document.getElementById('bookOtherServiceInput').value = 'تعویض کیبورد لپ‌تاپ و نصب ویندوز کاری';
            goToBookingStep(3);
            const otherRow = document.getElementById('bookSummaryOtherRow');
            const rowVisible = otherRow && !otherRow.classList.contains('hidden');
            const rowText = (document.getElementById('bookSummaryOtherText') || {}).textContent || '';
            confirmBooking({ preventDefault(){} });           // با شرح → ثبت
            const code = document.getElementById('bookSuccessCode').textContent.trim();
            const t = JSON.parse(localStorage.getItem('poshtiban_tickets') || '{}')[code] || {};
            closeBookingModal();
            return { cards, opened, blocked, wasOnStep3: before, rowVisible, rowText, code,
                     ticketOther: t.otherService || '', services: t.services || [] };
        }""")
        check(len(bk["cards"]) == 5 and "serviceCard_other" in bk["cards"] and bk["opened"],
              "R3-05 الف  گزینهٔ «سایر خدمات» با فیلد توضیح باز می‌شود",
              f"cards={bk['cards']} opened={bk['opened']}")
        check(bk["blocked"] and not bk["wasOnStep3"] is None and bk["rowVisible"]
              and bk["rowText"].startswith("تعویض کیبورد")
              and bk["ticketOther"].startswith("تعویض کیبورد")
              and "other" in bk["services"],
              "R3-05 ب  بدون شرح رد می‌شود؛ با شرح، در خلاصه و در تیکت ثبت می‌شود",
              f"blocked={bk['blocked']} summary=«{bk['rowText'][:32]}» ticket=«{bk['ticketOther'][:32]}» code={bk['code']}")
        check(not r3["intakeDot"] and r3["dotMention"],
              "R3-06  نقطهٔ زمان‌بندیِ محلی حذف است و برچسب خنثیِ پذیرش حضوری باقی می‌ماند",
              f"dot={r3['intakeDot']} text={r3['dotMention']}")

        # ---------- R3-07…R3-10: credits — rules frozen for v1 (grace, pause, cap, phone) ----------
        guard_inactivity = await pg.evaluate(r"""() => {
            const body = document.body.innerText;
            // کامنت‌های توضیحی (که خودشان این قاعده را شرح می‌دهند) کنار گذاشته می‌شوند؛
            // فقط کد اجراشدنی و متن دیده‌شدنی باید پاک باشند.
            const js = document.documentElement.innerHTML
                .replace(/\/\/[^\n]*/g, '')          // کامنت تک‌خطی JS
                .replace(/\/\*[\s\S]*?\*\//g, '');  // کامنت چندخطی JS
            const words = ['بی‌فعالیتی', 'بی‌فعال', 'عدم فعالیت', 'بی‌حرکتی'];
            return { text: words.filter(w => body.includes(w)),
                     script: words.filter(w => js.includes(w)),
                     ruleKeys: Object.keys(CREDITS).filter(k => /inactiv|idle/i.test(k)) };
        }""")
        check(not guard_inactivity["text"] and not guard_inactivity["script"] and not guard_inactivity["ruleKeys"],
              "R3-09 ث  نگهبان نسخهٔ ۱: هیچ توقف خودکار بر پایهٔ بی‌فعالیتی نه در کد و نه در متن سایت نیست",
              f"متن={guard_inactivity['text']} · کد={guard_inactivity['script']} · کلیدهای تنظیمات={guard_inactivity['ruleKeys']}")

        cr = await pg.evaluate(r"""() => {
            const out = {};
            localStorage.removeItem('poshtiban_credits');
            localStorage.removeItem('poshtiban_last_phone');
            localStorage.removeItem('poshtiban_tickets');
            resetCreditDemo();
            topUpCredits('p2');                       // ۳۰۰ اعتبار
            out.rules = { grace: CREDITS.setupGraceSeconds, capDefault: CREDITS.sessionCapDefault,
                          inactivity: typeof CREDITS.inactivityStopMinutes };
            const A = '09000000000', B = '09000000001';

            // Browser-only request with synthetic phone A → local allowance record.
            openRemoteModal();
            document.getElementById('remoteNameInput').value = 'آزمون A';
            document.getElementById('remotePhoneInput').value = A;
            document.getElementById('remoteConsentCheck').checked = true;
            handleRemoteSubmit({ preventDefault(){} });
            const codeA = document.getElementById('remoteSuccessCode').textContent.trim();
            closeRemoteModal();
            out.grantA = { known: creditFreeRemaining(A).known, left: creditFreeRemaining(A).left,
                           regrant: creditGrantFreeHour(A), lastPhone: localStorage.getItem('poshtiban_last_phone') };

            const jump = (mins) => { window.__creditNowOverride = creditSession.startedAt + mins * 60000; };

            // Session 1: 45 simulated minutes; 43 minutes recorded against the local allowance.
            startChargeSession(codeA, A);
            jump(45);
            out.free = stopChargeSession('user');

            // Session 2: 90 simulated minutes → 17 allowance minutes + 71 local units.
            startChargeSession(codeA, A);
            jump(90); tickChargeSession();
            out.second = stopChargeSession('user');

            // Session 3: this test number has no local allowance remaining.
            startChargeSession(codeA, A);
            jump(5);
            out.third = stopChargeSession('user');

            // Synthetic number B receives its separate local allowance record.
            openRemoteModal();
            document.getElementById('remoteNameInput').value = 'آزمون B';
            document.getElementById('remotePhoneInput').value = B;
            document.getElementById('remoteConsentCheck').checked = true;
            handleRemoteSubmit({ preventDefault(){} });
            const codeB = document.getElementById('remoteSuccessCode').textContent.trim();
            closeRemoteModal();
            startChargeSession(codeB, B);
            jump(20);
            out.otherPhone = stopChargeSession('user');
            out.balanceAfter = creditState().balance;
            out.grants = Object.keys(creditState().grants).length;

            // مهلت راه‌اندازی: در دقیقهٔ اول هیچ محاسبه‌ای انجام نمی‌شود
            startChargeSession(codeB, B);
            jump(1); tickChargeSession();
            out.grace = { phase: creditPhase(creditSession), burned: computeCharge(creditBillableMs(creditSession) / 60000, creditSession.freeLeft, creditSession.phone).cost };
            jump(3); tickChargeSession();
            out.afterGrace = { phase: creditPhase(creditSession), minutes: computeCharge(creditBillableMs(creditSession) / 60000, creditSession.freeLeft, creditSession.phone).minutes };
            stopChargeSession('user');

            // توقف موقت کارشناس: زمان توقف محاسبه نمی‌شود
            startChargeSession(codeA, A);
            jump(10); pauseChargeSession();                 // توقف
            out.pausedPhase = creditPhase(creditSession);
            jump(40); pauseChargeSession();                 // ادامه پس از ۳۰ دقیقه
            jump(45);
            out.paused = stopChargeSession('user');

            // سقف مصرف جلسه: با سقف ۶۰ اعتبار، جلسه در همان سقف بسته می‌شود
            const stCap = creditState(); stCap.balance = 300; creditSave(stCap);
            startChargeSession(codeA, A, 60);
            jump(120); tickChargeSession();
            const stoppedAtCap = !creditSession;
            const afterCap = creditState();
            const capSession = afterCap.sessions[0];
            out.cap = { stopped: stoppedAtCap, reason: capSession.reason, cost: capSession.cost,
                        cap: capSession.cap, balance: afterCap.balance };

            // اعتبار صفر → جلسه خودکار بسته می‌شود، بدون بدهی
            const stZero = creditState(); stZero.balance = 0; stZero.freeByPhone[A] = 0; creditSave(stZero);
            startChargeSession(codeA, A, 120);
            jump(5); tickChargeSession();
            out.autoStop = { stopped: !creditSession, balance: creditState().balance };

            delete window.__creditNowOverride;
            return out;
        }""")
        check(cr["rules"]["grace"] == 120 and cr["rules"]["capDefault"] == 120 and cr["rules"]["inactivity"] == "undefined",
              "R3-09 الف  قواعد داخلی شبیه‌ساز: مهلت محلی ۲ دقیقه، سقف پیش‌فرض ۱۲۰ واحد، بدون توقف خودکار بر پایهٔ بی‌فعالیتی",
              f"grace={cr['rules']['grace']}s · cap={cr['rules']['capDefault']} · inactivity-rule={cr['rules']['inactivity']}")
        check(cr["grace"]["phase"] == "grace" and cr["grace"]["burned"] == 0 and cr["afterGrace"]["phase"] == "billing"
              and cr["afterGrace"]["minutes"] == 1,
              "R3-09 ب  شمارندهٔ محلی: دقیقهٔ اول در سهمیه/واحدها محاسبه نمی‌شود و از دقیقهٔ سوم شروع می‌شود",
              f"دقیقهٔ ۱: {cr['grace']['phase']} (هزینه {cr['grace']['burned']}) · دقیقهٔ ۳: {cr['afterGrace']['phase']} ({cr['afterGrace']['minutes']} دقیقه)")
        check(cr["pausedPhase"] == "paused" and cr["paused"]["minutes"] == 13 and cr["paused"]["pausedMinutes"] == 30
              and cr["paused"]["cost"] == 13,
              "R3-09 پ  توقف موقتِ شبیه‌ساز: ۳۰ دقیقه از شمارندهٔ محلی کسر نمی‌شود (۴۵ دقیقهٔ آزمون → ۱۳ دقیقه محاسبه)",
              f"فاز={cr['pausedPhase']} محاسبه={cr['paused']['minutes']}د توقف={cr['paused']['pausedMinutes']}د هزینه={cr['paused']['cost']}")
        check(cr["cap"]["stopped"] and cr["cap"]["reason"] == "cap" and cr["cap"]["cost"] == 60
              and cr["cap"]["cap"] == 60 and cr["cap"]["balance"] == 240,
              "R3-09 ت  سقف محلی جلسه رعایت می‌شود: با سقف ۶۰ واحد، شبیه‌سازی در همان‌جا متوقف می‌شود",
              f"reason={cr['cap']['reason']} مصرف={cr['cap']['cost']} از سقف {cr['cap']['cap']} · مانده={cr['cap']['balance']}")
        check(cr["grantA"]["known"] and cr["grantA"]["left"] == 60 and cr["grantA"]["regrant"] is False
              and cr["grantA"]["lastPhone"] == "09" + "0" * 9,
              "R3-07 الف  سهمیهٔ آغازین محلی به شمارهٔ آزمایشی نخست متصل می‌شود و دوباره ثبت نمی‌شود",
              f"known={cr['grantA']['known']} left={cr['grantA']['left']} regrant={cr['grantA']['regrant']}")
        check(cr["free"]["totalMinutes"] == 45 and cr["free"]["minutes"] == 43 and cr["free"]["freeMinutes"] == 43
              and cr["free"]["cost"] == 0 and cr["free"]["freeMinutesLeft"] == 17,
              "R3-07 ب  آزمون ۴۵ دقیقه‌ای پس از راه‌اندازی، زمان را از سهمیهٔ محلی کم می‌کند و پرداختی بیرونی ندارد",
              f"کل={cr['free']['totalMinutes']}د محاسبه={cr['free']['minutes']}د سهمیهٔ محلی={cr['free']['freeMinutes']}د مانده={cr['free']['freeMinutesLeft']}د")
        check(cr["second"]["freeMinutes"] == 17 and cr["second"]["chargedMinutes"] == 71
              and cr["second"]["cost"] == 71 and cr["second"]["balanceAfter"] == 229,
              "R3-07 پ  آزمون بعدی همان شماره: ۱۷ دقیقه سهمیهٔ محلی باقی می‌ماند و سپس واحدهای محلی کم می‌شوند",
              f"۹۰د: سهمیهٔ محلی={cr['second']['freeMinutes']}د واحدهای محلی={cr['second']['chargedMinutes']} مانده={cr['second']['balanceAfter']}")
        check(cr["third"]["freeMinutes"] == 0 and cr["third"]["chargedMinutes"] == 3 and cr["third"]["cost"] == 3,
              "R3-08 الف  سهمیهٔ آغازین فقط یک بار برای هر شمارهٔ آزمایشی ثبت می‌شود؛ آزمون سوم از واحدهای محلی استفاده می‌کند",
              f"۵د: سهمیهٔ محلی={cr['third']['freeMinutes']}د واحدهای محلی={cr['third']['chargedMinutes']}")
        check(cr["otherPhone"]["freeMinutes"] == 18 and cr["otherPhone"]["cost"] == 0
              and cr["otherPhone"]["freeMinutesLeft"] == 42 and cr["grants"] == 2 and cr["balanceAfter"] == 226,
              "R3-08 ب  شمارهٔ آزمایشیِ دیگر سهمیهٔ محلیِ مستقلی دارد",
              f"شمارهٔ B ۲۰د: سهمیهٔ محلی={cr['otherPhone']['freeMinutes']}د مانده={cr['otherPhone']['freeMinutesLeft']}د · شماره‌ها={cr['grants']} · کیف={cr['balanceAfter']}")
        check(cr["autoStop"]["stopped"] and cr["autoStop"]["balance"] == 0,
              "R3-07 ت  با صفرشدن واحدهای محلی، شبیه‌ساز خودکار متوقف می‌شود و مانده منفی نمی‌شود",
              f"auto-stopped={cr['autoStop']['stopped']} balance={cr['autoStop']['balance']}")

        cr_ui = await pg.evaluate(r"""() => {
            localStorage.removeItem('poshtiban_credits');
            localStorage.removeItem('poshtiban_last_phone');
            resetCreditDemo();
            topUpCredits('p2');
            creditGrantFreeHour('09000000000');
            creditGrantFreeHour('09000000000');
            const seed = creditState(); seed.freeByPhone['09000000000'] = 12; creditSave(seed);
            openWalletModal();
            const open = !document.getElementById('walletModal').classList.contains('hidden');
            const packs = document.querySelectorAll('#walletPacks button').length;
            const packsText = document.getElementById('walletPacks').textContent;
            const intro = document.getElementById('walletModal').textContent;
            const freeRows = document.querySelectorAll('#walletFreeList > div').length;
            const mask = document.getElementById('walletFreeList').textContent;
            const panelText = document.getElementById('walletModal').textContent;
            closeWalletModal();
            // چیپ اعتبار با شمارهٔ تایپ‌شده
            openRemoteModal();
            document.getElementById('remotePhoneInput').value = '09000000000'; updateRemoteCreditChip();
            const chipUsed = document.getElementById('remoteCreditNote').textContent.trim();
            document.getElementById('remotePhoneInput').value = '09000000001'; updateRemoteCreditChip();
            const chipFresh = document.getElementById('remoteCreditNote').textContent.trim();
            document.getElementById('remotePhoneInput').value = ''; updateRemoteCreditChip();
            const chipEmpty = document.getElementById('remoteCreditNote').textContent.trim();
            // انتخاب سقف مصرف و شروع جلسه از نمای موفقیت
            const caps = document.querySelectorAll('#sessionCapChoices button').length;
            chooseSessionCap(300);
            const capChosen = document.querySelector('#sessionCapChoices button[aria-pressed="true"]').textContent.trim();
            document.getElementById('remoteNameInput').value = 'آزمون UI';
            document.getElementById('remotePhoneInput').value = '09000000000';
            document.getElementById('remoteConsentCheck').checked = true;
            handleRemoteSubmit({ preventDefault(){} });
            startSessionFromSuccess();
            const barVisible = !document.getElementById('creditSessionBar').classList.contains('hidden');
            const barPhase = document.getElementById('creditSessionPhase').textContent.trim();
            const barBurn = document.getElementById('creditSessionBurn').textContent.trim();
            window.__creditNowOverride = creditSession.startedAt + 5 * 60000;
            tickChargeSession();
            const summary = stopChargeSession('user');
            delete window.__creditNowOverride;
            const st = creditState();
            closeRemoteModal();
            openTrackingModalWithCode(summary.code);
            const row = document.getElementById('trackCreditsRow');
            const rowShown = row && !row.classList.contains('hidden');
            const rowText = (document.getElementById('trackCreditsText') || {}).textContent || '';
            closeTrackingModal();
            return { open, packs, packsText, intro, freeRows, mask: mask.slice(0, 60), barVisible, barPhase, barBurn,
                     caps, capChosen, chipUsed, chipFresh, chipEmpty, rowShown, rowText,
                     money: /تومان|ریال/.test(panelText), capOnSession: summary.cap,
                     maskedStored: (st.sessions[0] || {}).phoneMasked || '', afterFreeLeft: st.freeByPhone['09000000000'] };
        }""")
        check(cr_ui["open"] and cr_ui["packs"] == 3 and "واحد محلی" in cr_ui["packsText"]
              and "اعلام نشده" in cr_ui["packsText"]
              and "قیمت یا پرداختی از این صفحه انجام نمی‌شود" in cr_ui["packsText"]
              and not any(term in cr_ui["packsText"] for term in ("تا ۱ ساعت", "تا ۵ ساعت", "تا ۱۵ ساعت"))
              and not cr_ui["money"],
              "R3-10 الف  گزینه‌های اعتبار با واحد محلی و بدون قیمت/مدت خدمتِ ادعاشده نمایش داده می‌شوند",
              f"packs={cr_ui['packs']} · money={cr_ui['money']} · labels=«{cr_ui['packsText'][:72]}»")
        check("هزینه و شرایط استفاده اعلام نشده است" in cr_ui["intro"]
              and "منطق محلی همین صفحه" in cr_ui["intro"]
              and "این صفحه پرداخت یا خدمت بیرونی انجام نمی‌دهد" in cr_ui["intro"],
              "R3-10 ب  متن کیف پول، سهمیه را منطق محلی معرفی می‌کند و خدمت/پرداخت بیرونی را وعده نمی‌دهد",
              f"«{cr_ui['intro'][:90]}…»")
        check(cr_ui["caps"] == 3 and "۳۰۰" in cr_ui["capChosen"] and cr_ui["capOnSession"] == 300,
              "R3-10 پ  سقفِ واحدهای محلی انتخاب‌شده روی همان شبیه‌سازی اعمال می‌شود",
              f"گزینه‌ها={cr_ui['caps']} انتخاب=«{cr_ui['capChosen']}» سقف محلی={cr_ui['capOnSession']}")
        check(cr_ui["barVisible"] and "محلی" in cr_ui["barPhase"] and "سقف" in cr_ui["barBurn"]
              and cr_ui["rowShown"] and "واحد محلی" in cr_ui["rowText"] and "***" in cr_ui["maskedStored"],
              "R3-10 ت  نوار شمارنده و سقف محلی را نشان می‌دهد و خلاصهٔ شبیه‌سازی در تیکت ذخیره می‌شود",
              f"bar=«{cr_ui['barPhase']}» · «{cr_ui['barBurn'][:26]}» · ticket=«{cr_ui['rowText'][:44]}»")
        check("۱۲ دقیقه" in cr_ui["chipUsed"] and "اعتبار محلی" in cr_ui["chipUsed"]
              and "اعلام نشده" in cr_ui["chipUsed"]
              and "اعتبار محلی برای این شماره ثبت نشده است" in cr_ui["chipFresh"]
              and "هزینه و شرایط استفاده اعلام نشده" in cr_ui["chipEmpty"],
              "R3-10 ث  چیپ اعتبار، سهمیهٔ محلی ثبت‌شده/ثبت‌نشده و متن خنثیِ شرایط را نشان می‌دهد",
              f"شمارهٔ ثبت‌شده: «{cr_ui['chipUsed'][:44]}» · شمارهٔ تازه: «{cr_ui['chipFresh'][:44]}» · خالی: «{cr_ui['chipEmpty'][:34]}»")

        # ---------- R3-11…R3-15: local credit-simulator behavior; public terms remain undisclosed ----------
        cx = await pg.evaluate(r"""() => {
            const out = {};
            out.cfg = { expiry: CREDITS.expiryMonths, dispute: CREDITS.disputeWindowHours,
                        low: CREDITS.lowBalanceMinutes, drop: CREDITS.workshopDropGraceSeconds,
                        care: CREDITS.careMonthlyCredits };
            // ۱) انقضای ۱۲ ماهه + برچسب شمسی
            out.expiryLabel = creditJalaliLabel(creditExpiryAt(new Date('2026-10-06T10:00:00Z').getTime()));
            out.expiryExpected = `${creditFa(14)} مهر ${creditFa(1406)}`;
            out.nowLabel = creditJalaliLabel(new Date('2026-10-06T10:00:00Z').getTime());

            localStorage.removeItem('poshtiban_credits');
            localStorage.removeItem('poshtiban_last_phone');
            localStorage.removeItem('poshtiban_tickets');
            resetCreditDemo();
            topUpCredits('p1');
            out.walletExpiry = {
              note: (document.getElementById('walletExpiryNote') || {}).textContent || '',
              label: creditExpiryInfo().label, lots: creditState().lots.length,
              // انتظارِ «امروز-مستقل»: همان برچسبی که از زمان واقعیِ آخرین شارژ درمی‌آید
              expected: creditJalaliLabel(creditExpiryAt(new Date(creditState().lots[0].at).getTime()))
            };
            const stExp = creditState();
            stExp.lots = [{ at: new Date(Date.now() - 400 * 24 * 3600 * 1000).toISOString(), credits: 60, left: 60, pack: 'qadimi' }];
            stExp.balance = 60; creditSave(stExp);
            out.swept = creditSweepExpired();
            out.afterSweep = { balance: creditState().balance, note: (creditState().history[0] || {}).note || '' };

            // Test number whose local allowance has been partly used.
            const spend = (phone) => {
              const st = creditState();
              st.grants[phone] = st.grants[phone] || new Date().toISOString();
              st.freeByPhone[phone] = 0; creditSave(st);
            };
            const jump = (mins) => { window.__creditNowOverride = creditSession.startedAt + mins * 60000; };
            const remoteCode = (phone) => {
              openRemoteModal();
              document.getElementById('remoteNameInput').value = 'آزمون';
              document.getElementById('remotePhoneInput').value = phone;
              document.getElementById('remoteConsentCheck').checked = true;
              handleRemoteSubmit({ preventDefault(){} });
              const code = document.getElementById('remoteSuccessCode').textContent.trim();
              return code;
            };

            // ۵) local pause simulation in the browser-only session counter
            const A = '09000000000';
            spend(A); chooseSessionCap(120);
            const balSeed = creditState(); balSeed.balance = 300; creditSave(balSeed);
            const codeA = remoteCode(A);
            startSessionFromSuccess();
            jump(10); tickChargeSession();
            const beforeDrop = computeCharge(creditBillableMs(creditSession) / 60000, creditSession.freeLeft, creditSession.phone).minutes;
            toggleWorkshopDrop();
            jump(12); tickChargeSession();
            const duringDrop = computeCharge(creditBillableMs(creditSession) / 60000, creditSession.freeLeft, creditSession.phone).minutes;
            out.drop = { before: beforeDrop, during: duringDrop,
                         phaseShort: document.getElementById('creditSessionPhase').textContent.trim(),
                         btn: document.getElementById('creditSessionDropBtn').textContent.trim() };
            jump(16); tickChargeSession();
            out.drop.phaseLong = document.getElementById('creditSessionPhase').textContent.trim();
            toggleWorkshopDrop();
            out.drop.phaseBack = document.getElementById('creditSessionPhase').textContent.trim();
            jump(21); tickChargeSession();
            const sumDrop = stopChargeSession('user');

            // ۴) اعلان کم‌موجودی
            const stLow = creditState(); stLow.balance = 20; creditSave(stLow);
            const codeB = remoteCode(A);
            startSessionFromSuccess();
            jump(4); tickChargeSession();
            const alertEl = document.getElementById('creditSessionAlert');
            out.low = { early: !alertEl.classList.contains('hidden'), earlyRemaining: document.getElementById('creditSessionAlertText').textContent.trim() };
            jump(22); tickChargeSession();
            out.low.late = !alertEl.classList.contains('hidden');
            out.low.text = document.getElementById('creditSessionAlertText').textContent.trim();
            out.low.topup = (alertEl.querySelector('button') || {}).getAttribute ? alertEl.querySelector('button').getAttribute('onclick') : '';
            const sumLow = stopChargeSession('user');

            // ۲) local simulator note-window behavior; not a published review term
            openTrackingModalWithCode(sumDrop.code);
            const dRow = document.getElementById('trackDisputeRow');
            out.dispute = {
              rowVisible: !dRow.classList.contains('hidden'),
              status: document.getElementById('trackDisputeStatus').textContent.trim(),
              btnVisible: !document.getElementById('trackDisputeBtn').classList.contains('hidden')
            };
            toggleDisputeForm();
            document.getElementById('trackDisputeReason').value = 'مشکل حل نشد و دستگاه هنوز همان خطا را می‌دهد.';
            const rec = submitCreditDispute();
            out.dispute.record = rec && { code: rec.code, status: rec.status, reason: rec.reason };
            out.dispute.statusAfter = document.getElementById('trackDisputeStatus').textContent.trim();
            out.dispute.btnHiddenAfter = document.getElementById('trackDisputeBtn').classList.contains('hidden');
            out.dispute.shortReasonRejected = (() => {
              const st = creditState(); const before = st.disputes.length;
              document.getElementById('trackDisputeReason').value = 'ا';
              const r = submitCreditDispute();
              return r === null && creditState().disputes.length === before;
            })();
            closeTrackingModal();
            // پنجرهٔ گذشته
            const stStale = creditState();
            const idx = stStale.sessions.findIndex(x => x.code === sumDrop.code);
            stStale.sessions[idx].endedAt = new Date(Date.now() - 50 * 3600 * 1000).toISOString();
            stStale.disputes = []; creditSave(stStale);
            out.dispute.staleWithinWindow = creditDisputeState(sumDrop.code).withinWindow;
            renderTrackDispute(sumDrop.code);
            out.dispute.staleStatus = document.getElementById('trackDisputeStatus').textContent.trim();
            out.dispute.staleBtnHidden = document.getElementById('trackDisputeBtn').classList.contains('hidden');

            // ۳) اعتبار ماهانهٔ طرح‌های Care
            const plans = document.getElementById('plans').innerText;
            out.care = { undisclosed: (plans.match(/میزان و شرایط اعتبار اعلام نشده/g) || []).length,
                         unlimited: /نامحدود/.test(plans),
                         wallet: (document.getElementById('walletCareNote') || {}).textContent || '' };

            delete window.__creditNowOverride;
            return out;
        }""")
        check(cx["cfg"]["expiry"] == 12 and cx["cfg"]["dispute"] == 48 and cx["cfg"]["low"] == 5
              and cx["cfg"]["drop"] == 180 and cx["cfg"]["care"] == [300, 900, 3000],
              "R3-11 الف  قواعد شبیه‌ساز محلی حفظ‌اند؛ این آستانه‌ها به‌عنوان شرایط خدمتِ واقعی ارائه نمی‌شوند",
              f"local expiry={cx['cfg']['expiry']} · note window={cx['cfg']['dispute']} · alert={cx['cfg']['low']} · pause={cx['cfg']['drop']} · units={cx['cfg']['care']}")
        check(cx["expiryLabel"] == cx["expiryExpected"] and cx["nowLabel"] != cx["expiryLabel"]
              and "اعلام نشده" in cx["walletExpiry"]["note"] and "۱۲ ماه" not in cx["walletExpiry"]["note"]
              and cx["walletExpiry"]["label"] == cx["walletExpiry"]["expected"]
              and cx["walletExpiry"]["lots"] == 1,
              "R3-11 ب  محاسبهٔ تاریخ در دادهٔ محلی درست است و متن کیف پول شرایط مدت را اعلام‌نشده می‌گذارد",
              f"تابع → «{cx['expiryLabel']}» · متن کیف=«{cx['walletExpiry']['note']}» · مقدار=«{cx['walletExpiry']['label']}»")
        check(cx["swept"] == 60 and cx["afterSweep"]["balance"] == 0 and "انقضای اعتبار" in cx["afterSweep"]["note"],
              "R3-11 پ  ماندهٔ منقضیِ شبیه‌ساز محلی پاک و در گردش مرورگر ثبت می‌شود",
              f"سوخته={cx['swept']} اعتبار · مانده={cx['afterSweep']['balance']} · «{cx['afterSweep']['note'][:44]}…»")
        check(cx["drop"]["before"] == 8 and cx["drop"]["during"] == 8
              and "وقفهٔ محلی ثبت شده است" in cx["drop"]["phaseShort"]
              and cx["drop"]["btn"] == "اتصال برگشت"
              and "وقفهٔ محلی ثبت شده است" in cx["drop"]["phaseLong"]
              and cx["drop"]["phaseBack"] == "محاسبهٔ محلی در حال اجراست",
              "R3-15  وقفهٔ شبیه‌ساز محلی از شمارنده کنار گذاشته می‌شود؛ رابط ادعای اتصال/پاسخ کارشناس نمی‌کند",
              f"قبل/داخل={cx['drop']['before']}/{cx['drop']['during']} · «{cx['drop']['phaseShort']}» · «{cx['drop']['phaseBack']}»")
        check(cx["low"]["early"] is False and cx["low"]["late"] is True and "تا اتمام اعتبار" in cx["low"]["text"]
              and cx["low"]["topup"] == "openWalletModal()",
              "R3-14  هشدار داخلیِ مانده در آستانهٔ تعیین‌شده ظاهر می‌شود و فقط کیف محلی را باز می‌کند",
              f"زودتر: {cx['low']['early']} («{cx['low']['earlyRemaining']}») · در آستانه: {cx['low']['late']} («{cx['low']['text']}»)")
        check(cx["dispute"]["rowVisible"] and cx["dispute"]["btnVisible"]
              and "اعلام نشده" in cx["dispute"]["status"]
              and cx["dispute"]["record"] and cx["dispute"]["record"]["status"] == "open"
              and "یادداشت محلی ذخیره شده است" in cx["dispute"]["statusAfter"]
              and "بررسی بیرونی متصل نیست" in cx["dispute"]["statusAfter"]
              and cx["dispute"]["btnHiddenAfter"] and cx["dispute"]["shortReasonRejected"],
              "R3-12 الف  فرم یادداشت محلی، شرایط بررسی نامشخص، اعتبارسنجی شرح و ذخیرهٔ مرورگری را پوشش می‌دهد",
              f"وضعیت=«{cx['dispute']['statusAfter'][:52]}» · شرح کوتاه رد شد={cx['dispute']['shortReasonRejected']}")
        check(cx["dispute"]["staleWithinWindow"] is False and "اعلام نشده" in cx["dispute"]["staleStatus"]
              and cx["dispute"]["staleBtnHidden"],
              "R3-12 ب  پنجرهٔ داخلیِ شبیه‌ساز پس از مهلت بسته می‌شود؛ رابط شرایط زمانی را اعلام‌نشده می‌گذارد",
              f"پنجرهٔ داخلی باز={cx['dispute']['staleWithinWindow']} · «{cx['dispute']['staleStatus']}»")
        check(cx["care"]["undisclosed"] == 3 and cx["care"]["unlimited"] is False
              and "اعلام نشده" in cx["care"]["wallet"],
              "R3-13  هر سه کارت طرح، مقدار/شرایط را اعلام‌نشده می‌گذارند و ادعای «نامحدود» ندارند",
              f"کارت‌های خنثی={cx['care']['undisclosed']} · «نامحدود»={cx['care']['unlimited']} · کیف=«{cx['care']['wallet'][:64]}»")

        # ---------- R2-09: the header bar must fit its own container at every width ----------
        # (round 2 follow-up: the bar is max-w-6xl = 1104px of content, but its items summed to
        #  ~1346px, so from 1024px up the CTA and «رزرو حضوری» were pushed off-screen)
        widths = [1920, 1600, 1440, 1366, 1280, 1180, 1100, 1024, 960, 834, 768, 640, 430, 390, 360, 320]
        sweep_bad, sweep_seen = [], {}
        for w in widths:
            await pg.set_viewport_size({"width": w, "height": 880})
            await pg.wait_for_timeout(220)
            row = await pg.evaluate(r"""() => {
                const bar = document.querySelector('header > div');
                const kids = [...bar.children].flatMap(k => k.tagName === 'DIV' ? [...k.children] : [k]);
                const clipped = kids.filter(e => e.getBoundingClientRect().width > 0)
                                    .filter(e => { const r = e.getBoundingClientRect();
                                                   return r.x < -1 || r.right > innerWidth + 1; })
                                    .map(e => (e.textContent || e.tagName).replace(/\s+/g, ' ').trim().slice(0, 18));
                const vis = el => { const r = el.getBoundingClientRect(); return r.width > 0; };
                const cta = document.querySelector('header button[onclick="openRemoteModal()"]:not(#liveWorkStatusBadge)');
                const navEl = document.querySelector('header nav');
                const ctrls = kids.filter(e => e.matches('button,div') && e.getBoundingClientRect().width > 0);
                let last = ctrls[ctrls.length - 1];
                if (last && last.id === 'themeControl') last = last.querySelector('#themeToggleBtn');
                return { overflow: bar.scrollWidth - bar.clientWidth, clipped,
                         docOverflow: document.documentElement.scrollWidth - innerWidth,
                         ctaVisible: !!cta && vis(cta),
                         menuVisible: vis(document.querySelector('header button[aria-label="منوی موبایل"]')),
                         navVisible: !!navEl && vis(navEl),
                         lastControl: last ? (last.id || last.tagName) : '(none)' };
            }""")
            sweep_seen[w] = row
            nav_ok = row["navVisible"] if w >= 1024 else row["menuVisible"]
            last_ok = row["lastControl"] == "themeToggleBtn"
            if (row["overflow"] > 1 or row["clipped"] or row["docOverflow"] > 1 or not row["ctaVisible"]
                    or not nav_ok or not last_ok):
                sweep_bad.append(f"{w}px overflow={row['overflow']} clipped={row['clipped'][:2]} cta={row['ctaVisible']} "
                                 f"menu={row['menuVisible']} nav={row['navVisible']} last={row['lastControl']}")
        await pg.set_viewport_size({"width": 1440, "height": 900})
        await pg.wait_for_timeout(250)
        check(not sweep_bad,
              "R2-09  نوار هدر در ۱۶ عرض (۳۲۰ تا ۱۹۲۰px) درون ظرف خود جا می‌شود، CTA و دکمهٔ منو دیده می‌شوند و «حالت شب» آخرین کنترل است",
              "; ".join(sweep_bad) if sweep_bad else "بررسی‌شده: " + ", ".join(str(w) for w in widths))

        # ---------- F-16: آیکون‌های خطی SVG به‌جای ایموجی + الآن‌رپ قیمت طرح‌ها ----------
        f16 = await pg.evaluate(r"""() => {
            const EMOJI = /[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{2699}\u{26A0}\u{26D4}\u{23F3}\u{200D}]/u;
            const ALLOW = new Set(['✓', '✕', '✦', '→', '←', '⇒']);
            const iconEmoji = [...document.querySelectorAll('body *')]
                .filter(e => !e.children.length)
                .map(e => (e.textContent || '').trim())
                .filter(t => t && t.length <= 3 && EMOJI.test(t) && !ALLOW.has(t));
            const uses = [...document.querySelectorAll('svg use')].map(u => (u.getAttribute('href') || '').slice(1));
            const broken = uses.filter(id => !document.getElementById(id));
            const themeIcon = document.getElementById('themeToggleIcon');
            setThemeMode('dark');
            const dark = { icon: themeIcon.getAttribute('data-theme-icon'),
                           use: (themeIcon.querySelector('use') || {}).getAttribute
                                ? themeIcon.querySelector('use').getAttribute('href') : '',
                           svg: !!themeIcon.querySelector('svg'),
                           persisted: localStorage.getItem('poshtiban_theme'),
                           selected: document.querySelector('#themeModeMenu [data-theme-mode="dark"]').getAttribute('aria-pressed') };
            setThemeMode('light');
            const light = { icon: themeIcon.getAttribute('data-theme-icon'), persisted: localStorage.getItem('poshtiban_theme'),
                            selected: document.querySelector('#mobileThemeControl [data-theme-mode="light"]').getAttribute('aria-pressed') };
            setThemeMode('auto');
            const auto = { mode: localStorage.getItem('poshtiban_theme'),
                           selectedDesktop: document.querySelector('#themeModeMenu [data-theme-mode="auto"]').getAttribute('aria-pressed'),
                           selectedMobile: document.querySelector('#mobileThemeControl [data-theme-mode="auto"]').getAttribute('aria-pressed') };
            return { iconEmoji: [...new Set(iconEmoji)], uses: uses.length, broken: [...new Set(broken)], dark, light, auto,
                     svgCount: document.querySelectorAll('svg[viewBox="0 0 24 24"]').length,
                     symbols: document.querySelectorAll('symbol[id^="ic-"]').length };
        }""")
        check(not f16["iconEmoji"] and not f16["broken"] and f16["uses"] >= 18 and f16["symbols"] >= 14
              and f16["svgCount"] >= 18,
              "F-16 الف  هیچ ایموجی‌ای به‌عنوان آیکون رابط نمانده — همه با آیکون‌های خطی SVG جایگزین شدند",
              f"ایموجی‌های باقی‌مانده={f16['iconEmoji']} · ارجاع‌های آیکون={f16['uses']} · شکسته={f16['broken']} · نمادها={f16['symbols']}")
        check(f16["dark"]["icon"] == "sun" and f16["dark"]["svg"] and f16["dark"]["use"] == "#ic-sun"
              and f16["dark"]["persisted"] == "dark" and f16["dark"]["selected"] == "true"
              and f16["light"]["icon"] == "moon" and f16["light"]["persisted"] == "light"
              and f16["light"]["selected"] == "true" and f16["auto"]["mode"] == "auto"
              and f16["auto"]["selectedDesktop"] == "true" and f16["auto"]["selectedMobile"] == "true",
              "F-16 ب  آیکون SVG با تم روشن/تیره همگام است؛ هر سه انتخاب تم از هدر و موبایل پایدار و همگام می‌شوند",
              f"تیره={f16['dark']['icon']} ({f16['dark']['use']}) ذخیره={f16['dark']['persisted']} · روشن={f16['light']['icon']} ذخیره={f16['light']['persisted']} · خودکار={f16['auto']['mode']}")
        await pg.set_viewport_size({"width": 390, "height": 844})
        await pg.wait_for_timeout(300)
        f16p = await pg.evaluate(r"""() => [...document.querySelectorAll('#plans .font-mono')].map(blk => {
            const unit = blk.querySelector('span');
            const b = blk.getBoundingClientRect(), u = unit.getBoundingClientRect();
            return { txt: blk.textContent.replace(/\s+/g, ' ').trim().slice(0, 28),
                     sameLine: Math.abs((u.top + u.height / 2) - (b.top + b.height / 2)) < 8,
                     ws: getComputedStyle(blk).whiteSpace, h: Math.round(b.height) };
        })""")
        await pg.set_viewport_size({"width": 1440, "height": 900})
        await pg.wait_for_timeout(200)
        check(len(f16p) == 3 and all(x["sameLine"] and x["ws"] == "nowrap" and x["h"] <= 40 for x in f16p),
              "F-16 پ  در ۳۹۰px سطر اطلاعاتِ مقدار/هزینهٔ اعلام‌نشدهٔ سه گزینه نمی‌شکند",
              " · ".join(f"«{x['txt']}» h={x['h']}px" for x in f16p))

        # F-17: Persian text must not be rendered with a mono stack (it has no Persian glyphs
        # and the per-glyph fallback breaks letter joining)
        mono_fa = await pg.evaluate(r"""() => {
            const fa = /[\u0600-\u06FF]/;
            return [...document.querySelectorAll('*')]
              .filter(e => !e.children.length && fa.test(e.textContent)
                           && /mono/i.test(getComputedStyle(e).fontFamily))
              .map(e => ({txt: e.textContent.replace(/\s+/g, ' ').trim().slice(0, 22),
                          ff: getComputedStyle(e).fontFamily.slice(0, 30)}));
        }""")
        check(not mono_fa, "F-17  متن فارسی با فونت مونو رندر نمی‌شود (اتصال حروف حفظ شود)",
              f"offenders={len(mono_fa)}" + (f" · {mono_fa[:2]}" if mono_fa else ""))
        # F-15: negative letter-spacing must not touch pure-Persian text (it breaks letter joins)
        ls_bad = await pg.evaluate("""() => {
            const fa = /[\u0600-\u06FF]/;
            return [...document.querySelectorAll('h1, h2, h3, h4, span, b, strong, p, a, button, div')]
              .filter(e => !e.children.length && fa.test(e.textContent) && !/[A-Za-z]/.test(e.textContent))
              .map(e => ({txt: e.textContent.trim().slice(0, 20), ls: getComputedStyle(e).letterSpacing}))
              .filter(o => o.ls !== 'normal' && parseFloat(o.ls) !== 0);
        }""")
        check(not ls_bad, "F-15  فاصلهٔ حرفی متن فارسی عادی است (tracking فقط برای لاتین)",
              f"offenders={len(ls_bad)}" + (f" · {ls_bad[:3]}" if ls_bad else ""))
        # ---------- DESIGN-STEP1 (D-01 · D-02 · D-03 · D-05): لایهٔ جلای طراحی ----------
        # توجه: همهٔ اندازه‌گیری‌های بالا در حالت «کاهش حرکت» انجام می‌شود (وضعیت پایدار)؛
        # این بخش خودش مدیا را موقتاً عوض می‌کند تا رفتار هر دو حالت را بسنجد.
        amb = await pg.evaluate("""() => {
            const s = document.getElementById('overview');
            const a = getComputedStyle(s, '::before'), c = getComputedStyle(s, '::after');
            return { pos: getComputedStyle(s).position, aBg: a.backgroundImage, cBg: c.backgroundImage,
                     aPe: a.pointerEvents, aFilter: a.filter };
        }""")
        check(amb["pos"] == "relative" and "radial-gradient" in amb["aBg"] and "radial-gradient" in amb["cBg"]
              and amb["aPe"] == "none" and amb["aFilter"] in ("none", ""),
              "D-01  پرتو محیطی هیرو فعال است (گرادیان نرم، بدون filter، غیرقابل‌کلیک)",
              f"pos={amb['pos']} pe={amb['aPe']} filter={amb['aFilter']}")

        seams = await pg.evaluate("""() => ['ai-diagnostic','bottleneck','faq'].map(id => {
            const el = document.getElementById(id);
            const t = getComputedStyle(el, '::before');
            return { id, bg: t.backgroundImage, h: t.height };
        })""")
        check(all("linear-gradient" in x["bg"] and x["h"] not in ("auto", "0px") for x in seams),
              "D-05  درز گرادیانی بالای باندهای خاکستری فعال است",
              " · ".join(f"{x['id']}:{x['h']}" for x in seams))

        # D-02 — در حالت «حرکت مجاز» پنهان می‌شود و با اسکرول یک‌بار نمایان؛ در «کاهش حرکت» همیشه نمایان.
        await pg.emulate_media(reduced_motion="no-preference")
        await pg.reload(wait_until="load")
        await pg.wait_for_timeout(350)
        pre = await pg.evaluate("""() => {
            const el = document.querySelector('#plans .rise');
            return { js: document.documentElement.classList.contains('js'),
                     has: !!el, op: el ? parseFloat(getComputedStyle(el).opacity) : -1 };
        }""")
        await pg.evaluate("document.getElementById('plans').scrollIntoView({ block: 'center' })")
        try:
            await pg.wait_for_function(
                "() => { const el = document.querySelector('#plans .rise'); "
                "return el && el.classList.contains('in') && parseFloat(getComputedStyle(el).opacity) > 0.9; }",
                timeout=6000)
            revealed, detail = True, "پنهان پیش از اسکرول → نمایان پس از اسکرول"
        except Exception as exc:   # noqa: BLE001
            revealed, detail = False, f"نمایان نشد: {type(exc).__name__}"
        post = await pg.evaluate("() => { const el = document.querySelector('#plans .rise'); return el ? parseFloat(getComputedStyle(el).opacity) : -1; }")
        check(pre["js"] and pre["has"] and pre["op"] < 0.5 and revealed and post > 0.9,
              "D-02  ورود نرم اسکرولی: پنهانِ اولیه → نمایانِ یک‌باره با اسکرول",
              f"js={pre['js']} opacity پیش={pre['op']} پس={post:.2f} · {detail}")

        await pg.emulate_media(reduced_motion="reduce")
        await pg.reload(wait_until="load")
        await pg.wait_for_timeout(250)
        rm = await pg.evaluate("""() => {
            const el = document.querySelector('#plans .rise');
            return { js: document.documentElement.classList.contains('js'),
                     op: el ? parseFloat(getComputedStyle(el).opacity) : -1 };
        }""")
        check((not rm["js"]) and rm["op"] > 0.9,
              "D-02ب  کاهش حرکت: هیچ محتوایی پنهان نمی‌شود (بدون کلاس js، شفافیت کامل)",
              f"js={rm['js']} opacity={rm['op']}")

        # ---------- DESIGN-STEP2 (D-04 · D-08 · D-09 · D-10) ----------
        # D-04 — هالهٔ گوشهٔ دو کارت (background-image رادیال، بدون شبه‌عنصر)
        halo = await pg.evaluate("""() => {
            const cs = el => getComputedStyle(el);
            const diag = document.getElementById('aiTextDiagnosticCard');
            const pro  = document.querySelector('#plans .grid > div:nth-child(2)');
            return { diag: cs(diag).backgroundImage.includes('radial-gradient'),
                     pro:  cs(pro).backgroundImage.includes('radial-gradient'),
                     diagPos: cs(diag).backgroundPosition, proPos: cs(pro).backgroundPosition };
        }""")
        check(halo["diag"] and halo["pro"],
              "D-04  هالهٔ گوشهٔ کارت‌ها فعال است (عیب‌یاب، Care Pro)",
              f"عیب‌یاب={halo['diag']} ({halo['diagPos']}) · Pro={halo['pro']} ({halo['proPos']})")

        # D-09 — the legacy local flag still controls indicator styling; this is not evidence of actual availability.
        dots = await pg.evaluate("""() => {
            const keep = REMOTE_SUPPORT.manualOverride;
            const snap = id => { const el = document.getElementById(id); return el ? el.className : ''; };
            const ids = ['shopHoursStatusDot', 'remoteSectionDot', 'drawerPresenceDot'];
            REMOTE_SUPPORT.manualOverride = 'offline'; renderPresence();
            const off = ids.map(snap);
            REMOTE_SUPPORT.manualOverride = 'online';  renderPresence();
            const on  = ids.map(snap);
            REMOTE_SUPPORT.manualOverride = keep;      renderPresence();
            return { off, on };
        }""")
        off_ok = all(('amber' in c) and ('animate-pulse' not in c) for c in dots["off"])
        on_ok  = all(('emerald' in c) and ('animate-pulse' in c) for c in dots["on"])
        check(off_ok and on_ok,
              "D-09  سبک نشانگر از پرچم محلی تبعیت می‌کند (کهربایی/سبز)؛ متن وضعیت ادعای دسترسی نمی‌کند",
              f"offline={[('amber' in c, 'pulse' in c) for c in dots['off']]} · online={[('emerald' in c, 'pulse' in c) for c in dots['on']]}")
        # Source-level guard: static amber/gray indicators must not carry a pulse class.
        src_dots = SOURCE_HTML.read_text(encoding="utf-8")
        bad_dots = [c for c in re.findall(r'class="([^"]*animate-(?:pulse|ping)[^"]*)"', src_dots)
                    if any(t in c for t in ("amber", "neutral", "gray", "slate", "zinc"))]
        check(not bad_dots, "D-09  نشانگرهای ثابت کهربایی/خاکستری پالس ندارند (قاعدهٔ سراسری)", 
              f"offenders={len(bad_dots)}")


        # D-03 — کارت‌ها فقط در دسکتاپ با اشاره‌گر دقیق بلند می‌شوند
        await pg.emulate_media(reduced_motion="no-preference")
        await pg.reload(wait_until="load")
        await pg.wait_for_timeout(250)
        card = pg.locator("#plans .grid > div").first
        await card.scroll_into_view_if_needed()
        await pg.wait_for_timeout(450)
        await card.hover()
        await pg.wait_for_timeout(450)
        ty = await card.evaluate("""el => { const t = getComputedStyle(el).translate;
            if (!t || t === 'none') return 0;
            const parts = t.split(' ');
            return parseFloat(parts.length > 1 ? parts[1] : parts[0]) || 0; }""")
        check(ty <= -2.0, "D-03  بلندشدن کارت در هاور (۴px — فقط دسکتاپ با اشاره‌گر دقیق)",
              f"translateY={ty:.2f}px")

        # D-04 هاور — هاله بازتر می‌شود (background-size بزرگ‌تر)
        pro = pg.locator("#plans .grid > div").nth(1)
        await pro.scroll_into_view_if_needed(); await pg.wait_for_timeout(700)
        size_before = await pro.evaluate("el => parseFloat(getComputedStyle(el).backgroundSize)")
        await pro.hover(); await pg.wait_for_timeout(600)
        size_after = await pro.evaluate("el => parseFloat(getComputedStyle(el).backgroundSize)")
        check(size_after > size_before + 10,
              "D-04  هالهٔ کارت در هاور بازتر می‌شود (بدون پرش)",
              f"background-size {size_before:.0f}% → {size_after:.0f}%")

        # D-10 — زبان واحد دکمه‌های اصلی: هاور ≈۱٫۰۲
        # پوشش از روی «خودِ سلکتورِ استایل‌شیت» سنجیده می‌شود (نه یک سلکتور موازیِ تست):
        # اگر سلکتور قاعده ترکیب‌کنندهٔ فرزند داشته باشد یا شرطی روی خودِ دکمه برقرار نباشد،
        # هم scale عوض نمی‌شود و هم شمارش پوشش سقوط می‌کند. (بازگشتِ باگ سلکتورِ فرزندی — گام ۲ب)
        btn = pg.locator("#aiAnalyzeBtn")
        await btn.scroll_into_view_if_needed(); await pg.wait_for_timeout(900)
        cov = await pg.evaluate(r"""() => {
            const hit = r => r.style && r.style.transform && String(r.style.transform).includes('scale(1.02)');
            let sel = null;
            // نکته: در کرومیوم جدید، CSSStyleRule.cssRules یک فهرست خالیِ truthy است (پشتیبانی از nesting)
            // پس اول باید خودِ قاعده بررسی شود و بازگشت فقط با .length انجام شود.
            const scan = rules => { for (const r of rules) {
                if (r.selectorText && hit(r)) sel = r.selectorText;
                if (r.cssRules && r.cssRules.length) scan(r.cssRules); } };
            for (const sh of document.styleSheets) { let rs; try { rs = sh.cssRules; } catch (e) { continue; } scan(rs); }
            if (!sel) return { count: -1, nonCta: -1, sel: '' };
            const base = sel.replace(':hover', '').replace(':active', '');
            const els = [...document.querySelectorAll(base)];
            return { count: els.length,
                     nonCta: els.filter(e => !/^(A|BUTTON)$/.test(e.tagName)).length,
                     sel: base.slice(0, 80) };
        }""")
        mcount = cov["count"]
        before = await btn.evaluate("el => new DOMMatrixReadOnly(getComputedStyle(el).transform).a")
        await btn.hover(); await pg.wait_for_timeout(450)
        after = await btn.evaluate("el => new DOMMatrixReadOnly(getComputedStyle(el).transform).a")
        tr = await btn.evaluate("el => getComputedStyle(el).transitionProperty")
        check(after >= 1.018 and before <= 1.001 and mcount >= 8 and cov["nonCta"] == 0 and "transform" in tr,
              "D-10  دکمه‌های اصلی زبان واحد دارند (هاور ≈۱٫۰۲ — سلکتورِ خود قاعده، شامل دکمه‌های ساختهٔ JS)",
              f"scale {before:.3f}→{after:.3f} · زیر پوشش={mcount} · همه دکمه/لینک={cov['nonCta'] == 0} · گذار شامل transform={'transform' in tr}")

        # D-08 — نوارهای سنجش از صفر پر می‌شوند و تعامل بعدی دست‌نخورده است
        await pg.reload(wait_until="load"); await pg.wait_for_timeout(500)
        bar0 = await pg.evaluate("() => new DOMMatrixReadOnly(getComputedStyle(document.getElementById('benchBootBar')).transform).a")
        await pg.evaluate("document.getElementById('speed-booster').scrollIntoView({block:'center'})")
        await pg.wait_for_timeout(1500)
        bar1 = await pg.evaluate("() => new DOMMatrixReadOnly(getComputedStyle(document.getElementById('benchBootBar')).transform).a")
        await pg.click("#benchBtnHdd"); await pg.wait_for_timeout(800)
        hdd = await pg.evaluate("""() => { const b = document.getElementById('benchBootBar');
            return { w: b.getBoundingClientRect().width / b.parentElement.getBoundingClientRect().width,
                     tr: new DOMMatrixReadOnly(getComputedStyle(b).transform).a }; }""")
        check(bar0 <= 0.02 and bar1 >= 0.98 and 0.10 <= hdd["w"] <= 0.20 and hdd["tr"] >= 0.98,
              "D-08  نوارهای سنجش: صفر پیش از دیدن → پر پس از ورود؛ تغییر HDD هنوز کار می‌کند",
              f"مقیاس {bar0:.2f}→{bar1:.2f} · پس از HDD پهنای {hdd['w']*100:.0f}٪ (مقیاس {hdd['tr']:.2f})")
        await pg.click("#benchBtnNvme"); await pg.wait_for_timeout(400)

        # ---------- DESIGN-STEP3 (تصویر + ضربان زنده — «زنده‌شدن» صفحه) ----------
        # فضای آزمون اینجاست: حرکت روشن است (D-03/D-08 بالاتر آن را روشن کردند)
        # S3-01 — صحنهٔ هیرو: تصویرِ واقعاً رمزگشایی‌شده (نه جای‌گذار)، با alt و چیپ‌ها
        scene = await pg.evaluate("""() => {
            const st = document.getElementById('alHeroStage');
            const im = st && st.querySelector('img.al-shot');
            const r = im ? im.getBoundingClientRect() : null;
            return { has: !!st, src: im ? (im.getAttribute('src') || '').slice(0, 22) : '',
                     nat: im ? im.naturalWidth : 0, alt: im ? (im.getAttribute('alt') || '') : '',
                     w: r ? Math.round(r.width) : 0, h: r ? Math.round(r.height) : 0,
                     chips: st ? st.querySelectorAll('.al-chip').length : 0,
                     floats: st ? st.querySelectorAll('.al-float').length : 0,
                     drift: st ? st.querySelectorAll('.al-drift').length : 0 };
        }""")
        check(scene["has"] and scene["src"].startswith("data:image/webp") and scene["nat"] > 0
              and len(scene["alt"]) > 20 and scene["w"] > 600 and scene["h"] > 200
              and scene["chips"] == 2 and scene["floats"] == 2 and scene["drift"] >= 3,
              "S3-01  صحنهٔ هیرو: تصویر جاسازی‌شدهٔ رمزگشایی‌شده + ۲ چیپ + ۲ پنل زنده + عناصر شناور",
              f"src={scene['src']}… nat={scene['nat']}px · کادر {scene['w']}×{scene['h']} · چیپ={scene['chips']} پنل={scene['floats']} شناور={scene['drift']}")

        # S3-02 — the local-clock widget updates over time and uses Persian digits.
        t1 = await pg.evaluate("() => (document.getElementById('alClock') || {}).textContent || ''")
        await pg.wait_for_timeout(1500)
        t2 = await pg.evaluate("() => (document.getElementById('alClock') || {}).textContent || ''")
        check(bool(t1) and bool(t2) and t1 != t2 and bool(re.search(r"[۰-۹]", t1)) and bool(re.search(r"[۰-۹]", t2)),
              "S3-02  ساعت نمایشی به‌روز می‌شود و از رقم‌های فارسی استفاده می‌کند",
              f"«{t1}» → «{t2}»")

        # S3-03 — exercise the legacy local flag while ensuring the displayed status stays neutral.
        live = await pg.evaluate("""() => {
            const d = document.getElementById('alLiveDot'), t = document.getElementById('alLiveText');
            const keep = REMOTE_SUPPORT.manualOverride;
            REMOTE_SUPPORT.manualOverride = 'offline'; renderPresence();
            const off = { cls: d.className, st: d.dataset.state, tx: t.textContent };
            REMOTE_SUPPORT.manualOverride = 'online';  renderPresence();
            const on  = { cls: d.className, st: d.dataset.state, tx: t.textContent };
            REMOTE_SUPPORT.manualOverride = keep;      renderPresence();
            return { off, on };
        }""")
        check(live["off"]["st"] == "queue" and "amber" in live["off"]["cls"]
              and "pulse" not in live["off"]["cls"] and "اعلام نشده" in live["off"]["tx"]
              and live["on"]["st"] == "online" and "emerald" in live["on"]["cls"]
              and "pulse" in live["on"]["cls"] and "اعلام نشده" in live["on"]["tx"],
              "S3-03  پرچم داخلی سبک نقطه را عوض می‌کند، اما متن وضعیت در هر دو حالت خنثی می‌ماند",
              f"off: {live['off']['st']} «{live['off']['tx'][:34]}» · local-on: {live['on']['st']} «{live['on']['tx'][:34]}»")

        # S3-04 — شمارندهٔ اعداد: مقدار میانی دیده می‌شود و مقدار نهایی درست می‌نشیند
        await pg.reload(wait_until="load"); await pg.wait_for_timeout(120)
        await pg.evaluate("document.getElementById('speed-booster').scrollIntoView({block:'center'})")
        mids = []
        for _ in range(2):
            await pg.wait_for_timeout(230)
            mids.append(await pg.evaluate("() => document.getElementById('benchBootTime').textContent.trim()"))
        await pg.wait_for_timeout(1500)
        end = await pg.evaluate("() => document.getElementById('benchBootTime').textContent.trim()")
        check((any(m != end for m in mids)) and end.startswith("۷") and "ثانیه" in end,
              "S3-04  شمارندهٔ اعداد با اولین دیدن سکشن اجرا می‌شود و به عدد درست می‌نشیند",
              f"میانی={mids} · نهایی=«{end}»")

        # S3-05 — همهٔ تصاویر صفحه جاسازی‌شده‌اند، alt دارند و از بیرون نمی‌آیند + چهار باند
        imgs = await pg.evaluate("""() => {
            const all = [...document.querySelectorAll('img')].filter(i => (i.getAttribute('src') || '').trim() !== '');
            return { total: all.length,
                     b64: all.filter(i => (i.getAttribute('src') || '').startsWith('data:image/')).length,
                     noAlt: all.filter(i => !(i.getAttribute('alt') || '').trim()).length,
                     external: all.filter(i => /^(https?:)?\\/\\//.test(i.getAttribute('src') || '')).length,
                     bands: document.querySelectorAll('.al-band').length,
                     bandShots: [...document.querySelectorAll('.al-band img.al-band-shot')]
                                    .filter(i => i.naturalWidth > 0).length };
        }""")
        # (تصویرهای بدون src — مثل پیش‌نمایش آپلود عیب‌یاب تصویری — طبیعتاً شمرده نمی‌شوند)
        check(imgs["total"] >= 5 and imgs["b64"] == imgs["total"] and imgs["noAlt"] == 0
              and imgs["external"] == 0 and imgs["bands"] == 4 and imgs["bandShots"] == 4,
              "S3-05  تصاویرِ صفحه: همه جاسازی‌شده (base64)، همه با alt، صفر منبع بیرونی؛ چهار باند تصویری",
              f"تصاویر={imgs['total']} base64={imgs['b64']} بی‌alt={imgs['noAlt']} بیرونی={imgs['external']} · باند={imgs['bands']} سالم={imgs['bandShots']}")

        # S3-06 — کاهش حرکت: ضربان‌ها خاموش‌اند و صحنه کامل دیده می‌شود
        await pg.emulate_media(reduced_motion="reduce")
        await pg.reload(wait_until="load"); await pg.wait_for_timeout(350)
        rm3 = await pg.evaluate("""() => {
            const d = document.querySelector('.al-drift');
            const a = getComputedStyle(document.getElementById('overview'), '::before');
            const st = document.getElementById('alHeroStage');
            return { drift: d ? getComputedStyle(d).animationName : '(none)',
                     aurora: a.animationName,
                     op: parseFloat(getComputedStyle(st).opacity),
                     nat: st.querySelector('img.al-shot').naturalWidth };
        }""")
        check(rm3["drift"] in ("none", "") and rm3["aurora"] in ("none", "") and rm3["op"] > .9 and rm3["nat"] > 0,
              "S3-06  با «کاهش حرکت» هیچ ضربانی اجرا نمی‌شود ولی صحنه و تصویر کامل دیده می‌شوند",
              f"شناور={rm3['drift']} · پرتو={rm3['aurora']} · شفافیت صحنه={rm3['op']:.2f} · nat={rm3['nat']}")

        # S3-07 — پارالاکس ملایم: فقط دسکتاپِ اشاره‌گر دقیق، جابه‌جایی کوچک، و بازگشت با خروج ماوس
        await pg.emulate_media(reduced_motion="no-preference")
        await pg.reload(wait_until="load"); await pg.wait_for_timeout(400)
        stage_loc = pg.locator("#alHeroStage")
        await stage_loc.scroll_into_view_if_needed(); await pg.wait_for_timeout(600)
        box = await stage_loc.bounding_box()
        await pg.mouse.move(box["x"] + box["width"] * .22, box["y"] + box["height"] * .30)
        await pg.wait_for_timeout(300)
        moved = await pg.evaluate("() => [...document.querySelectorAll('#alHeroStage [data-al-depth]')].map(e => e.style.translate || '')")
        await pg.mouse.move(box["x"] + box["width"] + 60, box["y"] + box["height"] + 60)
        await pg.wait_for_timeout(300)
        rested = await pg.evaluate("() => [...document.querySelectorAll('#alHeroStage [data-al-depth]')].map(e => e.style.translate || '')")
        mags = []
        for t in moved:
            part = (t.split(" ")[0] or "0").replace("px", "")
            try:
                mags.append(abs(float(part)))
            except ValueError:
                mags.append(0.0)
        check(any(m > 0.4 for m in mags) and max(mags) <= 10 and all(r == "" for r in rested),
              "S3-07  پارالاکس ملایم هیرو (≤۱۰px، فقط دسکتاپِ اشاره‌گر دقیق) و بازگشت کامل با خروج ماوس",
              f"جابه‌جایی={[round(m, 1) for m in mags]} · پس از خروج={rested}")

        # S3-08 — نگهبان: هیچ جای‌گذار باقی‌مانده و هیچ تصویر بیرونی در منبع
        src3 = SOURCE_HTML.read_text(encoding="utf-8")
        placeholders = re.findall(r"(?<![A-Za-z_])(__[A-Z]+__)", src3)
        data_imgs = src3.count("data:image/webp;base64,")
        http_imgs = len(re.findall(r'<img[^>]+src="https?://', src3))
        check(not placeholders and data_imgs == 5 and http_imgs == 0,
              "S3-08  منبع تمیز است: بدون جای‌گذار باقی‌مانده، ۵ تصویر جاسازی‌شده، صفر تصویر بیرونی",
              f"جای‌گذار={placeholders} · جاسازی‌شده={data_imgs} · بیرونی={http_imgs}")

        # ---------- DESIGN-STEP4: زمان محلی، نور/شیشهٔ مشترک، حذف خطوط جداکننده ----------
        # S4-01 — chooser هر سه حالت را در هدر و drawer موبایل عرضه می‌کند و aria را همگام نگه می‌دارد.
        await pg.evaluate("setThemeMode('auto')")
        chooser = await pg.evaluate("""() => ({
            desktop: [...document.querySelectorAll('#themeModeMenu [data-theme-mode]')].map(e => e.dataset.themeMode),
            mobile: [...document.querySelectorAll('#mobileThemeControl [data-theme-mode]')].map(e => e.dataset.themeMode),
            trigger: !!document.querySelector('#themeToggleBtn[aria-controls="themeModeMenu"][aria-haspopup="dialog"]'),
            popupRole: document.querySelector('#themeModeMenu')?.getAttribute('role') === 'dialog',
            mobileGroup: document.querySelector('#mobileThemeControl')?.getAttribute('role') === 'group',
            pressed: [...document.querySelectorAll('[data-theme-mode="auto"]')].every(e => e.getAttribute('aria-pressed') === 'true')
        })""")
        check(chooser["desktop"] == ["auto", "light", "dark"] and chooser["mobile"] == ["auto", "light", "dark"]
              and chooser["trigger"] and chooser["popupRole"] and chooser["mobileGroup"] and chooser["pressed"],
              "S4-01  تم‌گزین هدر/موبایل سه انتخاب روشن/تیره/خودکار دارد و حالت انتخاب‌شدهٔ ARIA را همگام می‌کند",
              f"desktop={chooser['desktop']} mobile={chooser['mobile']} aria={chooser['pressed']}")

        # S4-02 — اجرای محلیِ طلوع/غروب: mock موقعیتِ تهران/آمستردام فقط در حافظه؛ بدون ذخیرهٔ مختصات.
        # باز-بارگذاری، درخواست مکان را از مسیر واقعی auto اجرا می‌کند؛ پاسخ مرورگر در این تست شبیه‌سازی شده است.
        await pg.add_init_script("""Object.defineProperty(Navigator.prototype, 'geolocation', {
          configurable: true, value: { getCurrentPosition(ok) { ok({coords:{latitude:52.3676,longitude:4.9041}}); } }
        });""")
        await pg.evaluate("localStorage.setItem('poshtiban_theme','auto')")
        await pg.reload(wait_until="load"); await pg.wait_for_timeout(350)
        sun = await pg.evaluate("""() => {
            const now = new Date(2026, 5, 21, 12, 0, 0);
            const rise = solarEventLocalMinutes(now, 52.3676, 4.9041, true);
            const set = solarEventLocalMinutes(now, 52.3676, 4.9041, false);
            const NativeDate = window.Date;
            const at = mins => {
              const hh = Math.floor(mins / 60), mm = mins % 60;
              window.Date = class extends NativeDate {
                constructor(...args) { if (args.length) super(...args); else super(2026, 5, 21, hh, mm, 0); }
                static now() { return new NativeDate(2026, 5, 21, hh, mm, 0).getTime(); }
              };
              return isNightByThemeRule('auto');
            };
            const nightBefore = at((rise.minutes + 1439) % 1440);
            const dayAfterRise = at((rise.minutes + 10) % 1440);
            const nightAfterSet = at((set.minutes + 10) % 1440);
            window.Date = NativeDate;
            const polarDay = solarEventLocalMinutes(new NativeDate(2026, 5, 21, 12), 80, 0, true).polar;
            const polarNight = solarEventLocalMinutes(new NativeDate(2026, 11, 21, 12), 80, 0, true).polar;
            const stored = Object.keys(localStorage).filter(k => /lat|lon|coord|location/i.test(k));
            const hint = document.getElementById('themeModeHint')?.textContent || '';
            return { rise: rise.minutes, set: set.minutes, nightBefore, dayAfterRise, nightAfterSet,
                     polarDay, polarNight, stored, ready: hint.includes('موقعیت دستگاه') };
        }""")
        check(sun["ready"] and sun["rise"] is not None and sun["set"] is not None
              and sun["nightBefore"] and not sun["dayAfterRise"] and sun["nightAfterSet"]
              and sun["polarDay"] == "day" and sun["polarNight"] == "night" and not sun["stored"],
              "S4-02  طلوع/غروب با موقعیتِ موقت و ساعت محلی محاسبه می‌شود؛ قطب‌ها درست‌اند و مختصات ذخیره نمی‌شود",
              f"طلوع={sun['rise']}د غروب={sun['set']}د · قبل/بعد طلوع/بعد غروب={[sun['nightBefore'],sun['dayAfterRise'],sun['nightAfterSet']]} · قطب={sun['polarDay']}/{sun['polarNight']} · ذخیره={sun['stored']}")

        # S4-03 — انتخاب دستی بر auto/time اولویت دارد و با refresh پایدار می‌ماند.
        await pg.evaluate("setThemeMode('dark')")
        await pg.reload(wait_until="load"); await pg.wait_for_timeout(220)
        persisted_dark = await pg.evaluate("({mode:localStorage.getItem('poshtiban_theme'),dark:document.documentElement.classList.contains('dark'),selected:document.querySelector('#themeModeMenu [data-theme-mode=dark]').getAttribute('aria-pressed')})")
        await pg.evaluate("setThemeMode('light')")
        await pg.wait_for_timeout(700)  # laisser se terminer la double-RAF de transition de thème
        manual_light = await pg.evaluate("({mode:localStorage.getItem('poshtiban_theme'),dark:document.documentElement.classList.contains('dark'),selected:document.querySelector('#mobileThemeControl [data-theme-mode=light]').getAttribute('aria-pressed')})")
        reopened = await pg.context.new_page()
        await reopened.goto(FILE, wait_until="load"); await reopened.wait_for_timeout(250)
        reopened_light = await reopened.evaluate("({mode:localStorage.getItem('poshtiban_theme'),dark:document.documentElement.classList.contains('dark')})")
        await reopened.close()
        await pg.evaluate("setThemeMode('auto')")
        check(persisted_dark["mode"] == "dark" and persisted_dark["dark"] and persisted_dark["selected"] == "true"
              and manual_light["mode"] == "light" and not manual_light["dark"] and manual_light["selected"] == "true"
              and reopened_light["mode"] == "light" and not reopened_light["dark"],
              "S4-03  تم دستی بر ساعت غالب است و انتخاب روشن/تیره پس از refresh و بازکردن دوبارهٔ صفحه باقی می‌ماند",
              f"پس از refresh تیره={persisted_dark} · دستی روشن={manual_light} · صفحهٔ بازشدهٔ دوباره={reopened_light}")

        # S4-04 — نور واحد آبی/بنفش و کارت شیشه‌ای؛ لبه‌های خاکستری در سکشن‌ها حذف شده‌اند.
        await pg.evaluate("setThemeMode('light')")
        surfaces = await pg.evaluate("""() => {
            const cs=(e,p)=>getComputedStyle(e,p), ai=document.getElementById('ai-diagnostic');
            const card=document.getElementById('aiTextDiagnosticCard'), head=document.getElementById('mainHeader');
            const rgba=cs(card).backgroundColor.match(/[\\d.]+/g)?.map(Number) || [];
            const sections=[...document.querySelectorAll('#main>section')];
            return {modes:[getComputedStyle(document.body,'::before').backgroundImage,getComputedStyle(document.body,'::after').backgroundImage],
                    aiGlass:cs(ai).backgroundColor,aiGlow:[cs(ai,'::before').backgroundImage,cs(ai,'::after').backgroundImage],
                    cardAlpha:rgba.length>3?rgba[3]:1,blur:cs(card).backdropFilter,reflection:cs(card).boxShadow.includes('inset'),
                    cardBorder:cs(card).borderTopColor,headerBlur:cs(head).backdropFilter,
                    sectionBorders:sections.map(e=>[cs(e).borderTopWidth,cs(e).borderBottomWidth]),footerBorder:cs(document.querySelector('footer')).borderTopWidth};
        }""")
        check(all("radial-gradient" in layer for layer in surfaces["modes"])
              and "rgba" in surfaces["aiGlass"] and all("linear-gradient" in g or "radial-gradient" in g for g in surfaces["aiGlow"])
              and surfaces["cardAlpha"] < .8 and "blur" in surfaces["blur"] and surfaces["reflection"]
              and "0, 0, 0" in surfaces["cardBorder"] and "blur" in surfaces["headerBlur"]
              and all(t == ["0px", "0px"] for t in surfaces["sectionBorders"]) and surfaces["footerBorder"] == "0px",
              "S4-04  نور محیطی یکپارچه + کارت شیشه‌ای شفاف/blur/بازتاب + حذف خط‌های خاکستری سکشن و فوتر",
              f"alpha={surfaces['cardAlpha']:.2f} blur={surfaces['blur']} · header={surfaces['headerBlur']} · borders={set(tuple(t) for t in surfaces['sectionBorders'])}/{surfaces['footerBorder']}")

        # S4-05 — گذار تم نرم است؛ reduced-motion آن را بی‌حرکت می‌کند.
        await pg.emulate_media(reduced_motion="no-preference")
        await pg.evaluate("setThemeMode('dark')")
        transition = await pg.evaluate("({active:document.documentElement.classList.contains('theme-transitioning'),duration:getComputedStyle(document.documentElement).transitionDuration})")
        await pg.wait_for_timeout(720)
        cleared = await pg.evaluate("!document.documentElement.classList.contains('theme-transitioning')")
        await pg.emulate_media(reduced_motion="reduce")
        await pg.evaluate("setThemeMode('light')")
        reduced = await pg.evaluate("({active:document.documentElement.classList.contains('theme-transitioning'),dur:getComputedStyle(document.body,'::before').transitionDuration})")
        check(transition["active"] and "0.48s" in transition["duration"] and cleared
              and not reduced["active"] and reduced["dur"] in ("0s", "0s, 0s"),
              "S4-05  تغییر تم با گذار نرم انجام می‌شود؛ prefers-reduced-motion آن را کامل خاموش می‌کند",
              f"گذار={transition} · پاک‌شده={cleared} · کاهش حرکت={reduced}")
        await pg.evaluate("setThemeMode('auto')")

        # S4-06 — when geolocation is denied, theme selection uses the browser-local daytime threshold; manual mode still wins.
        local_ctx = await b.new_context(timezone_id="Europe/Amsterdam", viewport={"width": 390, "height": 844},
                                        reduced_motion="reduce")
        local_pg = await local_ctx.new_page()
        await local_pg.add_init_script("""Object.defineProperty(Navigator.prototype, 'geolocation', {
          configurable: true, value: { getCurrentPosition(ok, fail) { fail({code: 1}); } }
        });""")
        await local_pg.goto(FILE, wait_until="load")
        await local_pg.wait_for_function("themeGeoState === 'denied'")
        fallback = await local_pg.evaluate("""() => {
            const NativeDate = Date, noon = new NativeDate(2026, 5, 21, 12);
            const rise = solarEventLocalMinutes(noon, 52.3676, 4.9041, true);
            const set = solarEventLocalMinutes(noon, 52.3676, 4.9041, false);
            const at = (hour, minute) => {
              const stamp = new NativeDate(2026, 5, 21, hour, minute).valueOf();
              window.Date = class extends NativeDate {
                constructor(...args) { return args.length ? new NativeDate(...args) : new NativeDate(stamp); }
                static now() { return stamp; }
              };
              applyThemePreference(false);
              return {time: `${hour}:${String(minute).padStart(2, '0')}`,
                      dark: document.documentElement.classList.contains('dark')};
            };
            const edges = [[6,59],[7,0],[18,59],[19,0]].map(([h,m]) => at(h,m));
            const manualStamp = new NativeDate(2026, 5, 21, 12).valueOf();
            window.Date = class extends NativeDate {
              constructor(...args) { return args.length ? new NativeDate(...args) : new NativeDate(manualStamp); }
              static now() { return manualStamp; }
            };
            setThemeMode('dark'); applyThemePreference(false);
            const manualDark = document.documentElement.classList.contains('dark');
            window.Date = NativeDate;
            return {offset: noon.getTimezoneOffset(), rise: rise.minutes, set: set.minutes, edges,
                    manualDark, mode: getThemeMode(), geo: themeGeoState, coords: themeGeoCoords};
        }""")
        await local_ctx.close()
        check(fallback["offset"] == -120 and 240 <= fallback["rise"] <= 360 and 1260 <= fallback["set"] <= 1380
              and [x["dark"] for x in fallback["edges"]] == [True, False, False, True]
              and fallback["manualDark"] and fallback["mode"] == "dark"
              and fallback["geo"] == "denied" and fallback["coords"] is None,
              "S4-06  رد مکان‌یابی، آستانهٔ روزانهٔ تم را به ساعت مرورگر ۰۷–۱۹ می‌سپارد؛ انتخاب دستی اولویت دارد",
              f"UTC offset={fallback['offset']} · sunrise/sunset={fallback['rise']}/{fallback['set']}m · edges={fallback['edges']} · denied={fallback['geo']} · manual={fallback['manualDark']}")

        # S4-07 — only outer section seams are removed; calendar, FAQ and control boundaries remain.
        await pg.evaluate("setThemeMode('light'); openBookingModal(); goToBookingStep(2)")
        calendar_divider = await pg.evaluate("""() => {
            const e = document.getElementById('calDaysGrid').previousElementSibling, s = getComputedStyle(e);
            return {width:s.borderBottomWidth, style:s.borderBottomStyle, color:s.borderBottomColor};
        }""")
        await pg.evaluate("closeBookingModal(); (() => {const b=document.querySelector('#faq button'); if(b.getAttribute('aria-expanded')!=='true') toggleFaq(b);})()")
        input = pg.locator("#aiProblemInput")
        await input.focus(); await pg.keyboard.press("Tab"); await pg.keyboard.press("Shift+Tab")
        light_boundary = await pg.evaluate("""() => {
            const css=e=>getComputedStyle(e), input=document.getElementById('aiProblemInput');
            return {section:css(document.getElementById('faq')).borderTopWidth,
              faq:[css(document.getElementById('faqAnswer1')).borderTopWidth,css(document.getElementById('faqAnswer1')).borderTopStyle],
              input:[css(input).borderTopWidth,css(input).borderTopStyle],
              outline:[css(input).outlineWidth,css(input).outlineStyle,css(input).outlineColor],
              focusVisible:input.matches(':focus-visible'),
              drop:[css(document.getElementById('dropZoneArea')).borderTopWidth,css(document.getElementById('dropZoneArea')).borderTopStyle]};
        }""")
        await pg.evaluate("setThemeMode('dark'); document.getElementById('aiProblemInput').blur()")
        await input.focus(); await pg.keyboard.press("Tab"); await pg.keyboard.press("Shift+Tab")
        dark_boundary = await pg.evaluate("""() => {
            const css=e=>getComputedStyle(e), input=document.getElementById('aiProblemInput');
            return {section:css(document.getElementById('faq')).borderTopWidth,
              faq:[css(document.getElementById('faqAnswer1')).borderTopWidth,css(document.getElementById('faqAnswer1')).borderTopStyle],
              input:[css(input).borderTopWidth,css(input).borderTopStyle],
              outline:[css(input).outlineWidth,css(input).outlineStyle,css(input).outlineColor],
              focusVisible:input.matches(':focus-visible'),
              drop:[css(document.getElementById('dropZoneArea')).borderTopWidth,css(document.getElementById('dropZoneArea')).borderTopStyle]};
        }""")
        preserved = (calendar_divider["width"] == "1px" and calendar_divider["style"] == "solid"
                     and all(v["section"] == "0px" and v["faq"] == ["1px", "solid"]
                             and v["input"] == ["1px", "solid"] and v["focusVisible"]
                             and v["outline"][:2] == ["2px", "solid"]
                             and v["drop"] == ["2px", "dashed"]
                             for v in (light_boundary, dark_boundary))
                     and "0, 113, 227" in light_boundary["outline"][2]
                     and "77, 163, 255" in dark_boundary["outline"][2])
        check(preserved,
              "S4-07  مرز سکشن حذف است؛ خط تقویم/FAQ، فوکوس صفحه‌کلید و کادر dashed بارگذاری در هر دو تم حفظ‌اند",
              f"calendar={calendar_divider} · light={light_boundary} · dark={dark_boundary}")

        await pg.emulate_media(reduced_motion="reduce")


        await b.close()

        # ---------- wording guard: reject specific around-the-clock claims, keep neutral disclosures ----------
        src_page = SOURCE_HTML.read_text(encoding="utf-8")
        leftovers = re.findall(r"۲۴/۷|24/7", src_page)
        check(not leftovers, "LANG-01  ادعای مشخص «۲۴/۷» یا «24/7» در متن سایت نیست",
              f"occurrences={len(leftovers)}")
        neutral_status_copy = all(term in src_page for term in (
            "زمان پذیرش حضوری اعلام نشده", "زمان پاسخ‌گویی اعلام نشده", "پوشش خدمات مشخص نشده"))
        check(neutral_status_copy, "LANG-01  متن، ساعت پذیرش/پاسخ‌گویی/پوشش را تأییدنشده اعلام می‌کند",
              f"neutralStatusCopy={neutral_status_copy} · تست ۲۴ ساعتهٔ داخلی حفظ شده: {'تست پایداری حداقل ۲۴ ساعته' in src_page}")

        # ---------- F-14 / F-15: wording + letter-spacing (static/style) ----------
        src = SOURCE_HTML.read_text(encoding="utf-8")
        check("شیفت عصر" not in src, "F-14  «شیفت عصر» → «بعدازظهر»")
        check("خدمت انتخابی" not in src, "F-14  الگوی «N خدمت» بدون «انتخابی»")
    # ---------- report (grouped by package) ----------
    PKG = {"P1": {"F-01", "F-03", "F-04", "F-14", "LANG-01"},
           "POS": {"REMOTE-01", "REMOTE-04"},
           "R2": {"R2-01", "R2-02", "R2-03", "R2-04", "R2-06", "R2-07", "R2-08", "R2-09"},
           "R3": {"R3-01", "R3-02", "R3-03", "R3-04", "R3-05", "R3-06", "R3-07", "R3-08", "R3-09", "R3-10",
                  "R3-11", "R3-12", "R3-13", "R3-14", "R3-15"},
           "P3": {"F-11", "F-12", "F-15", "F-16", "F-17"},
           "GUARD": {"F-02", "D-01", "D-02", "D-03", "D-04", "D-05", "D-08", "D-09", "D-10",
                   "S3-02", "S3-03", "S3-05", "S3-08", "S4-01", "S4-02", "S4-03", "S4-04", "S4-05", "S4-06", "S4-07"},
           "P2": {"F-05", "F-06", "F-07", "F-08", "F-09", "F-10", "F-13"}}
    NAME = {"P1": "بستهٔ ۱ · درست‌کارکرد", "P2": "بستهٔ ۲ · دسترس‌پذیری",
            "P3": "بستهٔ ۳ · موبایل", "POS": "ریموت‌محوری (سیاست جدید)",
            "R2": "راند ۲ · بازخورد فروشگاه", "R3": "راند ۳ · تغییرات جدید",
            "GUARD": "نگهبان‌های رگرسیون"}

    def pkg_of(label):
        m = re.search(r"(D-\d\d|R3-\d\d|R2-\d\d|S3-\d\d|S4-\d\d|REMOTE-\d\d|POS-\d\d|F-\d\d)", label)
        fid = m.group(0) if m else ""
        for k, ids in PKG.items():
            if fid in ids:
                return k
        return "P2"

    groups = {}
    for label in ok + bad:
        groups.setdefault(pkg_of(label), []).append((label in bad, label))

    print("\n" + "=" * 96)
    total_fail = len(bad)
    print(f"  PASS {len(ok)}   FAIL {total_fail}   INFO {len(info)}   (the list below is the to-do list)")
    print("=" * 96)
    for key in ("R3", "R2", "P1", "POS", "P2", "P3", "GUARD"):
        rows = groups.get(key, [])
        if not rows:
            continue
        fails = sum(1 for f, _ in rows if f)
        print(f"\n── {NAME[key]} " + "─" * (70 - len(NAME[key])) + f"  {'✓ all clear' if not fails else f'{fails} remaining'}")
        for is_fail, label in rows:
            print(("  ✗ " if is_fail else "  ✓ ") + label)
    if info:
        print("\n── notes")
        for x in info:
            print("  ·", x)
    print()
    sys.exit(1 if total_fail and any(pkg_of(l) in ("P1", "POS", "GUARD") for l in bad) else 0)

asyncio.run(main())
