export interface ApiValidationErrorItem {
  msg?: string;
}

interface ApiErrorShape {
  response?: {
    data?: {
      detail?: string | ApiValidationErrorItem[];
      error?: string;
    };
  };
  message?: string;
}

export function isNetworkError(error: unknown): boolean {
  const apiError = error as ApiErrorShape;
  return !apiError.response;
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  const apiError = error as ApiErrorShape;
  const detail = apiError.response?.data?.detail;
  const errorText = apiError.response?.data?.error;

  if (typeof errorText === 'string' && errorText.trim()) {
    return errorText;
  }

  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail)) {
    const combined = detail
      .map((item) => String(item.msg || '').replace(/^Value error,\s*/i, ''))
      .filter(Boolean)
      .join(', ');

    if (combined) {
      return combined;
    }
  }

  if (apiError.message) {
    return apiError.message;
  }

  return fallback;
}
