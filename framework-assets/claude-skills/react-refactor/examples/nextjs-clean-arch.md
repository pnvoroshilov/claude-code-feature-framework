# Next.js Clean Architecture Example

**Complete Next.js 14+ application structure with Clean Architecture, App Router, Server Components, and TypeScript.**

## Overview

This example demonstrates Clean Architecture implementation in Next.js with:

nextjs_features[8]{feature,architecture_layer,implementation}:
App Router,Presentation,Route groups and layouts
Server Components,Presentation + Application,Data fetching at server
Client Components,Presentation,Interactive UI
Server Actions,Application,Mutations and form handling
Route Handlers,Infrastructure,API endpoints
Middleware,Infrastructure,Auth and redirects
Streaming,Presentation,Suspense boundaries
Caching,Infrastructure,Data cache and revalidation

---

## Project Structure

```
src/
├── app/                          # Next.js App Router (Presentation entry)
│   ├── (auth)/                   # Route group for auth pages
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── (dashboard)/              # Route group for authenticated pages
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── orders/
│   │       ├── page.tsx
│   │       ├── [id]/
│   │       │   └── page.tsx
│   │       └── loading.tsx
│   ├── api/                      # Route Handlers (Infrastructure)
│   │   └── orders/
│   │       └── route.ts
│   ├── layout.tsx
│   └── page.tsx
│
├── domain/                       # Domain Layer (Zero dependencies)
│   ├── entities/
│   │   ├── User.ts
│   │   ├── Order.ts
│   │   └── Product.ts
│   ├── types/
│   │   └── index.ts
│   └── rules/
│       ├── OrderRules.ts
│       └── UserRules.ts
│
├── application/                  # Application Layer
│   ├── ports/                    # Interfaces (Ports)
│   │   ├── UserRepository.ts
│   │   ├── OrderRepository.ts
│   │   └── AuthService.ts
│   ├── use-cases/                # Server-side use cases
│   │   ├── orders/
│   │   │   ├── GetOrders.ts
│   │   │   ├── CreateOrder.ts
│   │   │   └── UpdateOrderStatus.ts
│   │   └── auth/
│   │       ├── Login.ts
│   │       └── Register.ts
│   ├── hooks/                    # Client-side hooks
│   │   ├── useOrders.ts
│   │   ├── useAuth.ts
│   │   └── useCart.ts
│   └── actions/                  # Server Actions
│       ├── orderActions.ts
│       └── authActions.ts
│
├── infrastructure/               # Infrastructure Layer
│   ├── database/
│   │   ├── prisma/
│   │   │   └── schema.prisma
│   │   └── repositories/
│   │       ├── PrismaUserRepository.ts
│   │       └── PrismaOrderRepository.ts
│   ├── api/
│   │   ├── ApiOrderRepository.ts
│   │   └── httpClient.ts
│   ├── auth/
│   │   └── NextAuthService.ts
│   └── cache/
│       └── redis.ts
│
├── presentation/                 # Presentation Layer
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Spinner.tsx
│   │   ├── orders/
│   │   │   ├── OrderList.tsx
│   │   │   ├── OrderCard.tsx
│   │   │   └── OrderForm.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   └── providers/
│       ├── AuthProvider.tsx
│       └── QueryProvider.tsx
│
└── lib/                          # Shared utilities
    ├── di/                       # Dependency injection
    │   └── container.ts
    └── utils/
        └── formatters.ts
```

---

## Domain Layer

### Entities

```typescript
// src/domain/entities/Order.ts
export interface Order {
  id: string;
  userId: string;
  items: OrderItem[];
  status: OrderStatus;
  shippingAddress: Address;
  total: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface OrderItem {
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  subtotal: number;
}

export type OrderStatus =
  | 'pending'
  | 'confirmed'
  | 'processing'
  | 'shipped'
  | 'delivered'
  | 'cancelled';

export interface Address {
  street: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
}

// src/domain/entities/User.ts
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  createdAt: Date;
}

export type UserRole = 'admin' | 'customer' | 'guest';
```

### Business Rules

```typescript
// src/domain/rules/OrderRules.ts
import { Order, OrderItem, OrderStatus } from '../entities/Order';

export function calculateOrderTotal(items: OrderItem[]): number {
  return items.reduce((sum, item) => sum + item.subtotal, 0);
}

export function calculateItemSubtotal(
  quantity: number,
  unitPrice: number
): number {
  return quantity * unitPrice;
}

export function canCancelOrder(order: Order): boolean {
  const cancellableStatuses: OrderStatus[] = ['pending', 'confirmed'];
  return cancellableStatuses.includes(order.status);
}

export function canUpdateOrderStatus(
  currentStatus: OrderStatus,
  newStatus: OrderStatus
): boolean {
  const transitions: Record<OrderStatus, OrderStatus[]> = {
    pending: ['confirmed', 'cancelled'],
    confirmed: ['processing', 'cancelled'],
    processing: ['shipped', 'cancelled'],
    shipped: ['delivered'],
    delivered: [],
    cancelled: [],
  };

  return transitions[currentStatus]?.includes(newStatus) ?? false;
}

export function validateOrder(order: Partial<Order>): string[] {
  const errors: string[] = [];

  if (!order.items?.length) {
    errors.push('Order must have at least one item');
  }

  if (!order.shippingAddress) {
    errors.push('Shipping address is required');
  }

  return errors;
}
```

---

## Application Layer

### Ports (Interfaces)

```typescript
// src/application/ports/OrderRepository.ts
import { Order, OrderStatus } from '@/domain/entities/Order';

export interface OrderFilters {
  userId?: string;
  status?: OrderStatus;
  dateFrom?: Date;
  dateTo?: Date;
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  findAll(
    filters: OrderFilters,
    page: number,
    pageSize: number
  ): Promise<PaginatedResult<Order>>;
  findByUserId(userId: string): Promise<Order[]>;
  create(order: Omit<Order, 'id' | 'createdAt' | 'updatedAt'>): Promise<Order>;
  update(id: string, data: Partial<Order>): Promise<Order>;
  updateStatus(id: string, status: OrderStatus): Promise<Order>;
  delete(id: string): Promise<void>;
}
```

### Use Cases (Server-side)

```typescript
// src/application/use-cases/orders/GetOrders.ts
import { Order } from '@/domain/entities/Order';
import {
  OrderRepository,
  OrderFilters,
  PaginatedResult,
} from '@/application/ports/OrderRepository';

export class GetOrdersUseCase {
  constructor(private orderRepository: OrderRepository) {}

  async execute(
    filters: OrderFilters,
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResult<Order>> {
    return this.orderRepository.findAll(filters, page, pageSize);
  }
}

// src/application/use-cases/orders/CreateOrder.ts
import { Order, OrderItem } from '@/domain/entities/Order';
import { OrderRepository } from '@/application/ports/OrderRepository';
import {
  calculateOrderTotal,
  validateOrder,
} from '@/domain/rules/OrderRules';

export interface CreateOrderInput {
  userId: string;
  items: Omit<OrderItem, 'subtotal'>[];
  shippingAddress: Order['shippingAddress'];
}

export class CreateOrderUseCase {
  constructor(private orderRepository: OrderRepository) {}

  async execute(input: CreateOrderInput): Promise<Order> {
    // Calculate subtotals for each item
    const itemsWithSubtotal: OrderItem[] = input.items.map((item) => ({
      ...item,
      subtotal: item.quantity * item.unitPrice,
    }));

    // Calculate total
    const total = calculateOrderTotal(itemsWithSubtotal);

    // Prepare order data
    const orderData: Omit<Order, 'id' | 'createdAt' | 'updatedAt'> = {
      userId: input.userId,
      items: itemsWithSubtotal,
      shippingAddress: input.shippingAddress,
      status: 'pending',
      total,
    };

    // Validate
    const errors = validateOrder(orderData);
    if (errors.length > 0) {
      throw new Error(`Validation failed: ${errors.join(', ')}`);
    }

    // Create order
    return this.orderRepository.create(orderData);
  }
}

// src/application/use-cases/orders/UpdateOrderStatus.ts
import { Order, OrderStatus } from '@/domain/entities/Order';
import { OrderRepository } from '@/application/ports/OrderRepository';
import { canUpdateOrderStatus } from '@/domain/rules/OrderRules';

export class UpdateOrderStatusUseCase {
  constructor(private orderRepository: OrderRepository) {}

  async execute(orderId: string, newStatus: OrderStatus): Promise<Order> {
    const order = await this.orderRepository.findById(orderId);

    if (!order) {
      throw new Error('Order not found');
    }

    if (!canUpdateOrderStatus(order.status, newStatus)) {
      throw new Error(
        `Cannot transition from ${order.status} to ${newStatus}`
      );
    }

    return this.orderRepository.updateStatus(orderId, newStatus);
  }
}
```

### Server Actions

```typescript
// src/application/actions/orderActions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { getContainer } from '@/lib/di/container';
import { CreateOrderUseCase, CreateOrderInput } from '../use-cases/orders/CreateOrder';
import { UpdateOrderStatusUseCase } from '../use-cases/orders/UpdateOrderStatus';
import { OrderStatus } from '@/domain/entities/Order';

export async function createOrder(formData: FormData) {
  const container = getContainer();
  const createOrderUseCase = container.resolve(CreateOrderUseCase);

  const input: CreateOrderInput = {
    userId: formData.get('userId') as string,
    items: JSON.parse(formData.get('items') as string),
    shippingAddress: {
      street: formData.get('street') as string,
      city: formData.get('city') as string,
      state: formData.get('state') as string,
      postalCode: formData.get('postalCode') as string,
      country: formData.get('country') as string,
    },
  };

  try {
    const order = await createOrderUseCase.execute(input);
    revalidatePath('/orders');
    redirect(`/orders/${order.id}`);
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to create order',
    };
  }
}

export async function updateOrderStatus(
  orderId: string,
  status: OrderStatus
) {
  const container = getContainer();
  const updateStatusUseCase = container.resolve(UpdateOrderStatusUseCase);

  try {
    await updateStatusUseCase.execute(orderId, status);
    revalidatePath(`/orders/${orderId}`);
    revalidatePath('/orders');
    return { success: true };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to update status',
    };
  }
}
```

### Client Hooks

```typescript
// src/application/hooks/useOrders.ts
'use client';

import { useState, useEffect, useCallback, useTransition } from 'react';
import { Order, OrderStatus } from '@/domain/entities/Order';
import { updateOrderStatus } from '../actions/orderActions';

interface UseOrdersResult {
  orders: Order[];
  loading: boolean;
  error: Error | null;
  updateStatus: (orderId: string, status: OrderStatus) => Promise<void>;
  isUpdating: boolean;
}

export function useOrders(initialOrders: Order[]): UseOrdersResult {
  const [orders, setOrders] = useState(initialOrders);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [isPending, startTransition] = useTransition();

  const handleUpdateStatus = useCallback(
    async (orderId: string, status: OrderStatus) => {
      startTransition(async () => {
        const result = await updateOrderStatus(orderId, status);

        if (result.error) {
          setError(new Error(result.error));
        } else {
          // Optimistic update
          setOrders((prev) =>
            prev.map((order) =>
              order.id === orderId ? { ...order, status } : order
            )
          );
        }
      });
    },
    []
  );

  return {
    orders,
    loading,
    error,
    updateStatus: handleUpdateStatus,
    isUpdating: isPending,
  };
}
```

---

## Infrastructure Layer

### Database Repository

```typescript
// src/infrastructure/database/repositories/PrismaOrderRepository.ts
import { PrismaClient } from '@prisma/client';
import { Order, OrderStatus } from '@/domain/entities/Order';
import {
  OrderRepository,
  OrderFilters,
  PaginatedResult,
} from '@/application/ports/OrderRepository';

export class PrismaOrderRepository implements OrderRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string): Promise<Order | null> {
    const order = await this.prisma.order.findUnique({
      where: { id },
      include: { items: true },
    });

    return order ? this.mapToDomain(order) : null;
  }

  async findAll(
    filters: OrderFilters,
    page: number,
    pageSize: number
  ): Promise<PaginatedResult<Order>> {
    const where = this.buildWhereClause(filters);

    const [items, total] = await Promise.all([
      this.prisma.order.findMany({
        where,
        include: { items: true },
        skip: (page - 1) * pageSize,
        take: pageSize,
        orderBy: { createdAt: 'desc' },
      }),
      this.prisma.order.count({ where }),
    ]);

    return {
      items: items.map(this.mapToDomain),
      total,
      page,
      pageSize,
    };
  }

  async findByUserId(userId: string): Promise<Order[]> {
    const orders = await this.prisma.order.findMany({
      where: { userId },
      include: { items: true },
      orderBy: { createdAt: 'desc' },
    });

    return orders.map(this.mapToDomain);
  }

  async create(
    data: Omit<Order, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<Order> {
    const order = await this.prisma.order.create({
      data: {
        userId: data.userId,
        status: data.status,
        total: data.total,
        shippingAddress: data.shippingAddress,
        items: {
          create: data.items,
        },
      },
      include: { items: true },
    });

    return this.mapToDomain(order);
  }

  async update(id: string, data: Partial<Order>): Promise<Order> {
    const order = await this.prisma.order.update({
      where: { id },
      data: {
        status: data.status,
        shippingAddress: data.shippingAddress,
      },
      include: { items: true },
    });

    return this.mapToDomain(order);
  }

  async updateStatus(id: string, status: OrderStatus): Promise<Order> {
    return this.update(id, { status });
  }

  async delete(id: string): Promise<void> {
    await this.prisma.order.delete({ where: { id } });
  }

  private buildWhereClause(filters: OrderFilters) {
    const where: any = {};

    if (filters.userId) where.userId = filters.userId;
    if (filters.status) where.status = filters.status;
    if (filters.dateFrom || filters.dateTo) {
      where.createdAt = {};
      if (filters.dateFrom) where.createdAt.gte = filters.dateFrom;
      if (filters.dateTo) where.createdAt.lte = filters.dateTo;
    }

    return where;
  }

  private mapToDomain(prismaOrder: any): Order {
    return {
      id: prismaOrder.id,
      userId: prismaOrder.userId,
      items: prismaOrder.items,
      status: prismaOrder.status as OrderStatus,
      shippingAddress: prismaOrder.shippingAddress,
      total: prismaOrder.total,
      createdAt: prismaOrder.createdAt,
      updatedAt: prismaOrder.updatedAt,
    };
  }
}
```

### Dependency Injection

```typescript
// src/lib/di/container.ts
import { PrismaClient } from '@prisma/client';
import { PrismaOrderRepository } from '@/infrastructure/database/repositories/PrismaOrderRepository';
import { GetOrdersUseCase } from '@/application/use-cases/orders/GetOrders';
import { CreateOrderUseCase } from '@/application/use-cases/orders/CreateOrder';
import { UpdateOrderStatusUseCase } from '@/application/use-cases/orders/UpdateOrderStatus';

class Container {
  private static instance: Container;
  private prisma: PrismaClient;
  private orderRepository: PrismaOrderRepository;

  private constructor() {
    this.prisma = new PrismaClient();
    this.orderRepository = new PrismaOrderRepository(this.prisma);
  }

  static getInstance(): Container {
    if (!Container.instance) {
      Container.instance = new Container();
    }
    return Container.instance;
  }

  resolve<T>(UseCaseClass: new (...args: any[]) => T): T {
    switch (UseCaseClass.name) {
      case 'GetOrdersUseCase':
        return new GetOrdersUseCase(this.orderRepository) as T;
      case 'CreateOrderUseCase':
        return new CreateOrderUseCase(this.orderRepository) as T;
      case 'UpdateOrderStatusUseCase':
        return new UpdateOrderStatusUseCase(this.orderRepository) as T;
      default:
        throw new Error(`Unknown use case: ${UseCaseClass.name}`);
    }
  }
}

export function getContainer(): Container {
  return Container.getInstance();
}
```

---

## Presentation Layer (App Router)

### Server Component Page

```tsx
// src/app/(dashboard)/orders/page.tsx
import { Suspense } from 'react';
import { getContainer } from '@/lib/di/container';
import { GetOrdersUseCase } from '@/application/use-cases/orders/GetOrders';
import { OrderList } from '@/presentation/components/orders/OrderList';
import { OrderListSkeleton } from '@/presentation/components/orders/OrderListSkeleton';

interface OrdersPageProps {
  searchParams: {
    page?: string;
    status?: string;
  };
}

async function OrdersData({ searchParams }: OrdersPageProps) {
  const container = getContainer();
  const getOrdersUseCase = container.resolve(GetOrdersUseCase);

  const page = Number(searchParams.page) || 1;
  const status = searchParams.status || undefined;

  const result = await getOrdersUseCase.execute({ status }, page, 20);

  return (
    <OrderList
      initialOrders={result.items}
      totalPages={Math.ceil(result.total / result.pageSize)}
      currentPage={page}
    />
  );
}

export default function OrdersPage({ searchParams }: OrdersPageProps) {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Orders</h1>

      <Suspense fallback={<OrderListSkeleton />}>
        <OrdersData searchParams={searchParams} />
      </Suspense>
    </div>
  );
}
```

### Client Component

```tsx
// src/presentation/components/orders/OrderList.tsx
'use client';

import { memo } from 'react';
import { Order } from '@/domain/entities/Order';
import { useOrders } from '@/application/hooks/useOrders';
import { OrderCard } from './OrderCard';
import { Pagination } from '../common/Pagination';

interface OrderListProps {
  initialOrders: Order[];
  totalPages: number;
  currentPage: number;
}

export const OrderList = memo<OrderListProps>(function OrderList({
  initialOrders,
  totalPages,
  currentPage,
}) {
  const { orders, updateStatus, isUpdating, error } = useOrders(initialOrders);

  if (error) {
    return <div className="text-red-500">Error: {error.message}</div>;
  }

  return (
    <div>
      <div className="grid gap-4">
        {orders.map((order) => (
          <OrderCard
            key={order.id}
            order={order}
            onStatusChange={(status) => updateStatus(order.id, status)}
            disabled={isUpdating}
          />
        ))}
      </div>

      <Pagination totalPages={totalPages} currentPage={currentPage} />
    </div>
  );
});

// src/presentation/components/orders/OrderCard.tsx
'use client';

import { memo } from 'react';
import Link from 'next/link';
import { Order, OrderStatus } from '@/domain/entities/Order';
import { canUpdateOrderStatus } from '@/domain/rules/OrderRules';
import { formatCurrency, formatDate } from '@/lib/utils/formatters';

interface OrderCardProps {
  order: Order;
  onStatusChange: (status: OrderStatus) => void;
  disabled?: boolean;
}

const STATUS_OPTIONS: OrderStatus[] = [
  'pending',
  'confirmed',
  'processing',
  'shipped',
  'delivered',
  'cancelled',
];

export const OrderCard = memo<OrderCardProps>(function OrderCard({
  order,
  onStatusChange,
  disabled,
}) {
  const availableStatuses = STATUS_OPTIONS.filter((status) =>
    canUpdateOrderStatus(order.status, status)
  );

  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm">
      <div className="flex justify-between items-start">
        <div>
          <Link
            href={`/orders/${order.id}`}
            className="text-lg font-semibold hover:underline"
          >
            Order #{order.id.slice(0, 8)}
          </Link>
          <p className="text-gray-600">{formatDate(order.createdAt)}</p>
        </div>

        <div className="text-right">
          <p className="text-xl font-bold">{formatCurrency(order.total)}</p>
          <span
            className={`inline-block px-2 py-1 rounded text-sm ${getStatusColor(order.status)}`}
          >
            {order.status}
          </span>
        </div>
      </div>

      <div className="mt-4">
        <p className="text-sm text-gray-600">
          {order.items.length} item(s)
        </p>

        {availableStatuses.length > 0 && (
          <div className="mt-2 flex gap-2">
            {availableStatuses.map((status) => (
              <button
                key={status}
                onClick={() => onStatusChange(status)}
                disabled={disabled}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-100 disabled:opacity-50"
              >
                Mark as {status}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
});

function getStatusColor(status: OrderStatus): string {
  const colors: Record<OrderStatus, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-blue-100 text-blue-800',
    processing: 'bg-purple-100 text-purple-800',
    shipped: 'bg-indigo-100 text-indigo-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
  };
  return colors[status];
}
```

### Layout with Providers

```tsx
// src/app/(dashboard)/layout.tsx
import { ReactNode } from 'react';
import { Header } from '@/presentation/components/layout/Header';
import { Sidebar } from '@/presentation/components/layout/Sidebar';
import { AuthProvider } from '@/presentation/providers/AuthProvider';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 p-6">{children}</main>
        </div>
      </div>
    </AuthProvider>
  );
}
```

---

## Key Patterns Summary

nextjs_clean_arch_patterns[10]{pattern,layer,purpose}:
Server Components for Data,Presentation,Fetch data at server without client JS
Client Components for Interaction,Presentation,Handle user events and state
Server Actions for Mutations,Application,Form handling with server validation
Use Cases for Business Logic,Application,Encapsulate business rules
Repository Pattern,Infrastructure,Abstract data access
Dependency Injection,Infrastructure,Decouple implementations
Domain Rules,Domain,Pure business logic functions
Streaming with Suspense,Presentation,Progressive loading
Route Handlers for API,Infrastructure,External API endpoints
Middleware for Auth,Infrastructure,Request interceptors

---

## Testing Strategy

```typescript
// __tests__/application/use-cases/CreateOrder.test.ts
import { CreateOrderUseCase } from '@/application/use-cases/orders/CreateOrder';
import { OrderRepository } from '@/application/ports/OrderRepository';

describe('CreateOrderUseCase', () => {
  let mockRepository: jest.Mocked<OrderRepository>;
  let useCase: CreateOrderUseCase;

  beforeEach(() => {
    mockRepository = {
      create: jest.fn(),
      findById: jest.fn(),
      findAll: jest.fn(),
      findByUserId: jest.fn(),
      update: jest.fn(),
      updateStatus: jest.fn(),
      delete: jest.fn(),
    };
    useCase = new CreateOrderUseCase(mockRepository);
  });

  it('calculates total correctly', async () => {
    const input = {
      userId: 'user-1',
      items: [
        { productId: 'p1', productName: 'Item', quantity: 2, unitPrice: 10 },
      ],
      shippingAddress: {
        street: '123 Main',
        city: 'City',
        state: 'ST',
        postalCode: '12345',
        country: 'US',
      },
    };

    mockRepository.create.mockResolvedValue({
      id: 'order-1',
      ...input,
      items: [{ ...input.items[0], subtotal: 20 }],
      status: 'pending',
      total: 20,
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    const result = await useCase.execute(input);

    expect(result.total).toBe(20);
    expect(mockRepository.create).toHaveBeenCalledWith(
      expect.objectContaining({ total: 20 })
    );
  });
});
```

---

**File Size**: ~480 lines
**Reference**: Use with `reference/clean-architecture.md` for architectural principles
