import "@testing-library/jest-dom";
import { vi } from "vitest";

// Declare global for TypeScript
declare const global: any;

// Mock SvelteKit modules
vi.mock("$app/environment", () => ({
  browser: true,
  dev: false,
  building: false,
}));

vi.mock("$app/navigation", () => ({
  goto: vi.fn(),
  invalidate: vi.fn(),
  invalidateAll: vi.fn(),
  preloadData: vi.fn(),
  preloadCode: vi.fn(),
}));

vi.mock("$app/stores", () => ({
  page: { subscribe: vi.fn() },
  navigating: { subscribe: vi.fn() },
  updated: { subscribe: vi.fn() },
}));

// Mock fetch globally
(global as any).fetch = vi.fn();

// Mock window.URL.createObjectURL
Object.defineProperty(window, "URL", {
  value: {
    createObjectURL: vi.fn(() => "mocked-url"),
    revokeObjectURL: vi.fn(),
  },
  writable: true,
});

// Mock File and FileList
(global as any).File = class MockFile {
  name: string;
  size: number;
  type: string;

  constructor(bits: any[], name: string, options?: any) {
    this.name = name;
    this.size = bits.length;
    this.type = options?.type || "text/plain";
  }
} as any;

(global as any).FileList = class MockFileList {
  private files: File[];

  constructor(files: File[]) {
    this.files = files;
  }

  get length() {
    return this.files.length;
  }

  item(index: number) {
    return this.files[index] || null;
  }

  [Symbol.iterator]() {
    return this.files[Symbol.iterator]();
  }
} as any;
