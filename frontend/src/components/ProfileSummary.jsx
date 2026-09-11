// Shows the info the backend already extracts from the resume
// (skills, education, years of experience, tone) that wasn't
// being displayed anywhere before.

export default function ProfileSummary({ extractedInfo, sentiment }) {
  if (!extractedInfo) return null;

  const { skills, education, experience_years } = extractedInfo;

  return (
    <section className="profile-section">
      <div className="section-title">
        <h2>Candidate Profile</h2>
        <span>Extracted automatically from the resume</span>
      </div>

      <div className="profile-grid">

        {/* SKILLS */}
        <div className="profile-card">
          <span className="label">SKILLS DETECTED</span>
          <div className="chip-row">
            {skills && skills.length > 0 ? (
              skills.map((skill, i) => (
                <span className="chip" key={i}>{skill}</span>
              ))
            ) : (
              <p className="empty-text">No skills detected.</p>
            )}
          </div>
        </div>

        {/* EDUCATION */}
        <div className="profile-card">
          <span className="label">EDUCATION</span>
          <div className="chip-row">
            {education && education.length > 0 ? (
              education.map((ed, i) => (
                <span className="chip chip-alt" key={i}>{ed}</span>
              ))
            ) : (
              <p className="empty-text">No education detected.</p>
            )}
          </div>
        </div>

        {/* EXPERIENCE */}
        <div className="profile-card">
          <span className="label">EXPERIENCE</span>
          <strong className="stat-number">
            {experience_years != null ? `${experience_years} yrs` : "—"}
          </strong>
        </div>

        {/* SENTIMENT / TONE */}
        {sentiment && (
          <div className="profile-card">
            <span className="label">RESUME TONE</span>
            <strong className="stat-number capitalize">
              {sentiment.tone}
            </strong>
            <p className="empty-text">
              Professionalism: {Math.round(sentiment.professionalism_score * 100)}%
            </p>
          </div>
        )}

      </div>
    </section>
  );
}
