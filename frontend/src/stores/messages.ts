import { writable } from "svelte/store";
import type { Message } from "../types/file";

export const messages = writable<Message[]>([]);

export const messageActions = {
  add(text: string, type: Message["type"] = "info", duration: number = 5000) {
    const id = crypto.randomUUID();
    const message: Message = { text, type, id };

    messages.update((msgs) => [...msgs, message]);

    // Auto-remove message after duration
    if (duration > 0) {
      setTimeout(() => {
        this.remove(id);
      }, duration);
    }

    return id;
  },

  remove(id: string) {
    messages.update((msgs) => msgs.filter((msg) => msg.id !== id));
  },

  clear() {
    messages.set([]);
  },

  success(text: string, duration?: number) {
    return this.add(text, "success", duration);
  },

  error(text: string, duration?: number) {
    return this.add(text, "error", duration);
  },

  warning(text: string, duration?: number) {
    return this.add(text, "warning", duration);
  },

  info(text: string, duration?: number) {
    return this.add(text, "info", duration);
  },
};
