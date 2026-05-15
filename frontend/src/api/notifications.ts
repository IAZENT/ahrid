import { apiClient } from "./client";
import type { NotificationDto, NotificationListResponse } from "../types/api";

export const notificationsApi = {
  async list(params?: { limit?: number; offset?: number; unread?: boolean }): Promise<NotificationListResponse> {
    const { data } = await apiClient.get<NotificationListResponse>(
      "/notifications", { params: { ...params, unread: params?.unread ? 1 : undefined } },
    );
    return data;
  },
  async unreadCount(): Promise<number> {
    const { data } = await apiClient.get<{ unread: number }>("/notifications/unread-count");
    return data.unread;
  },
  async markRead(id: string): Promise<NotificationDto> {
    const { data } = await apiClient.patch<NotificationDto>(`/notifications/${id}/read`);
    return data;
  },
  async markAllRead(): Promise<number> {
    const { data } = await apiClient.post<{ updated: number }>("/notifications/read-all");
    return data.updated;
  },
  async dismiss(id: string): Promise<void> {
    await apiClient.delete(`/notifications/${id}`);
  },
};
