import React from "react";

export default function JobCard({
  jobTitle,
  jobDescription,
  company,
  location,
  keySkills,
  experienceYears,
  postedDate = "Recently posted"
}) {
  const safeTitle = (jobTitle || "Untitled Role").trim() || "Untitled Role";
  const safeLocation = (location || "Location flexible").trim() || "Location flexible";

  return (
    <div className="job-card">
      <div className="job-card-header">
        <div className="job-info">
          <h2 className="job-title">{safeTitle}</h2>
          <div className="job-meta">
            <span className="company">{company}</span>
            <span className="separator">•</span>
            <span className="location">📍 {safeLocation}</span>
            <span className="separator">•</span>
            <span className="posted-date">{postedDate}</span>
          </div>
        </div>
        <div className="job-actions" />
      </div>

      <div className="job-description">
        <h3>Job Description</h3>
        <p className="description-text">
          {jobDescription.length > 250
            ? `${jobDescription.substring(0, 250)}...`
            : jobDescription
          }
        </p>
        {jobDescription.length > 250 && (
          <button className="read-more-btn">Read More</button>
        )}
      </div>
    </div>
  );
}