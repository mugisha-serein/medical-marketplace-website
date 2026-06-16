import type { Role } from '../enums/Role'

export interface User {
  readonly id: string;
  readonly email: string;
  readonly role: Role;
  readonly name?: string;
  readonly avatarUrl?: string;
}
