export interface CartItem {
  readonly equipmentId: string;
  readonly name: string;
  readonly vendorId: string;
  readonly quantity: number;
  readonly unitPrice: number;
  readonly thumbnailUrl?: string;
}
