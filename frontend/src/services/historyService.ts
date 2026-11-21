import api from "./api";

// Structure d'une conversation dans la liste
export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  last_message: string;
}

// Structure d'un message
export interface ConversationMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

// Structure d'une conversation complète
export interface ConversationDetail {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ConversationMessage[];
}

// Récupérer toutes les conversations
export async function getConversations(): Promise<Conversation[]> {
  const response = await api.get<Conversation[]>(
    "/api/v1/chat/conversations"
  );

  return response.data;
}

// Récupérer une conversation avec ses messages
export async function getConversation(
  conversationId: number
): Promise<ConversationDetail> {
  const response = await api.get<ConversationDetail>(
    `/api/v1/chat/conversations/${conversationId}`
  );

  return response.data;
}