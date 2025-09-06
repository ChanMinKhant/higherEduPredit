import React from "react";
import "./Home.css";
import { Link } from "react-router-dom";

export default function HeroSection() {
  return (
    <section className="hero" aria-labelledby="hero-heading">
      {/* Left Content */}
      <div className="content">
        <span className="eyebrow">Higher Education • Predictive Analytics</span>
        <h1 id="hero-heading">
          Open the door to better outcomes with {" "}
          <span className="accent">Higher Education Access Prediction</span>
        </h1>
        <p className="lead">
         A lightweight model that analyzes student data to predict final exam performance and higher education interest. It also provides personalized support to help students prepare effectively for their exams
        </p>

        {/* CTA Buttons */}
        <div className="cta-row">
          <Link to="/predict" className="btn" role="button">
            Predict now
          </Link>
          <Link to='/register' className="btn secondary" role="button">
            Register
          </Link>
        </div>

        {/* KPIs */}
        <div className="kpis" role="list" aria-label="Key metrics">
          <div className="kpi" role="listitem">
            <span>Predictive accuracy</span>
            <b>89%</b>
          </div>
          <div className="kpi" role="listitem">
            <span>Avg. decision time</span>
            <b>~0.6s / predict</b>
          </div>
        </div>
      </div>

      {/* Right Panel */}
      {/* <aside className="panel" aria-label="Preview panel">
        <div className="meta">
          <span className="chip">Model: ensemble</span>
          <span className="chip">Data: anonymized</span>
        </div>

        <div className="mock-visual" aria-hidden="true">
          <div>
            <div className="visual-title">Applicant access map</div>
            <div className="visual-sub">
              Heatmap + risk tiers • Interactive filters • Export CSV
            </div>
          </div>
        </div>

        <div className="meta">
          <div>Export • CSV / JSON</div>
          <div>Integrations: SIS, LMS</div>
        </div>
      </aside> */}
    </section>
  );
}