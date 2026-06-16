export interface Vendor {
  readonly id: string;
  readonly name: string;
  readonly contactEmail: string;
  readonly logoUrl?: string;
  readonly rating: number;
  readonly isVerified: boolean;
}
