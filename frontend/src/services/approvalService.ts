import api from "./api";

export interface Approval {
  id: number;
  customer_id: number;
  recipient_email: string;
  message: string;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  reviewed_at: string | null;
}

// Récupérer toutes les notifications
export async function getApprovals(): Promise<Approval[]> {
  const response = await api.get<Approval[]>("/api/v1/approvals/");
  return response.data;
}

// Approuver ou rejeter une notification
export async function reviewApproval(
  approvalId: number,
  action: "approve" | "reject"
): Promise<Approval> {
  const response = await api.post<Approval>(
    `/api/v1/approvals/${approvalId}/${action}`
  );

  return response.data;
}