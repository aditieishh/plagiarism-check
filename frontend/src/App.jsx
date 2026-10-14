
import { useRef, useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  useLocation,
  useNavigate,
  Link,
} from "react-router-dom";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/compare";
const MAX_FILES = 10;
const MAX_FILE_SIZE = 5 * 1024 * 1024;


function Navbar() {
  return (
    <nav className="navbar">
      <Link className="brand" to="/">
        <span className="brand-mark">A</span>
        <span>authentica</span>
      </Link>
      <span className="nav-label">PDF SIMILARITY CHECKER</span>
    </nav>
  );
}

// -------------------- PDF Upload Page --------------------

function UploadPage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInput = useRef(null);
  const navigate = useNavigate();

  function addFiles(event) {
    const selected = Array.from(event.target.files || []);
    event.target.value = "";

    setError("");

    setFiles((currentFiles) => {
      const nextFiles = [...currentFiles];
      let message = "";

      for (const file of selected) {
        if (!file.name.toLowerCase().endsWith(".pdf")) {
          message = "Only PDF files are allowed.";
          continue;
        }

        if (file.size > MAX_FILE_SIZE) {
          message = `${file.name} exceeds the 5 MB limit.`;
          continue;
        }

        if (file.size === 0) {
          message = `${file.name} is empty.`;
          continue;
        }

        const alreadyAdded = nextFiles.some(
          (existing) =>
            existing.name === file.name &&
            existing.size === file.size &&
            existing.lastModified === file.lastModified
        );

        if (alreadyAdded) {
          message = `${file.name} has already been added.`;
          continue;
        }

        if (nextFiles.length >= MAX_FILES) {
          message = `You can add a maximum of ${MAX_FILES} PDFs.`;
          break;
        }

        nextFiles.push(file);
      }

      if (message) {
        setError(message);
      }

      return nextFiles;
    });
  }

  function removeFile(indexToRemove) {
    setFiles((currentFiles) =>
      currentFiles.filter((_, index) => index !== indexToRemove)
    );
    setError("");
  }

  async function compareFiles() {
    if (files.length < 2) {
      setError("Please add at least two PDF assignments.");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to compare your PDFs."
        );
      }

      navigate("/results", {
        state: {
          results: data,
          filenames: files.map((file) => file.name),
        },
      });
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to the backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-content">
      <section className="hero">
        <span className="eyebrow">
          <span className="status-dot" />
          YOUR WORK. YOUR ORIGINALITY.
        </span>

        <h1>
          Check your
          <br />
          <span>authenticity.</span>
        </h1>

        <p className="hero-description">
          Your ideas deserve to be yours. Compare assignments, discover
          similar passages, and understand how closely your documents align.
        </p>
      </section>

      <section className="upload-card">
        <div className="card-heading">
          <div>
            <p className="section-kicker">LET&apos;S GET STARTED</p>
            <h2>Compare your assignments</h2>
            <p className="muted">
              Add at least two PDFs, one at a time.
            </p>
          </div>

          <div className="pdf-icon">PDF</div>
        </div>

        <input
          ref={fileInput}
          className="hidden-input"
          type="file"
          accept=".pdf,application/pdf"
          multiple
          onChange={addFiles}
        />

        {files.length === 0 ? (
          <button
            className="first-upload"
            type="button"
            onClick={() => fileInput.current?.click()}
          >
            <span className="upload-icon">↑</span>
            <strong>Choose your first PDF</strong>
            <span className="drop-hint">Click to browse your files</span>
            <span className="file-note">
              PDF only · Up to 5 MB per file
            </span>
          </button>
        ) : (
          <div className="selected-files">
            <div className="selected-heading">
              <strong>Your assignments</strong>
              <span>
                {files.length} of {MAX_FILES} PDFs
              </span>
            </div>

            {files.map((file, index) => (
              <div
                className="file-row"
                key={`${file.name}-${file.lastModified}-${index}`}
              >
                <span className="file-badge">PDF</span>

                <div className="file-info">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </span>
                </div>

                <button
                  className="remove-file"
                  type="button"
                  aria-label={`Remove ${file.name}`}
                  onClick={() => removeFile(index)}
                >
                  ×
                </button>
              </div>
            ))}

            {files.length < MAX_FILES && (
              <button
                className="add-pdf-button"
                type="button"
                onClick={() => fileInput.current?.click()}
              >
                <span className="plus-icon">+</span>
                <span>Add another PDF</span>
              </button>
            )}
          </div>
        )}

        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}

        <button
          className="compare-button"
          type="button"
          onClick={compareFiles}
          disabled={loading}
        >
          {loading ? "Analyzing your assignments..." : "Check authenticity"}
          {!loading && <span>→</span>}
        </button>

        <p className="privacy-note">
          Your documents are processed by your comparison service.
        </p>
      </section>
    </main>
  );
}



function SimilarityMeter({ label, value, tone }) {
  const score = Number(value);
  const hasScore =
    value !== null && value !== undefined && value !== "" &&
    Number.isFinite(score);

  const safeScore = hasScore ? Math.max(0, Math.min(100, score)) : 0;

  let description = "Lower similarity";

  if (safeScore >= 70) {
    description = "High similarity";
  } else if (safeScore >= 40) {
    description = "Moderate similarity";
  }

  return (
    <div className={`meter-card ${tone}`}>
      <div className="meter-heading">
        <span>{label}</span>
        <strong>{hasScore ? `${score}%` : "N/A"}</strong>
      </div>

      <div
        className="meter-track"
        role="progressbar"
        aria-label={label}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={safeScore}
      >
        <div
          className="meter-fill"
          style={{ width: `${safeScore}%` }}
        />
      </div>

      <span className="meter-caption">
        {hasScore ? description : "Score unavailable"}
      </span>
    </div>
  );
}



function PassageCard({ title, sentence, tone }) {
  return (
    <div className={`passage-card ${tone}`}>
      <span className="passage-label">{title}</span>
      <p>
        <mark>{sentence}</mark>
      </p>
    </div>
  );
}



function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const results = location.state?.results;

  if (!Array.isArray(results)) {
    return (
      <main className="page-content results-page">
        <section className="empty-report">
          <h1>No report to display yet</h1>
          <p className="muted">
            Upload and compare at least two PDF assignments to see your report.
          </p>
          <button
            className="compare-button"
            onClick={() => navigate("/")}
          >
            Go to PDF upload →
          </button>
        </section>
      </main>
    );
  }

  const filenames = location.state?.filenames || [];
  const documentCount = filenames.length;

  function average(key) {
    if (results.length === 0) return 0;

    const values = results
      .map((result) => result[key])
      .filter(
        (value) =>
          value !== null &&
          value !== undefined &&
          value !== "" &&
          Number.isFinite(Number(value))
      )
      .map(Number);

    if (values.length === 0) return 0;

    return Number(
      (
        values.reduce((sum, value) => sum + value, 0) / values.length
      ).toFixed(1)
    );
  }

  const averageWord = average("similarity_percentage");
  const averageSemantic = average("semantic_similarity_percentage");

  const phraseMatchCount = results.reduce(
    (total, result) =>
      total + (result.matching_sentences?.length || 0),
    0
  );

  const semanticMatchCount = results.reduce(
    (total, result) =>
      total + (result.semantic_matches?.length || 0),
    0
  );

  return (
    <main className="page-content results-page">
      <button
        className="back-button"
        type="button"
        onClick={() => navigate("/")}
      >
        ← Back to uploads
      </button>

      <section className="results-heading">
        <p className="section-kicker">YOUR ANALYSIS</p>
        <h1>Your similarity report.</h1>
        <p className="muted">
          A side-by-side review of your documents and their textual similarities.
        </p>
      </section>

      
      <section className="summary-panel">
        <div className="summary-top">
          <div>
            <span className="summary-eyebrow">COMPARISON OVERVIEW</span>
            <h2>Your report at a glance</h2>
          </div>

          <span className="summary-badge">Analysis complete</span>
        </div>

        <div className="summary-stats">
          <div className="summary-stat">
            <span>Documents</span>
            <strong>{documentCount || "—"}</strong>
            <small>PDF assignments</small>
          </div>

          <div className="summary-stat">
            <span>Comparisons</span>
            <strong>{results.length}</strong>
            <small>Document pairs</small>
          </div>

          <div className="summary-stat">
            <span>Sentence matches</span>
            <strong>{phraseMatchCount}</strong>
            <small>Phrase matches detected</small>
          </div>

          <div className="summary-stat">
            <span>Potential paraphrases</span>
            <strong>{semanticMatchCount}</strong>
            <small>Semantic matches detected</small>
          </div>
        </div>

        <div className="overall-scores">
          <div className="overall-score">
            <div className="overall-score-heading">
              <span>Average word similarity</span>
              <strong>{averageWord}%</strong>
            </div>

            <div className="meter-track">
              <div
                className="meter-fill word-fill"
                style={{
                  width: `${Math.max(0, Math.min(100, averageWord))}%`,
                }}
              />
            </div>
          </div>

          <div className="overall-score">
            <div className="overall-score-heading">
              <span>Average semantic similarity</span>
              <strong>{averageSemantic}%</strong>
            </div>

            <div className="meter-track">
              <div
                className="meter-fill semantic-fill"
                style={{
                  width: `${Math.max(0, Math.min(100, averageSemantic))}%`,
                }}
              />
            </div>
          </div>
        </div>

        <p className="summary-disclaimer">
          Averages are calculated across the returned document pairs.
          Similarity indicates textual overlap or semantic resemblance,
          not proof of plagiarism.
        </p>
      </section>

      
      <div className="pair-section-heading">
        <div>
          <p className="section-kicker">DETAILED BREAKDOWN</p>
          <h2>Document comparisons</h2>
        </div>

        <span>
          {results.length} {results.length === 1 ? "pair" : "pairs"}
        </span>
      </div>

      {results.map((result, index) => {
        const phraseMatches = result.matching_sentences || [];
        const semanticMatches = result.semantic_matches || [];

        return (
          <article
            className="result-card enhanced-result-card"
            key={`${result.file1}-${result.file2}-${index}`}
          >
            <div className="pair-card-heading">
              <span className="pair-number">
                COMPARISON {String(index + 1).padStart(2, "0")}
              </span>

              <div className="comparison-names">
                <span>{result.file1}</span>
                <span className="versus">VS</span>
                <span>{result.file2}</span>
              </div>
            </div>

            

            
            <section className="passage-section">
              <div className="passage-section-heading">
                <h3>Matching sentences</h3>
                <span className="count-pill">{phraseMatches.length}</span>
              </div>

              <p className="section-description">
                Sentences identified by the phrase-matching algorithm.
              </p>

              {phraseMatches.length > 0 ? (
                phraseMatches.map((match, i) => (
                  <div className="passage-pair" key={`phrase-${i}`}>
                    {match.similarity_score != null && (
                      <span className="match-score-pill">
                        {match.similarity_score}% match
                      </span>
                    )}

                    <div className="passage-columns">
                      <PassageCard
                        title={result.file1}
                        sentence={match.sentence1}
                        tone="original-passage"
                      />

                      <PassageCard
                        title={result.file2}
                        sentence={match.sentence2}
                        tone="compared-passage"
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-matches">
                  No phrase matches were detected for this pair.
                </div>
              )}
            </section>

            
            <section className="passage-section semantic-section">
              <div className="passage-section-heading">
                <h3>Potential paraphrases</h3>
                <span className="count-pill semantic-count">
                  {semanticMatches.length}
                </span>
              </div>

              <p className="section-description">
                Sentences with similar meanings, even when their wording differs.
              </p>

              {semanticMatches.length > 0 ? (
                semanticMatches.map((match, i) => (
                  <div className="passage-pair" key={`semantic-${i}`}>
                    {match.similarity_score != null && (
                      <span className="match-score-pill semantic-score-pill">
                        {match.similarity_score}% semantic match
                      </span>
                    )}

                    <div className="passage-columns">
                      <PassageCard
                        title={result.file1}
                        sentence={match.sentence1}
                        tone="original-passage"
                      />

                      <PassageCard
                        title={result.file2}
                        sentence={match.sentence2}
                        tone="semantic-passage"
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-matches">
                  No semantic matches were detected above the configured threshold.
                </div>
              )}
            </section>
          </article>
        );
      })}

      <p className="report-note">
        Review the highlighted passages in context. Shared terminology,
        quotations, references, and standard academic phrases may be legitimate.
      </p>

      <button
        className="compare-button report-action"
        type="button"
        onClick={() => navigate("/")}
      >
        Compare more assignments →
      </button>
    </main>
  );
}



function AppLayout() {
  return (
    <div className="app-shell">
      <Navbar />

      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="*" element={<UploadPage />} />
      </Routes>

      <footer>
        <span>authentica</span>
        <span>Built for clarity. Designed for originality.</span>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}
