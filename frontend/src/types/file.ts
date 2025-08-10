export interface FileData {
  file_id: string;
  name: string;
  size: number;
  content_type: string;
  upload_date: string;
  extension: string;
  _id?: string;
}

export interface UploadResponse {
  message: string;
  file: FileData;
}

export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
}

export interface Message {
  text: string;
  type: "success" | "error" | "warning" | "info";
  id: string;
}

export interface FileUploadState {
  isUploading: boolean;
  progress: number;
  fileName?: string;
}

export interface FileEditState {
  editingFileId: string | null;
  editingName: string;
}
