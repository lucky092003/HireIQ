import React, { useMemo, useState } from "react";
import "./FindMatches.css";

export default function ResultsPanel({ results = [] }) {
  const [sortBy, setSortBy] = useState("score");
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const sortedResults = useMemo(() => {
    const list = [...results];
    if (sortBy === "skills") {
      list.sort((a, b) => (b.matched_skills?.length || 0) - (a.matched_skills?.length || 0));
    } else {
      list.sort((a, b) => b.match_score - a.match_score);
    }
    return list;
  }, [results, sortBy]);

  const stats = useMemo(() => {
    if (!results.length) return { averageScore: 0, totalSkills: 0, topScore: 0 };
    const totalScore = results.reduce((sum, c) => sum + c.match_score, 0);
    const totalSkills = results.reduce((sum, c) => sum + (c.matched_skills?.length || 0), 0);
    const topScore = Math.max(...results.map((c) => c.match_score));
    return { averageScore: (totalScore / results.length).toFixed(1), totalSkills, topScore };
  }, [results]);

  const exportToCSV = () => {
    if (!results.length) return;
    const headers = ["Rank", "Name", "Title", "Location", "Match Score", "Matched Skills", "Rationale"];
    const rows = sortedResults.map((candidate, index) => [
      index + 1,
      candidate.name,
      candidate.title,
      candidate.location || "N/A",
      `${candidate.match_score}%`,
      candidate.matched_skills?.join(" | ") || "N/A",
      candidate.rationale || "N/A",
    ]);

    const csv = [headers, ...rows]
      .map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `mike-smart-match-results-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="results-panel">
      <div className="results-header">
        <div>
          <h3>Top Candidates Matched by Mike</h3>
          <p className="candidate-count">{results.length} candidates found</p>
        </div>

        <div className="results-actions">
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="sort-select">
            <option value="score">Sort by Score</option>
            <option value="skills">Sort by Skills</option>
          </select>
          <button type="button" className="export-btn" onClick={exportToCSV} disabled={!results.length}>
            Export CSV
          </button>
        </div>
      </div>

      {results.length > 0 && (
        <div className="match-stats">
          <div className="stat-card">
            <span className="stat-label">Average Score</span>
            <span className="stat-value">{stats.averageScore}%</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Total Skills</span>
            <span className="stat-value">{stats.totalSkills}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Top Score</span>
            <span className="stat-value">{stats.topScore}%</span>
          </div>
        </div>
      )}

      {results.length === 0 ? (
        <div className="no-results">No matching candidates found.</div>
      ) : (
        <div className="candidates-list">
          {sortedResults.map((candidate, index) => (
            <div key={candidate.id} className="candidate-card" onClick={() => setSelectedCandidate(candidate)}>
              <div className="candidate-header">
                <div className="candidate-rank">#{index + 1}</div>
                <div className="candidate-info">
                  <h4>{candidate.name}</h4>
                  <p className="candidate-title">{candidate.title}</p>
                  {candidate.location && <p className="candidate-location">📍 {candidate.location}</p>}
                </div>
                <div className="match-score">
                  <div className="score-badge">{candidate.match_score}%</div>
                  <span className="score-label">Match</span>
                </div>
              </div>

              <div className="candidate-rationale">
                <p>{candidate.rationale}</p>
              </div>

              {candidate.matched_skills?.length > 0 && (
                <div className="candidate-matched-skills">
                  <span>Matched skills:</span>
                  {candidate.matched_skills.map((skill, idx) => (
                    <span key={idx} className="skill-tag">{skill}</span>
                  ))}
                </div>
              )}

              <div className={`location-fit ${candidate.location_match ? "match" : "no-match"}`}>
                {candidate.location_match ? "✅ Location preference matches" : "⚠️ Location preference may not match"}
              </div>

              <div className="candidate-footer">
                <div className="mike-badge">Matched by Mike</div>
                <div className="view-details">Click to view details</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedCandidate && (
        <div className="modal-overlay" onClick={() => setSelectedCandidate(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedCandidate(null)}>×</button>

            <div className="modal-header">
              <div>
                <h2>{selectedCandidate.name}</h2>
                <p>{selectedCandidate.title}</p>
              </div>
              <div className="modal-score">{selectedCandidate.match_score}% Match</div>
            </div>

            <div className="modal-section">
              <h3>Profile</h3>
              <p><strong>Location:</strong> {selectedCandidate.location || "Not specified"}</p>
            </div>

            <div className="modal-section">
              <h3>Matched Skills</h3>
              <div className="skills-grid">
                {selectedCandidate.matched_skills?.length > 0 ? (
                  selectedCandidate.matched_skills.map((skill, idx) => (
                    <span key={idx} className="skill-badge">{skill}</span>
                  ))
                ) : (
                  <p>No matched skills found.</p>
                )}
              </div>
            </div>

            <div className="modal-section">
              <h3>Match Analysis</h3>
              <p className="rationale-full">{selectedCandidate.rationale}</p>
            </div>

            <div className="modal-section">
              <h3>Location Fit</h3>
              <div className={`location-badge ${selectedCandidate.location_match ? "match" : "no-match"}`}>
                {selectedCandidate.location_match ? "Location preference matches" : "Location may not match"}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
