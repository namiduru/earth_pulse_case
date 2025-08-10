/**
 * Format file size in human-readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

/**
 * Format date in a user-friendly format
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

  if (diffInHours < 24) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } else if (diffInHours < 168) {
    // 7 days
    return date.toLocaleDateString([], { weekday: "short" });
  } else {
    return date.toLocaleDateString([], { month: "short", day: "numeric" });
  }
}

/**
 * Get file icon based on file type
 */
export function getFileIcon(contentType: string): string {
  if (contentType.startsWith("image/")) {
    return "📷";
  } else if (contentType.startsWith("video/")) {
    return "🎥";
  } else if (contentType.startsWith("audio/")) {
    return "🎵";
  } else if (contentType.includes("pdf")) {
    return "📄";
  } else if (contentType.includes("zip") || contentType.includes("rar")) {
    return "📦";
  } else if (
    contentType.includes("text/") ||
    contentType.includes("json") ||
    contentType.includes("xml")
  ) {
    return "📝";
  } else {
    return "📁";
  }
}

/**
 * Sanitize filename for display
 */
export function sanitizeFilename(
  filename: string,
  maxLength: number = 50
): string {
  if (filename.length <= maxLength) {
    return filename;
  }

  const extension = filename.split(".").pop();
  const name = filename.substring(0, filename.lastIndexOf("."));
  const maxNameLength = maxLength - (extension ? extension.length + 1 : 0);

  return (
    name.substring(0, maxNameLength) +
    "..." +
    (extension ? "." + extension : "")
  );
}
