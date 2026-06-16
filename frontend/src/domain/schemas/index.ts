import { z } from 'zod';
import { Role } from '../enums/Role';

export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  role: z.nativeEnum(Role),
  name: z.string().min(2).optional(),
  avatarUrl: z.string().url().optional(),
});

export const EquipmentSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(3),
  description: z.string().min(10),
  priceCents: z.number().positive(),
  stock: z.number().nonnegative(),
  categoryId: z.string(),
  images: z.array(z.string().url()),
  vendorId: z.string().uuid(),
  rating: z.number().min(0).max(5).optional(),
  condition: z.enum(['new', 'refurbished', 'used']),
  specifications: z.record(z.string(), z.string()).optional(),
});

export type UserDTO = z.infer<typeof UserSchema>;
export type EquipmentDTO = z.infer<typeof EquipmentSchema>;
