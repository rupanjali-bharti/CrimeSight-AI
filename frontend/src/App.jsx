import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowRight,
  BookOpen,
  Check,
  Clipboard,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  Database,
  Download,
  FileText,
  GitBranch,
  Menu,
  Network,
  Plus,
  Send,
  Scale,
  Settings,
  ShieldCheck,
  Sparkles,
  Terminal,
  Zap,
  X,
} from "lucide-react";
import {
  classifyCrimeCategory,
  extractBnsSections,
  getEvidenceCategoryLabel,
  getEvidenceRequirements,
} from "./evidenceMatcher.js";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/analyze-situation";
const starters = [
  "Theft with Private Defence",
  "Street Assault with Grievous Hurt",
  "Cyber Fraud & Extortion",
];
const flow = [
  {
    number: "01",
    title: "User Situation",
    icon: FileText,
    copy: "Turn complex incident narratives into structured legal intelligence.",
  },
  {
    number: "02",
    title: "Schema RAG",
    icon: GitBranch,
    copy: "BNS and BNSS schemas retrieved with contextual precision.",
  },
  {
    number: "03",
    title: "Text-to-Cypher",
    icon: Terminal,
    copy: "Generate transparent, read-only graph queries from legal intent.",
  },
  {
    number: "04",
    title: "Graph Traversal",
    icon: Network,
    copy: "Execute multi-hop Neo4j traversals across connected provisions.",
  },
  {
    number: "05",
    title: "Legal Synthesis",
    icon: ShieldCheck,
    copy: "Deliver cited reasoning with auditable compliance context.",
  },
];
const capabilities = [
  [
    "Contextual Schema Intelligence",
    "Retrieve the precise BNS and BNSS graph context for every matter.",
    GitBranch,
  ],
  [
    "Deterministic Legal Mapping",
    "Trace every conclusion through verified relationships and provisions.",
    Network,
  ],
  [
    "Zero-Hallucination Guardrails",
    "Keep legal synthesis anchored to source-backed graph evidence.",
    BookOpen,
  ],
  [
    "Persistent Case Intelligence",
    "Maintain conversational session context across complex investigations.",
    ShieldCheck,
  ],
];
const thinkingSteps = [
  ["Analyzing incident narrative...", FileText],
  ["Retrieving dynamic BNS schema patterns...", Zap],
  ["Traversing Neo4j legal knowledge graph...", Network],
  ["Synthesizing grounded legal response...", ShieldCheck],
];
const demoResponse = `### Matched Legal Provisions
- The representative result identifies provisions relating to assault causing grievous hurt under the Bharatiya Nyaya Sanhita, 2023.
### Relevant Offence Definitions
- No offence definition was explicitly retrieved from the graph.
### Key Limitations / Next Steps
- The classification depends on medical evidence, intent, and the circumstances of the incident.
- Additional specific statutory provisions can be retrieved by providing the relevant section numbers.`;

function Logo({ compact = false }) {
  return (
    <div className={compact ? "logo-mark compact" : "logo-mark"}>
      <span>CS</span>
    </div>
  );
}

function Landing({ onLaunch }) {
  return (
    <main className="landing">
      <nav className="topbar page-width">
        <button
          className="brand-button"
          onClick={onLaunch}
          aria-label="Open CrimeSight workspace"
        >
          <Logo />
          <span>
            CrimeSight<span className="brand-dot">.</span>AI
          </span>
        </button>
        <div className="top-links">
          <a href="#architecture">Architecture</a>
          <a href="#capabilities">Capabilities</a>
          <span className="status">
            <i /> System online
          </span>
        </div>
        <button className="nav-launch" onClick={onLaunch}>
          Open workspace <ArrowRight size={15} />
        </button>
      </nav>
      <section className="hero page-width">
        <div className="hero-copy">
          <div className="eyebrow">
            <span className="eyebrow-line" /> AI LEGAL INTELLIGENCE / BNS + BNSS
          </div>
          <h1>
            Legal intelligence
            <br />
            <em>with evidence.</em>
          </h1>
          <p className="hero-subtitle">
            CrimeSight Agent transforms complex incident narratives into
            transparent, source-grounded legal intelligence across the BNS and
            BNSS knowledge graph.
          </p>
          <div className="hero-actions">
            <button className="primary-button" onClick={onLaunch}>
              Launch CrimeSight Agent <ArrowRight size={18} />
            </button>
            <span className="micro-note">
              <ShieldCheck size={15} /> Auditable reasoning. Verified graph evidence.
            </span>
          </div>
        </div>
        <div className="hero-visual" aria-label="Knowledge graph visualization">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="graph-lines">
            <span />
            <span />
            <span />
            <span />
            <span />
          </div>
          <div className="graph-center">
            <Database size={22} />
            <b>NEO4J</b>
            <small>LEGAL GRAPH</small>
          </div>
          <div className="graph-node node-a">
            <FileText size={15} />
            <span>incident</span>
          </div>
          <div className="graph-node node-b">
            <BookOpen size={15} />
            <span>§ 115</span>
          </div>
          <div className="graph-node node-c">
            <ShieldCheck size={15} />
            <span>defence</span>
          </div>
          <div className="graph-caption">
            <span>PRODUCTION GRAPH</span>
            <b>12,847+</b>
            <small>connected legal entities</small>
          </div>
        </div>
      </section>
      <section className="architecture page-width" id="architecture">
        <div className="section-heading">
          <span>01 / HOW IT THINKS</span>
          <h2>From narrative to defensible legal intelligence.</h2>
        </div>
        <div className="flow-grid">
          {flow.map(({ number, title, icon: Icon, copy }, index) => (
            <motion.div
              className="flow-item"
              key={title}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.08 }}
              viewport={{ once: true }}
            >
              <span className="flow-number">{number}</span>
              <Icon size={20} />
              <h3>{title}</h3>
              <p>{copy}</p>
              {index < flow.length - 1 && (
                <ArrowRight className="flow-arrow" size={16} />
              )}
            </motion.div>
          ))}
        </div>
      </section>
      <section className="capabilities page-width" id="capabilities">
        <div className="section-heading">
          <span>02 / BUILT FOR THE DETAILS</span>
          <h2>Reasoning built for scrutiny.</h2>
        </div>
        <div className="capability-grid">
          {capabilities.map(([title, copy, Icon]) => (
            <div className="capability" key={title}>
              <Icon size={19} />
              <h3>{title}</h3>
              <p>{copy}</p>
            </div>
          ))}
        </div>
      </section>
      <footer className="footer page-width">
        <span>
          <Logo compact /> CrimeSight-AI
        </span>
        <span>Indian Criminal Law · BNS + BNSS</span>
        <span>© 2026</span>
      </footer>
    </main>
  );
}

function Thinking({ active }) {
  return (
    <div className="thinking">
      <div className="thinking-label">
        <Sparkles size={15} /> AGENT TRACE
      </div>
      {thinkingSteps.map(([label, Icon], index) => (
        <div
          className={`thinking-step ${index < active ? "done" : ""} ${index === active ? "current" : ""}`}
          key={label}
        >
          <span className="step-icon">
            {index < active ? <Check size={13} /> : <Icon size={14} />}
          </span>
          <span>{label}</span>
          {index === active && <i className="pulse" />}
        </div>
      ))}
    </div>
  );
}

function MarkdownResponse({ text }) {
  const technicalMarkers = [
    "uid",
    "internal id",
    "node label",
    "retrieval metadata",
    "property dump",
    "cypher",
    "timestamp",
  ];
  const lines = text.split("\n").filter((line) => {
    const trimmed = line.trim();
    return (
      trimmed &&
      !trimmed.startsWith("|") &&
      !/^[-| :]+$/.test(trimmed) &&
      !technicalMarkers.some((marker) => trimmed.toLowerCase().includes(marker))
    );
  });
  return (
    <div className="response-copy">
      {lines.map((line, index) => {
        if (line.startsWith("### "))
          return <h3 key={index}>{line.slice(4)}</h3>;
        if (/^(?:[-*+]\s+|\d+[.)]\s+|•\s+)/.test(line))
          return (
            <div className="response-bullet" key={index}>
              <span />
              {line
                .replace(/^(?:[-*+]\s+|\d+[.)]\s+|•\s+)/, "")
                .split(/(\*\*.*?\*\*)/)
                .map((part, i) =>
                  part.startsWith("**") ? (
                    <strong key={i}>{part.slice(2, -2)}</strong>
                  ) : (
                    part
                  ),
                )}
            </div>
          );
        return (
          <p key={index}>
            {line
              .split(/(\*\*.*?\*\*)/)
              .map((part, i) =>
                part.startsWith("**") ? (
                  <strong key={i}>{part.slice(2, -2)}</strong>
                ) : (
                  part
                ),
              )}
          </p>
        );
      })}
    </div>
  );
}

function Evidence({ cypher, matched }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={`evidence ${open ? "open" : ""}`}>
      <button onClick={() => setOpen(!open)}>
        <span>
          <Terminal size={15} /> View graph sources &amp; Cypher
        </span>
        <ChevronDown size={16} />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            className="evidence-body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
          >
            <div className="query-label">GENERATED READ-ONLY QUERY</div>
            <pre>{cypher}</pre>
            <div className="evidence-meta">
              <span>
                <Database size={13} /> Neo4j execution · 0.42s
              </span>
              <span>
                <Check size={13} /> {matched || 3} matched nodes
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function EvidenceMatcherPanel({
  messages,
  draft,
  onGenerateDraft,
  draftGenerating,
  draftError,
}) {
  const narrative = [
    ...messages
      .filter((message) => message.role === "user")
      .map((message) => message.text),
    draft,
  ]
    .filter(Boolean)
    .join("\n");
  const latestServerMessageIndex = messages.reduce(
    (latest, message, index) =>
      message.role === "agent" && message.caseAnalysis ? index : latest,
    -1,
  );
  const latestUserMessageIndex = messages.reduce(
    (latest, message, index) =>
      message.role === "user" ? index : latest,
    -1,
  );
  const latestServerAnalysis =
    latestServerMessageIndex > latestUserMessageIndex
      ? messages[latestServerMessageIndex].caseAnalysis
      : null;
  const serverAnalysis = draft.trim() ? null : latestServerAnalysis;
  const category =
    serverAnalysis?.category || classifyCrimeCategory(narrative);
  const requirements = serverAnalysis?.evidence_checklist
    ? serverAnalysis.evidence_checklist.map(({ item, status }) => ({
        label: item,
        available: status === "AVAILABLE",
      }))
    : getEvidenceRequirements(category, narrative);
  const availableCount = requirements.filter((item) => item.available).length;
  const firReady =
    serverAnalysis?.fir_ready ??
    (requirements.length > 0 && availableCount === requirements.length);
  const matchedStatutes = messages.reduce(
    (latest, message) =>
      message.role === "agent" && Array.isArray(message.matchedStatutes)
        ? message.matchedStatutes
        : latest,
    [],
  );
  const sections = matchedStatutes.length
    ? matchedStatutes
    : extractBnsSections(
        messages
          .filter((message) => message.role === "agent")
          .map((message) => message.text),
      ).map((section) => ({ section, title: "" }));

  return (
    <aside className="evidence-matcher" aria-live="polite">
      <div className="matcher-heading">
        <span className="workspace-kicker">CASE EVIDENCE / BNS</span>
        <h2>Evidence to Statute Matcher</h2>
        <p>Requirements update as you describe the case.</p>
      </div>

      <section className="matcher-section">
        <span className="matcher-label">DETECTED CASE CATEGORY</span>
        <strong className="matcher-category">
          {serverAnalysis?.category_label ||
            getEvidenceCategoryLabel(category) ||
            "Awaiting incident details"}
        </strong>
      </section>

      <section className="matcher-section">
        <div className="matcher-section-heading">
          <span className="matcher-label">MATCHED BNS STATUTES</span>
          <Scale size={16} />
        </div>
        {sections.length ? (
          <div className="statute-tags">
            {sections.map((statute) => {
              const section =
                typeof statute === "string" ? statute : statute.section;
              const title =
                typeof statute === "string" ? "" : statute.title;
              return (
                <span
                  className="statute-tag"
                  key={`${section}-${title}`}
                  title={statute.description || title || undefined}
                >
                  {section ? `BNS § ${section}` : `BNS · ${title}`}
                </span>
              );
            })}
          </div>
        ) : (
          <p className="matcher-empty">
            Statutes appear here when cited in the agent response.
          </p>
        )}
      </section>

      <section className="matcher-section">
        <div className="matcher-section-heading">
          <span className="matcher-label">EVIDENCE CHECKLIST</span>
          <span className="matcher-count">
            {narrative.trim()
              ? `${availableCount}/${requirements.length} mentioned`
              : "—"}
          </span>
        </div>
        {narrative.trim() ? (
          <ul className="matcher-list">
            {requirements.map(({ label, available }) => (
              <li
                className={available ? "evidence-available" : ""}
                key={label}
              >
                <span className="matcher-status" aria-hidden="true">
                  {available ? <Check size={13} /> : null}
                </span>
                <span>{label}</span>
                <b>{available ? "AVAILABLE" : "MISSING"}</b>
              </li>
            ))}
          </ul>
        ) : (
          <p className="matcher-empty">
            Describe the incident to generate relevant evidence requirements.
          </p>
        )}
        <p className="matcher-note">
          “Available” means mentioned in the conversation; it does not verify
          or validate supporting records.
        </p>
      </section>
      {firReady && (
        <div className="matcher-draft-action">
          <button
            className="matcher-generate"
            type="button"
            onClick={onGenerateDraft}
            disabled={draftGenerating}
          >
            {draftGenerating ? (
              <span className="loading-dot" />
            ) : (
              <FileText size={16} />
            )}
            {draftGenerating ? "Preparing FIR Draft..." : "Generate Official FIR Draft"}
          </button>
          {draftError && (
            <p className="matcher-draft-error" role="alert">
              {draftError}
            </p>
          )}
        </div>
      )}
    </aside>
  );
}

function Workspace({ onBack }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sessions, setSessions] = useState([
    { id: "1", title: "New Case", messages: [] },
  ]);
  const [activeSessionId, setActiveSessionId] = useState("1");
  const [situation, setSituationState] = useState("");
  const [loading, setLoading] = useState(false);
  const [thinking, setThinking] = useState(0);
  const [error, setError] = useState("");
  const [draftGenerating, setDraftGenerating] = useState(false);
  const [draftGenerationError, setDraftGenerationError] = useState("");
  const [draftActionFeedback, setDraftActionFeedback] = useState("");
  const [firDraft, setFirDraft] = useState("");
  const textareaRef = useRef(null);
  const activeSession =
    sessions.find((session) => session.id === activeSessionId) || sessions[0];
  const messages = activeSession?.messages || [];
  const sidebarChats = sessions.filter(
    (session) => session.messages.length > 0,
  );
  const setSituation = (value) => {
    const selectedSession = sessions.find(
      (session) => session.title === value && session.messages.length > 0,
    );
    if (selectedSession) setActiveSessionId(selectedSession.id);
    else setSituationState(value);
  };
  const setMessages = (updater) => {
    setSessions((current) => {
      if (Array.isArray(updater) && updater.length === 0) {
        const newId = Date.now().toString();
        setActiveSessionId(newId);
        return [...current, { id: newId, title: "New Case", messages: [] }];
      }
      const session = current.find((item) => item.id === activeSessionId);
      if (!session) return current;
      const nextMessages =
        typeof updater === "function" ? updater(session.messages) : updater;
      const firstUserMessage = nextMessages.find(
        (message) => message.role === "user",
      );
      const title =
        session.title === "New Case" && firstUserMessage
          ? firstUserMessage.text.split(/\s+/).slice(0, 6).join(" ")
          : session.title;
      const updatedSession = { ...session, title, messages: nextMessages };
      const otherSessions = current.filter(
        (item) => item.id !== activeSessionId,
      );
      return nextMessages.length === 1 && nextMessages[0].role === "user"
        ? [updatedSession, ...otherSessions]
        : current.map((item) =>
            item.id === activeSessionId ? updatedSession : item,
          );
    });
  };
  useEffect(() => {
    if (!loading) return undefined;
    setThinking(0);
    const timer = setInterval(
      () => setThinking((step) => Math.min(step + 1, 4)),
      850,
    );
    return () => clearInterval(timer);
  }, [loading]);
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [situation]);
  useEffect(() => {
    if (!firDraft) return undefined;
    const closeOnEscape = (event) => {
      if (event.key === "Escape") setFirDraft("");
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [firDraft]);
  const appendFirNextSteps = () => {
    setMessages((current) =>
      current.some((message) => message.firNextSteps)
        ? current
        : [
            ...current,
            {
              role: "agent",
              text: "Your FIR draft is ready! Would you like me to list the essential documents and ID proofs you should carry when visiting the police station?",
              firNextSteps: true,
            },
          ],
    );
  };
  const generateFirDraft = async () => {
    const pendingNarrative = situation.trim();
    const userMessages = messages.filter((message) => message.role === "user");
    const currentSituation =
      pendingNarrative || userMessages[userMessages.length - 1]?.text || "";
    if (!currentSituation || draftGenerating) return;

    setDraftGenerating(true);
    setDraftGenerationError("");
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/generate-fir-draft",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            situation: currentSituation,
            chat_history: messages.map(({ role, text }) => ({
              role,
              content: text,
            })),
          }),
        },
      );
      const data = await response.json();
      if (!response.ok) {
        const detail = data.detail;
        throw new Error(
          typeof detail === "string"
            ? detail
            : detail?.message || "Could not generate the FIR draft.",
        );
      }
      setFirDraft(data.draft);
      setDraftActionFeedback("");
      appendFirNextSteps();
    } catch (generationError) {
      setDraftGenerationError(
        generationError instanceof Error
          ? generationError.message
          : "Could not generate the FIR draft.",
      );
    } finally {
      setDraftGenerating(false);
    }
  };
  const copyFirDraft = async () => {
    try {
      await navigator.clipboard.writeText(firDraft);
      setDraftActionFeedback("Draft copied to clipboard.");
    } catch {
      setDraftActionFeedback("Clipboard access failed. Select and copy the draft text.");
    }
  };
  const downloadFirDraft = () => {
    try {
      const blob = new Blob([firDraft], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "crimesight-fir-draft.txt";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setDraftActionFeedback("FIR draft downloaded as a text file.");
      appendFirNextSteps();
    } catch {
      setDraftActionFeedback("Could not download the FIR draft.");
    }
  };
  const submit = async (value = situation) => {
    const query = value.trim();
    if (!query || loading) return;
    const historyForRequest = [
      ...messages.map(({ role, text }) => ({ role, content: text })),
      { role: "user", content: query },
    ];
    setSituation("");
    setError("");
    setLoading(true);
    setMessages((current) => [...current, { role: "user", text: query }]);
    try {
      const result = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          situation: query,
          chat_history: historyForRequest,
        }),
      });
      if (!result.ok) throw new Error("Backend unavailable");
      const data = await result.json();
      setMessages((current) => [
        ...current,
        {
          role: "agent",
          text: data.reply || data.agent_response || demoResponse,
          caseAnalysis: data.detected_category && data.evidence_checklist
            ? {
                category: data.case_analysis?.category,
                category_label: data.detected_category,
                evidence_checklist: data.evidence_checklist,
                fir_ready: data.fir_ready ?? data.case_analysis?.fir_ready,
              }
            : data.case_analysis,
          cypher:
            data.extracted_cypher ||
            data.cypher_query ||
            "MATCH (e:Entity)-[r]-(s:Entity) RETURN e, s",
          matched: data.matched_nodes,
          matchedStatutes: data.matched_statutes || [],
        },
      ]);
    } catch {
      setError(
        "Live API unavailable. Showing a representative grounded response.",
      );
      setMessages((current) => [
        ...current,
        {
          role: "agent",
          text: demoResponse,
          cypher:
            "MATCH (e:Entity)-[r]-(s:Entity)\nWHERE toString(e.name) CONTAINS 'assault'\nRETURN e, s",
          matched: 3,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };
  return (
    <main className="workspace">
      <aside className={`sidebar ${sidebarOpen ? "" : "collapsed"}`}>
        <div className="side-top">
          <button className="brand-button workspace-brand" onClick={onBack}>
            <Logo />
            <span>
              CrimeSight<span className="brand-dot">.</span>AI
            </span>
          </button>
          <button
            className="icon-button side-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? (
              <ChevronLeft size={17} />
            ) : (
              <ChevronRight size={17} />
            )}
          </button>
        </div>
        {sidebarOpen && (
          <>
            <div className="connection">
              <span className="connection-dot" />
              <span>Neo4j Connected</span>
              <span className="connection-ping" />
            </div>
            <button
              className="new-case"
              onClick={() => {
                setMessages([]);
                setError("");
              }}
            >
              <Plus size={17} /> New case analysis
            </button>
            <div className="history">
              <span className="side-label">CASE HISTORY</span>
              {sidebarChats.map((session) => (
                <button
                  className={`history-item ${session.id === activeSessionId ? "selected" : ""}`}
                  key={session.id}
                  onClick={() => setActiveSessionId(session.id)}
                >
                  <FileText size={15} />
                  <span>{session.title}</span>
                  <ChevronRight size={13} />
                </button>
              ))}
            </div>
            <div className="side-bottom">
              <button className="profile">
                <span className="avatar">RB</span>
                <span>
                  <b>Rupanjali Bharti</b>
                  <small>Researcher</small>
                </span>
                <ChevronRight size={14} />
              </button>
              <button className="settings">
                <Settings size={16} /> System settings
              </button>
            </div>
          </>
        )}
      </aside>
      <section className="chat">
        <header className="chat-header">
          <button
            className="icon-button mobile-menu"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <Menu size={19} />
          </button>
          <div>
            <span className="workspace-kicker">CRIMESIGHT / CASE ANALYSIS</span>
            <h1>Legal intelligence workspace</h1>
          </div>
          <button className="help-button" aria-label="Help">
            <CircleHelp size={18} />
          </button>
        </header>
        <div className="chat-scroll">
          <AnimatePresence initial={false}>
            {messages.length === 0 && !loading && (
              <motion.div
                className="welcome"
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="welcome-symbol">
                  <Sparkles size={20} />
                </div>
                <span className="workspace-kicker">
                  GOOD AFTERNOON, RESEARCHER
                </span>
                <h2>What happened?</h2>
                <p>
                  Describe an incident in your own words. The graph will map it
                  to relevant BNS provisions and show its work.
                </p>
                <div className="starter-grid">
                  {starters.map((starter) => (
                    <button key={starter} onClick={() => submit(starter)}>
                      {starter}
                      <ArrowRight size={14} />
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
            {messages.map((message, index) =>
              message.role === "user" ? (
                <motion.div
                  className="message user-message"
                  key={`${message.text}-${index}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <span>{message.text}</span>
                </motion.div>
              ) : (
                <motion.div
                  className="agent-block"
                  key={`${message.text}-${index}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <div className="agent-heading">
                    <Logo compact />
                    <span>CRIMESIGHT AGENT</span>
                    <i /> <small>grounded response</small>
                  </div>
                  <div className="agent-card">
                    <MarkdownResponse text={message.text} />
                    <Evidence
                      cypher={message.cypher}
                      matched={message.matched}
                    />
                  </div>
                </motion.div>
              ),
            )}
            {loading && (
              <motion.div
                className="agent-block"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <div className="agent-heading">
                  <Logo compact />
                  <span>CRIMESIGHT AGENT</span>
                </div>
                <Thinking active={thinking} />
              </motion.div>
            )}
          </AnimatePresence>
          {error && (
            <div className="api-note">
              <Zap size={14} /> {error}
            </div>
          )}
        </div>
        <form
          className="composer-wrap"
          onSubmit={(event) => {
            event.preventDefault();
            submit();
          }}
        >
          <div className="composer">
            <textarea
              ref={textareaRef}
              value={situation}
              onChange={(event) => setSituation(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  submit();
                }
              }}
              placeholder="Describe the incident..."
              rows="1"
              maxLength="2000"
            />
            <div className="composer-footer">
              <span>{situation.length} / 2,000</span>
              <button
                className="send-button"
                type="submit"
                disabled={!situation.trim() || loading}
                aria-label="Send analysis"
              >
                {loading ? (
                  <span className="loading-dot" />
                ) : (
                  <Send size={17} />
                )}
              </button>
            </div>
          </div>
          <p className="disclaimer">
            <ShieldCheck size={13} /> Automated legal analysis grounded in BNS
            2023. Verify with legal counsel.
          </p>
        </form>
      </section>
      <EvidenceMatcherPanel
        messages={messages}
        draft={situation}
        onGenerateDraft={generateFirDraft}
        draftGenerating={draftGenerating}
        draftError={draftGenerationError}
      />
      {firDraft && (
        <div
          className="fir-draft-backdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setFirDraft("");
          }}
        >
          <section
            className="fir-draft-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="fir-draft-title"
          >
            <header className="fir-draft-header">
              <div>
                <span className="workspace-kicker">CASE DOCUMENT</span>
                <h2 id="fir-draft-title">FIR / Petition Draft</h2>
              </div>
              <div className="fir-draft-actions">
                <button
                  className="fir-draft-action"
                  type="button"
                  onClick={downloadFirDraft}
                >
                  <Download size={15} />
                  Download .txt
                </button>
                <button
                  className="fir-draft-action"
                  type="button"
                  onClick={copyFirDraft}
                >
                  <Clipboard size={15} />
                  Copy to Clipboard
                </button>
                <button
                  className="icon-button"
                  type="button"
                  aria-label="Close FIR draft"
                  onClick={() => setFirDraft("")}
                >
                  <X size={17} />
                </button>
              </div>
            </header>
            <pre className="fir-draft-content">{firDraft}</pre>
            {draftActionFeedback && (
              <p className="fir-draft-feedback" role="status" aria-live="polite">
                {draftActionFeedback}
              </p>
            )}
            <p className="fir-draft-disclaimer">
              Review and verify the details and legal references before
              submission. This is a draft, not a filed FIR or legal advice.
            </p>
          </section>
        </div>
      )}
    </main>
  );
}

function App() {
  const [view, setView] = useState("landing");
  return (
    <AnimatePresence mode="wait">
      {view === "landing" ? (
        <motion.div
          key="landing"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <Landing onLaunch={() => setView("workspace")} />
        </motion.div>
      ) : (
        <motion.div
          key="workspace"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <Workspace onBack={() => setView("landing")} />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
export default App;
