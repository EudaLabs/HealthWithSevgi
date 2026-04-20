import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

export type UploadErrorType =
  | 'invalid_format'
  | 'file_too_large'
  | 'dataset_too_small'
  | 'no_numeric_columns'
  | 'empty_file'
  | 'target_not_found'
  | 'dataset_unavailable'

interface Props {
  errorType: UploadErrorType
  onRetry: () => void
  onClose: () => void
}

const ERROR_CONFIG: Record<UploadErrorType, {
  title: string
  description: string
  detail: string
}> = {
  invalid_format: {
    title: 'Invalid file format',
    description: 'Only .csv files are supported.',
    detail: 'Please upload a CSV dataset to continue.',
  },
  file_too_large: {
    title: 'File too large',
    description: 'The selected dataset exceeds the allowed size.',
    detail: 'Maximum file size is 50 MB.',
  },
  dataset_too_small: {
    title: 'Dataset too small',
    description: 'The uploaded dataset does not contain enough records.',
    detail: 'At least 10 rows are required for meaningful analysis.',
  },
  no_numeric_columns: {
    title: 'No Numeric Columns Detected',
    description: 'The dataset must contain at least one numeric column.',
    detail: 'Numeric features are essential for machine learning analysis.',
  },
  empty_file: {
    title: 'Empty file',
    description: 'The uploaded file contains no data.',
    detail: 'Please upload a CSV file with at least 10 rows of patient data.',
  },
  target_not_found: {
    title: 'Target column not found',
    description: 'The expected target column was not found in your dataset.',
    detail: 'Upload your CSV and use the Column Mapper to select the correct target column.',
  },
  dataset_unavailable: {
    title: 'Dataset not available',
    description: 'The default dataset for this clinical domain has not been downloaded yet.',
    detail: 'Upload your own CSV file, or ask your administrator to populate the data cache for this specialty.',
  },
}

/**
 * Friendly modal for Step 2 upload/validation failures.
 * Maps a handful of known backend error codes (`invalid_format`,
 * `file_too_large`, `dataset_too_small`, …) to a clinician-readable
 * title, description, and actionable detail so users understand *why*
 * their CSV was rejected rather than seeing a stack trace.
 */
export default function ErrorModal({ errorType, onRetry, onClose }: Props) {
  const config = ERROR_CONFIG[errorType]

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 440, overflow: 'hidden' }}>
        <div className="error-modal-content">
          <div className="error-modal-icon">
            <AlertTriangle size={24} style={{ color: '#ffffff' }} />
          </div>
          <div className="error-modal-title">{config.title}</div>
          <div className="error-modal-desc">{config.description}</div>
          <div className={`error-modal-detail${errorType === 'invalid_format' || errorType === 'file_too_large' ? ' error-modal-detail-accent' : ''}`}>
            {config.detail}
          </div>

          {errorType === 'invalid_format' && (
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              <strong>Accepted Format:</strong> .csv
            </div>
          )}

          <button className="btn btn-primary" onClick={onRetry}>
            <RefreshCw size={15} /> Try Again
          </button>

          <div className="error-modal-requirements">
            <strong>Requirements:</strong> CSV format, max 50 MB, at least 10 rows, and at least 1 numeric column.
          </div>
        </div>
      </div>
    </div>
  )
}
