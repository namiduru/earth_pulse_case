/// <reference types="vitest/globals" />

declare module "@testing-library/svelte" {
  export function render(component: any, options?: any): any;
  export const screen: any;
  export const fireEvent: any;
}

declare module "*.svelte" {
  import type { ComponentType } from "svelte";
  const component: ComponentType;
  export default component;
}
