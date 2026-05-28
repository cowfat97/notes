import { useParams, Link } from "react-router-dom";
import articles from "../data/articles";
import "./DetailPage.css";

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>();
  const article = articles.find((a) => a.slug === slug);

  if (!article) {
    return (
      <div className="detail-page">
        <div className="detail-container">
          <Link to="/" className="back-link">← how</Link>
          <p>文章不存在</p>
        </div>
      </div>
    );
  }

  return (
    <div className="detail-page">
      <div className="detail-container">
        <Link to="/" className="back-link">← how</Link>
        <div className="detail-tags">
          {article.tags.map((t) => (
            <span key={t}>{t}</span>
          ))}
        </div>
        <h1 className="detail-title">{article.title}</h1>
        <div className="detail-date">{article.date}</div>
        <div
          className="detail-body"
          dangerouslySetInnerHTML={{ __html: article.body }}
        />
      </div>
    </div>
  );
}
