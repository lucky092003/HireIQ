import React, { useMemo, useState } from "react";
import JobCard from "./components/JobCard";
import FindMatches from "./components/FindMatches";
import ResultsPanel from "./components/ResultsPanel";

export default function App() {
  const [results, setResults] = useState([]);
  const [jobDescription, setJobDescription] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobLocation, setJobLocation] = useState("");
  const [keySkills, setKeySkills] = useState("");
  const [experienceYears, setExperienceYears] = useState("");

  const summaryItems = useMemo(
    () => [
      { label: "Fast screening", value: "Top 10" },
      { label: "Match engine", value: "Skills + Location" },
      { label: "Exports", value: "CSV ready" },
    ],
    []
  );

  const previewDescription = useMemo(() => {
    const fullDescription = jobDescription.trim();
    if (fullDescription.length >= 10) {
      return fullDescription;
    }

    const lines = [
      `Role: ${jobTitle.trim() || "General Software Engineer"}`,
      `Experience: ${experienceYears || "Open"} years`,
      `Location: ${jobLocation.trim() || "Flexible"}`,
      `Skills: ${keySkills.trim() || "No explicit skills provided"}`,
      "Using quick-input mode. Add full JD only if you want deeper context.",
    ];

    return lines.join("\n");
  }, [jobDescription, jobTitle, experienceYears, jobLocation, keySkills]);

  return (
    <div className="page app-shell">
      <div className="app-backdrop app-backdrop-left" />
      <div className="app-backdrop app-backdrop-right" />

      <div className="container app-grid">
        <header className="hero-section">
          <div className="brand-row">
            <div className="brand-mark">M</div>
            <div>
              <span className="eyebrow">AI recruiter assistant</span>
              <h1 className="hero-title">HireIQ</h1>
            </div>
          </div>

          <p className="hero-subtitle">
            Smartly match the right candidates by role, skills, and location through a fast, recruiter-first experience.
          </p>

          <div className="hero-summary">
            {summaryItems.map((item) => (
              <div className="summary-card" key={item.label}>
                <span className="summary-value">{item.value}</span>
                <span className="summary-label">{item.label}</span>
              </div>
            ))}
          </div>
        </header>

        <section className="job-input-section panel-surface">
          <div className="section-heading">
            <div>
              <span className="section-kicker">Job brief</span>
              <h2>Enter the role you want to fill</h2>
            </div>
            <div className="section-actions">
              <FindMatches
                jobDescription={jobDescription}
                jobTitle={jobTitle}
                jobLocation={jobLocation}
                keySkills={keySkills}
                experienceYears={experienceYears}
                showInternalResults={false}
                showButton={true}
                onResults={(candidates) => setResults(candidates)}
              />
            </div>
          </div>

          <div className="title-location-row">
            <div className="input-group half-input-group">
              <label htmlFor="jobTitle">Job Title</label>
              <input
                id="jobTitle"
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g. Senior React Developer"
                className="job-title-input"
              />
            </div>

            <div className="input-group half-input-group">
              <label htmlFor="jobLocation">Location</label>
              <input
                id="jobLocation"
                type="text"
                value={jobLocation}
                onChange={(e) => setJobLocation(e.target.value)}
                placeholder="e.g. San Francisco, CA or Remote"
                className="job-title-input"
              />
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="keySkills">Key Skills (comma separated)</label>
            <input
              id="keySkills"
              type="text"
              value={keySkills}
              onChange={(e) => setKeySkills(e.target.value)}
              placeholder="e.g. React, Node.js, PostgreSQL"
              className="job-title-input"
            />
          </div>

          <div className="input-group">
            <label htmlFor="experienceYears">Experience (years)</label>
            <input
              id="experienceYears"
              type="number"
              min="0"
              value={experienceYears}
              onChange={(e) => setExperienceYears(e.target.value)}
              placeholder="e.g. 3"
              className="job-title-input"
            />
          </div>

          <div className="input-group">
            <label htmlFor="jobDescription">Job Description</label>
            <p className="input-helper">Optional: leave this blank if you only want to search with skills + years.</p>
            <textarea
              id="jobDescription"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={6}
              placeholder="Optional: paste full JD for richer matching..."
              className="jd-input"
            />
          </div>
        </section>

        <section className="results-preview panel-surface">
          <div className="section-heading compact">
            <div>
              <span className="section-kicker">Preview</span>
              <h2>How your job card will look</h2>
            </div>
          </div>

          <JobCard
            jobTitle={jobTitle}
            jobDescription={previewDescription}
            company="TechCorp Inc."
            location={jobLocation}
            keySkills={keySkills}
            experienceYears={experienceYears}
          />

          {/* Render results panel under the preview */}
          {results && results.length >= 0 && <ResultsPanel results={results} />}
        </section>
      </div>
    </div>
  );
}
