import { useParams, Link } from "react-router-dom";
import diaries from "../data/diaries";
import "./DetailPage.css";

export default function DiaryPage() {
  const { id } = useParams<{ id: string }>();
  const idx = Number(id);
  const diary = diaries[idx];

  if (!diary) {
    return (
      <div className="detail-page">
        <div className="detail-container">
          <Link to="/" className="back-link">← how</Link>
          <p>日记不存在</p>
        </div>
      </div>
    );
  }

  return (
    <div className="detail-page">
      <div className="detail-container">
        <Link to="/" className="back-link">← how</Link>
        <h1 className="detail-title">{diary.title}</h1>
        <div className="detail-date">{diary.date}</div>
        <div
          className="detail-body"
          dangerouslySetInnerHTML={{ __html: diary.body }}
        />
      </div>
    </div>
  );
}
