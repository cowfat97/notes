import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import articles from "../data/articles";
import diaries from "../data/diaries";
import "./HomePage.css";

const sections = ["about", "articles", "timeline"] as const;

export default function HomePage() {
  const rightRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState("about");
  const [showQR, setShowQR] = useState(false);

  useEffect(() => {
    const el = rightRef.current;
    if (!el) return;
    const handle = () => {
      let current = "about";
      for (const id of sections) {
        const s = document.getElementById(id);
        if (s && s.getBoundingClientRect().top <= 200) current = id;
      }
      setActive(current);
    };
    el.addEventListener("scroll", handle, { passive: true });
    return () => el.removeEventListener("scroll", handle);
  }, []);

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="app">
      {/* ── 左面板 ── */}
      <aside className="left-panel">
        <div className="left-top">
          <p className="hi">你好，我是</p>
          <h1>how</h1>
          <p className="bio">
            <span className="yr">2020 – 2025</span>Java 开发工程师
            <br />
            <span className="yr">2026 –</span>大模型开发工程师
          </p>
        </div>

        <nav className="left-nav">
          {sections.map((id, i) => (
            <a
              key={id}
              href={`#${id}`}
              className={active === id ? "active" : ""}
              onClick={(e) => {
                e.preventDefault();
                scrollTo(id);
              }}
            >
              <span className="num">—</span>{" "}
              {["关于", "文章", "时间线"][i]}
            </a>
          ))}
        </nav>

        <div className="left-bottom">
          <ul className="social-icons">
            <li>
              <a href="https://github.com/cowfat97" target="_blank" rel="noreferrer" title="GitHub">
                <svg xmlns="http://www.w3.org/2000/svg" role="img" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <title>GitHub</title>
                  <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
                </svg>
              </a>
            </li>
            <li>
              <a href="https://space.bilibili.com/235982069" target="_blank" rel="noreferrer" title="B站">
                <svg xmlns="http://www.w3.org/2000/svg" role="img" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <title>Bilibili</title>
                  <path d="M17.813 4.653h.854c1.51.054 2.769.578 3.773 1.574 1.004.995 1.524 2.249 1.56 3.76v7.36c-.036 1.51-.556 2.769-1.56 3.773s-2.262 1.524-3.773 1.56H5.333c-1.51-.036-2.769-.556-3.773-1.56S.036 18.858 0 17.347v-7.36c.036-1.511.556-2.765 1.56-3.76 1.004-.996 2.262-1.52 3.773-1.574h.774l-1.174-1.12a1.234 1.234 0 0 1-.373-.906c0-.356.124-.658.373-.907l.027-.027c.267-.249.573-.373.92-.373.347 0 .653.124.92.373L9.653 4.44c.071.071.134.142.187.213h4.267a.836.836 0 0 1 .16-.213l2.853-2.747c.267-.249.573-.373.92-.373.347 0 .662.151.929.4.267.249.391.551.391.907 0 .355-.124.657-.373.906zM5.333 7.24c-.746.018-1.373.276-1.88.773-.506.498-.769 1.13-.786 1.894v7.52c.017.764.28 1.395.786 1.893.507.498 1.134.756 1.88.773h13.334c.746-.017 1.373-.275 1.88-.773.506-.498.769-1.129.786-1.893v-7.52c-.017-.765-.28-1.396-.786-1.894-.507-.497-1.134-.755-1.88-.773zM8 11.107c.373 0 .684.124.933.373.25.249.383.569.4.96v1.173c-.017.391-.15.711-.4.96-.249.25-.56.374-.933.374s-.684-.125-.933-.374c-.25-.249-.383-.569-.4-.96V12.44c0-.373.129-.689.386-.947.258-.257.574-.386.947-.386zm8 0c.373 0 .684.124.933.373.25.249.383.569.4.96v1.173c-.017.391-.15.711-.4.96-.249.25-.56.374-.933.374s-.684-.125-.933-.374c-.25-.249-.383-.569-.4-.96V12.44c.017-.391.15-.711.4-.96.249-.249.56-.373.933-.373Z" />
                </svg>
              </a>
            </li>
            <li>
              <a href="#" onClick={(e) => { e.preventDefault(); setShowQR(true); }} title="公众号">
                <svg xmlns="http://www.w3.org/2000/svg" role="img" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <title>WeChat</title>
                  <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89c-.135-.01-.27-.027-.407-.03zm-2.53 3.274c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.97-.982zm4.844 0c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.969-.982z" />
                </svg>
              </a>
            </li>
            <li>
              <a href="mailto:biohow@163.com" title="邮箱">
                <svg xmlns="http://www.w3.org/2000/svg" role="img" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <title>邮箱</title>
                  <path d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L5.455 4.64 12 9.548l6.545-4.91 1.528-1.145C21.69 2.28 24 3.434 24 5.457z" />
                </svg>
              </a>
            </li>
          </ul>
        </div>
      </aside>

      {/* ── 右面板 ── */}
      <main className="right-panel" ref={rightRef}>
        <section id="about">
          <h2 className="numbered-heading">关于我</h2>
          <p>Java 后端开发 5 年，Spring Cloud 微服务体系。2025 年底离职转大模型方向。</p>
          <p>目前在系统学习 LLM 技术栈：RAG、Agent、LangChain、微调等。同时在写 AI 行业分析文章，也在 B 站录制相关视频。</p>
          <p>也在准备 408 考研，目标苏州大学非全日制。</p>
          <ul className="skill-list">
            <li>Java / Spring Cloud</li>
            <li>Python / PyTorch</li>
            <li>LangChain / LangGraph</li>
            <li>RAG / Agent</li>
            <li>MySQL / Redis / Kafka</li>
            <li>Docker</li>
          </ul>
        </section>

        <section id="articles">
          <h2 className="numbered-heading">文章</h2>
          {articles.map((a) => (
            <div key={a.slug} className="article-item">
              <div className="tags">
                {a.tags.map((t) => (
                  <span key={t}>{t}</span>
                ))}
              </div>
              <Link to={`/article/${a.slug}`} className="title">
                {a.title}
              </Link>
              <div className="date">{a.date}</div>
            </div>
          ))}
        </section>

        <section id="timeline">
          <h2 className="numbered-heading">时间线</h2>
          {diaries.map((d, i) => (
            <div key={i} className="tl-entry">
              <Link to={`/diary/${i}`}>
                <div className="tl-date">{d.date.slice(5)}</div>
                <div className="tl-preview">{d.title}</div>
              </Link>
            </div>
          ))}
        </section>
      </main>

      {showQR && (
        <div className="qr-overlay" onClick={() => setShowQR(false)}>
          <div className="qr-modal" onClick={(e) => e.stopPropagation()}>
            <button className="qr-close" onClick={() => setShowQR(false)}>×</button>
            <img src="/qrcode.jpg" alt="公众号二维码" />
            <p>微信扫码关注</p>
          </div>
        </div>
      )}
    </div>
  );
}
