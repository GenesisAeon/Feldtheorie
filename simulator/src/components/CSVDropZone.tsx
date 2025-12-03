/**
 * CSV Drag & Drop Zone with Browser-based β/Θ Estimation
 *
 * Allows users to drag CSV files with time-series data to estimate
 * logistic parameters directly in the browser.
 *
 * References:
 * - FinalyzeVorschlägeGemini.txt:79-161 (CSV import spec)
 * - V6ToDorefresh.md Priority 10 (Simulator-UX)
 */

import { useCallback, useState } from 'react';
import { Upload, FileText, TrendingUp } from 'lucide-react';
import { processCSV, generateExampleCSV, RegressionResult } from '../utils/csvRegression';

interface CSVDropZoneProps {
  onDataProcessed: (result: RegressionResult) => void;
  language: 'en' | 'de';
}

export const CSVDropZone = ({ onDataProcessed, language }: CSVDropZoneProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [result, setResult] = useState<RegressionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const texts = {
    en: {
      title: 'CSV Data Import',
      dragHint: 'Drag & Drop CSV file here or click to upload',
      format: 'Format: time,resource (one value per line)',
      processing: 'Processing...',
      estimated: 'Estimated Parameters',
      beta: 'β (Steepness)',
      theta: 'Θ (Threshold)',
      rSquared: 'R² (Fit Quality)',
      dataPoints: 'Data Points',
      applyPreset: 'Apply as Custom Preset',
      downloadExample: 'Download Example CSV',
      error: 'Error'
    },
    de: {
      title: 'CSV-Daten-Import',
      dragHint: 'CSV-Datei hier ablegen oder klicken zum Hochladen',
      format: 'Format: Zeit,Ressource (ein Wert pro Zeile)',
      processing: 'Verarbeite...',
      estimated: 'Geschätzte Parameter',
      beta: 'β (Steilheit)',
      theta: 'Θ (Schwellenwert)',
      rSquared: 'R² (Anpassungsgüte)',
      dataPoints: 'Datenpunkte',
      applyPreset: 'Als Custom Preset übernehmen',
      downloadExample: 'Beispiel-CSV herunterladen',
      error: 'Fehler'
    }
  };

  const t = texts[language];

  const handleFile = useCallback((file: File) => {
    setError(null);
    setResult(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const csvText = e.target?.result as string;
        const processed = processCSV(csvText, file.name);

        if (processed.data.length < 2) {
          setError('Not enough data points (minimum 2 required)');
          return;
        }

        setResult(processed);
        onDataProcessed(processed);
      } catch (err) {
        setError(`${t.error}: ${err instanceof Error ? err.message : String(err)}`);
      }
    };
    reader.onerror = () => {
      setError('Failed to read file');
    };
    reader.readAsText(file);
  }, [onDataProcessed, t]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && (file.name.endsWith('.csv') || file.name.endsWith('.txt'))) {
      handleFile(file);
    } else {
      setError('Please drop a CSV or TXT file');
    }
  }, [handleFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  }, [handleFile]);

  const handleDownloadExample = useCallback(() => {
    const csvContent = generateExampleCSV();
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'example_logistic_data.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, []);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {t.title}
        </h3>
        <button
          onClick={handleDownloadExample}
          className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 flex items-center gap-1"
        >
          <FileText className="w-3 h-3" />
          {t.downloadExample}
        </button>
      </div>

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
          transition-colors duration-200
          ${isDragging
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
          }
        `}
      >
        <input
          type="file"
          accept=".csv,.txt"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
          {t.dragHint}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-500">
          {t.format}
        </p>
      </div>

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-700 dark:text-red-400">
            {error}
          </p>
        </div>
      )}

      {result && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg space-y-3">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-green-600 dark:text-green-400" />
            <h4 className="text-sm font-medium text-green-900 dark:text-green-100">
              {t.estimated}
            </h4>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-600 dark:text-gray-400">{t.beta}:</span>
              <span className="ml-2 font-mono font-medium text-gray-900 dark:text-gray-100">
                {result.beta.toFixed(2)}
              </span>
            </div>
            <div>
              <span className="text-gray-600 dark:text-gray-400">{t.theta}:</span>
              <span className="ml-2 font-mono font-medium text-gray-900 dark:text-gray-100">
                {result.theta.toFixed(2)}
              </span>
            </div>
            <div>
              <span className="text-gray-600 dark:text-gray-400">{t.rSquared}:</span>
              <span className="ml-2 font-mono font-medium text-gray-900 dark:text-gray-100">
                {result.r_squared.toFixed(3)}
              </span>
            </div>
            <div>
              <span className="text-gray-600 dark:text-gray-400">{t.dataPoints}:</span>
              <span className="ml-2 font-mono font-medium text-gray-900 dark:text-gray-100">
                {result.data.length}
              </span>
            </div>
          </div>

          {result.label && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              File: {result.label}
            </p>
          )}
        </div>
      )}
    </div>
  );
};
