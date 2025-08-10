import type { FileData, UploadResponse, ApiResponse } from "../types/file";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(message: string, public status: number, public response?: any) {
    super(message);
    this.name = "ApiError";
  }
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_URL}${endpoint}`;

    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // If error response is not JSON, use default message
        }

        throw new ApiError(errorMessage, response.status, response);
      }

      // Handle empty responses
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return await response.json();
      }

      return {} as T;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        error instanceof Error ? error.message : "Network error",
        0
      );
    }
  }

  // File operations
  async getFiles(): Promise<FileData[]> {
    return this.request<FileData[]>("/api/v1/files");
  }

  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    return this.request<UploadResponse>("/api/v1/files/upload", {
      method: "POST",
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    });
  }

  async downloadFile(fileId: string): Promise<Blob> {
    const response = await fetch(`${API_URL}/api/v1/files/download/${fileId}`);

    if (!response.ok) {
      throw new ApiError(
        `Download failed: ${response.statusText}`,
        response.status
      );
    }

    return response.blob();
  }

  async deleteFile(fileId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/v1/files/${fileId}`, {
      method: "DELETE",
    });
  }

  async updateFileName(
    fileId: string,
    newName: string
  ): Promise<{ message: string }> {
    return this.request<{ message: string }>(
      `/api/v1/files/${fileId}?name=${encodeURIComponent(newName)}`,
      {
        method: "PUT",
      }
    );
  }

  // Health check
  async healthCheck(): Promise<{ status: string; database: string }> {
    return this.request<{ status: string; database: string }>("/health");
  }
}

export const apiService = new ApiService();
export { ApiError };
