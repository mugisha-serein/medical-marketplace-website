import { NotificationType } from '../enums/NotificationType'

export interface Notification {
  readonly id: string;
  readonly type: NotificationType;
  readonly message: string;
  readonly createdAt: string;
  readonly read: boolean;
  readonly meta?: Record<string, unknown>;
}
