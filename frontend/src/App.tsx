
import ReactMarkdown from "react-markdown";
import { useState, useEffect, type FormEvent } from "react";
import {
  Bot,
  MessageSquare,
  History,
  ShieldCheck,
  Settings,
  Plus,
  Send,
  Sparkles,
  PanelLeftClose,
  CircleUserRound,
} from "lucide-react";
import {
  getApprovals,
  reviewApproval,
  type Approval,
} from "./services/approvalService";
import {
  getConversations,
  getConversation,
  type Conversation,
} from "./services/historyService";
import { sendMessage } from "./services/chatService";
import "./App.css";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function App() {
  const [activePage, setActivePage] = useState("Assistant");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  // Identifiant de la conversation sauvegardée dans SQLite
  const [conversationId, setConversationId] = useState<number | null>(null);

  // État de chargement et gestion des erreurs
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // Gestion des notifications à approuver
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [approvalsLoading, setApprovalsLoading] = useState(false);
  const [approvalError, setApprovalError] = useState("");
  const [reviewingId, setReviewingId] = useState<number | null>(null);

  // Gestion de l'historique
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");

  const navigation = [
    { name: "Assistant", icon: MessageSquare },
    { name: "Historique", icon: History },
    { name: "Approvals", icon: ShieldCheck },
  ];

  useEffect(() => {
  if (activePage === "Approvals") {
    loadApprovals();
  }
}, [activePage]);

  useEffect(() => {
    if (activePage === "Historique") {
      loadConversations();
    }
  }, [activePage]);

async function loadApprovals() {
  setApprovalsLoading(true);
  setApprovalError("");

  try {
    const data = await getApprovals();
    setApprovals(data);
  } catch (err) {
    console.error("Approvals API error:", err);
    setApprovalError("Impossible de charger les notifications.");
  } finally {
    setApprovalsLoading(false);
  }
}

  async function loadConversations() {
    setHistoryLoading(true);
    setHistoryError("");

    try {
      const data = await getConversations();
      setConversations(data);
    } catch (err) {
      console.error("History API error:", err);
      setHistoryError("Impossible de charger l'historique.");
    } finally {
      setHistoryLoading(false);
    }
  }

  async function openConversation(conversationId: number) {
    setHistoryLoading(true);
    setHistoryError("");

    try {
      const data = await getConversation(conversationId);

      // Restaurer les messages dans le Chat
      setMessages(
        data.messages.map((msg) => ({
          role: msg.role,
          content: msg.content,
        }))
      );

      // Restaurer l'identifiant pour continuer la conversation
      setConversationId(data.id);

      // Retourner automatiquement vers Assistant
      setActivePage("Assistant");
    } catch (err) {
      console.error("Open conversation error:", err);
      setHistoryError("Impossible d'ouvrir cette conversation.");
    } finally {
      setHistoryLoading(false);
    }
  }

  async function handleReview(
  approvalId: number,
  action: "approve" | "reject"
) {
  setReviewingId(approvalId);
  setApprovalError("");

  try {
    const updatedApproval = await reviewApproval(approvalId, action);

    setApprovals((previous) =>
      previous.map((approval) =>
        approval.id === approvalId ? updatedApproval : approval
      )
    );
  } catch (err) {
    console.error("Approval review error:", err);
    setApprovalError("Impossible de mettre à jour cette notification.");
  } finally {
    setReviewingId(null);
  }
}

  async function handleSend(e: FormEvent) {
    e.preventDefault();

    const content = message.trim();

    if (!content || isLoading) return;

    // Afficher immédiatement le message de l'utilisateur
    setMessages((previous) => [
      ...previous,
      { role: "user", content },
    ]);

    setMessage("");
    setError("");
    setIsLoading(true);

    try {
      // Envoyer le message au backend FastAPI
      const data = await sendMessage(content, conversationId);

      // Conserver l'identifiant pour les prochains messages
      setConversationId(data.conversation_id);

      // Afficher la réponse réelle de l'agent Gemini
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.response,
        },
      ]);

    } catch (err) {
      console.error("Chat API error:", err);

      setError(
        "Impossible de contacter AgentFlow. Vérifiez que le backend est lancé."
      );

    } finally {
      setIsLoading(false);
    }
  }

  function handleNewConversation() {
    setMessages([]);
    setConversationId(null);
    setMessage("");
    setError("");
    setIsLoading(false);
    setActivePage("Assistant");
  }

  return (
    <div className="app-container">

      {/* SIDEBAR */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">
            <Bot size={25} />
          </div>
          <span>Agent<span className="brand-highlight">Flow</span></span>
          <PanelLeftClose className="sidebar-toggle" size={19} />
        </div>

        <button
          className="new-chat"
          onClick={handleNewConversation}
        >
          <Plus size={18} />
          New conversation
        </button>

        <div className="nav-section">
          <p className="section-label">WORKSPACE</p>

          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.name}
                className={`nav-item ${
                  activePage === item.name ? "active" : ""
                }`}
                onClick={() => setActivePage(item.name)}
              >
                <Icon size={19} />
                <span>{item.name}</span>
              </button>
            );
          })}
        </div>

        <div className="sidebar-bottom">
          <button className="nav-item">
            <Settings size={19} />
            <span>Settings</span>
          </button>

          <div className="profile">
            <div className="avatar">
              <CircleUserRound size={23} />
            </div>
            <div>
              <p className="profile-name">Administrator</p>
              <p className="profile-role">Workspace account</p>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">

        <header className="topbar">
          <div>
            <p className="breadcrumb">Workspace / {activePage}</p>
            <h2>{activePage}</h2>
          </div>

          <div className="assistant-status">
            <span className="status-dot"></span>
            AI Assistant
          </div>
        </header>

        {activePage === "Assistant" && (
          <section className="chat-area">

            <div className="chat-content">

              {messages.length === 0 ? (
                <div className="welcome">
                  <div className="welcome-icon">
                    <Sparkles size={30} />
                  </div>

                  <p className="welcome-label">
                    YOUR AI BUSINESS ASSISTANT
                  </p>

                  <h1>
                    How can I help you <span>today?</span>
                  </h1>

                  <p className="welcome-description">
                    Manage customers, track orders and prepare
                    business notifications with AgentFlow.
                  </p>

                  <div className="suggestions">
                    <div className="suggestion-card">
                      <MessageSquare size={20} />
                      <h3>Customer information</h3>
                      <p>Retrieve customer details from your database.</p>
                    </div>

                    <div className="suggestion-card">
                      <History size={20} />
                      <h3>Order tracking</h3>
                      <p>Check order status and customer orders.</p>
                    </div>

                    <div className="suggestion-card">
                      <ShieldCheck size={20} />
                      <h3>Notifications</h3>
                      <p>Prepare notifications for human approval.</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="messages">
                  {messages.map((msg, index) => (
                    <div
                      key={index}
                      className={`message ${msg.role}`}
                    >
                      <div className="message-avatar">
                        {msg.role === "user" ? (
                          <CircleUserRound size={20} />
                        ) : (
                          <Bot size={20} />
                        )}
                      </div>

                      <div className="message-content">
                        <strong>
                          {msg.role === "user" ? "You" : "AgentFlow"}
                        </strong>
                        <ReactMarkdown>
                          {msg.content.replace(/\\([*`_])/g, "$1")}
                        </ReactMarkdown>
                      </div>
                    </div>
                  ))}

                  {isLoading && (
                    <div className="message assistant">
                      <div className="message-avatar">
                        <Bot size={20} />
                      </div>
                      <div className="message-content">
                        <strong>AgentFlow</strong>
                        <p>Thinking...</p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {error && (
                <p className="chat-error">{error}</p>
              )}

            </div>

            <div className="input-container">
              <form onSubmit={handleSend} className="chat-form">
                <input
                  type="text"
                  placeholder="Ask AgentFlow anything..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  disabled={isLoading}
                />

                <button
                  type="submit"
                  disabled={!message.trim() || isLoading}
                  className="send-button"
                >
                  <Send size={19} />
                </button>
              </form>

              <p className="input-hint">
                AgentFlow can make mistakes. Verify important information.
              </p>
            </div>

          </section>
        )}

        {activePage === "Historique" && (
          <section className="history-page">
            <div className="history-header">
              <div>
                <h2>Conversation History</h2>
                <p>Access and continue your previous conversations.</p>
              </div>

              <button
                className="refresh-button"
                onClick={loadConversations}
                disabled={historyLoading}
              >
                {historyLoading ? "Loading..." : "Refresh"}
              </button>
            </div>

            {historyError && (
              <p className="approval-error">{historyError}</p>
            )}

            {historyLoading ? (
              <div className="approval-empty">
                Loading conversations...
              </div>
            ) : conversations.length === 0 ? (
              <div className="approval-empty">
                <History size={38} />
                <h3>No conversations yet</h3>
                <p>Your saved conversations will appear here.</p>
              </div>
            ) : (
              <div className="history-list">
                {conversations.map((conversation) => (
                  <button
                    key={conversation.id}
                    className="history-card"
                    onClick={() => openConversation(conversation.id)}
                  >
                    <div className="history-icon">
                      <MessageSquare size={21} />
                    </div>

                    <div className="history-info">
                      <h3>
                        {conversation.title ||
                          `Conversation #${conversation.id}`}
                      </h3>

                      <p>{conversation.last_message || "No messages"}</p>

                      <span>
                        {new Date(conversation.updated_at).toLocaleString()}
                      </span>
                    </div>

                    <div className="history-arrow">
                      <History size={18} />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </section>
        )}

        {activePage === "Approvals" && (
          <section className="approvals-page">
            <div className="approvals-header">
              <div>
                <h2>Approval Center</h2>
                <p>Review notifications prepared by AgentFlow before approval.</p>
              </div>

              <button
                className="refresh-button"
                onClick={loadApprovals}
                disabled={approvalsLoading}
              >
                {approvalsLoading ? "Loading..." : "Refresh"}
              </button>
            </div>

            <div className="approval-stats">
              <div className="approval-stat">
                <span>Total notifications</span>
                <strong>{approvals.length}</strong>
              </div>

              <div className="approval-stat">
                <span>Pending</span>
                <strong>
                  {approvals.filter((a) => a.status === "pending").length}
                </strong>
              </div>

              <div className="approval-stat">
                <span>Approved</span>
                <strong>
                  {approvals.filter((a) => a.status === "approved").length}
                </strong>
              </div>

              <div className="approval-stat">
                <span>Rejected</span>
                <strong>
                  {approvals.filter((a) => a.status === "rejected").length}
                </strong>
              </div>
            </div>

            {approvalError && (
              <p className="approval-error">{approvalError}</p>
            )}

            {approvalsLoading ? (
              <div className="approval-empty">
                Loading notifications...
              </div>
            ) : approvals.length === 0 ? (
              <div className="approval-empty">
                <ShieldCheck size={38} />
                <h3>No notifications yet</h3>
                <p>Notifications prepared by AgentFlow will appear here.</p>
              </div>
            ) : (
              <div className="approval-list">
                {approvals.map((approval) => (
                  <article className="approval-card" key={approval.id}>
                    <div className="approval-card-header">
                      <div>
                        <h3>Notification #{approval.id}</h3>
                        <span>Customer ID: {approval.customer_id}</span>
                      </div>

                      <span className={`approval-status ${approval.status}`}>
                        {approval.status}
                      </span>
                    </div>

                    <div className="approval-details">
                      <p>
                        <strong>Recipient:</strong> {approval.recipient_email}
                      </p>

                      <p>
                        <strong>Created:</strong>{" "}
                        {new Date(approval.created_at).toLocaleString()}
                      </p>

                      <div className="approval-message">
                        <strong>Message:</strong>
                        <p>{approval.message}</p>
                      </div>
                    </div>

                    {approval.status === "pending" && (
                      <div className="approval-actions">
                        <button
                          className="approve-button"
                          onClick={() => handleReview(approval.id, "approve")}
                          disabled={reviewingId !== null}
                        >
                          {reviewingId === approval.id
                            ? "Processing..."
                            : "Approve"}
                        </button>

                        <button
                          className="reject-button"
                          onClick={() => handleReview(approval.id, "reject")}
                          disabled={reviewingId !== null}
                        >
                          {reviewingId === approval.id
                            ? "Processing..."
                            : "Reject"}
                        </button>
                      </div>
                    )}
                  </article>
                ))}
              </div>
            )}
          </section>
        )}

      </main>
    </div>
  );
}
