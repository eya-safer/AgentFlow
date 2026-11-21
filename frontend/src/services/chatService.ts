import api from "./api";

export interface ChatResponse {
  success: boolean;
  conversation_id: number;
  response: string;
  tools_used: string[];
  tool_results: unknown[];
}

export async function sendMessage(
  content: string,
  conversationId: number | null
): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>("/api/v1/chat/", {
    conversation_id: conversationId,
    content,
  });

  return response.data;
}