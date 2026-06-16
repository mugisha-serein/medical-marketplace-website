export interface Equipment {
  readonly id: string;
  readonly productId?: string;
  readonly name: string;
  readonly description: string;
  readonly priceCents: number;
  readonly images: readonly string[];
  readonly categoryId: string;
  readonly vendorId: string;
  readonly stock: number;
  readonly specifications: Record<string, string>;
  readonly rating?: number;
  readonly condition?: 'new' | 'refurbished' | 'used';
}
