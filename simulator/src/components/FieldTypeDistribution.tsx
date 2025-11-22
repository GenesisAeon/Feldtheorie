import { FC, useMemo } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Legend
} from 'recharts';
import { DomainPreset } from '../types';
import { classifyFieldType, getAllFieldTypes } from '../utils/fieldTypeClassifier';
import { Language } from '../i18n/translations';

interface FieldTypeDistributionProps {
  activePresets: DomainPreset[];
  lang: Language;
}

/**
 * Field Type Distribution
 *
 * Shows how active domains are distributed across the five UTAC field types
 * based on their β values:
 *
 * - Weakly Coupled: β < 2.5
 * - High-Dimensional: β ∈ [2.5, 4.0]
 * - Strongly Coupled: β ∈ [4.0, 5.5]
 * - Physically Constrained: β ∈ [5.5, 10.0]
 * - Meta-Adaptive: β > 10.0
 */
export const FieldTypeDistribution: FC<FieldTypeDistributionProps> = ({
  activePresets,
  lang
}) => {
  const distributionData = useMemo(() => {
    const fieldTypes = getAllFieldTypes();
    const counts = new Map<string, number>();

    // Initialize counts
    fieldTypes.forEach(ft => counts.set(ft.type, 0));

    // Count active presets per field type
    activePresets.forEach(preset => {
      const beta = preset.analysis.beta;
      const fieldType = classifyFieldType(beta);
      counts.set(fieldType.type, (counts.get(fieldType.type) || 0) + 1);
    });

    // Build chart data
    return fieldTypes.map(ft => {
      const label = lang === 'en'
        ? ft.description.split(':')[0]
        : {
            'Weakly Coupled': 'Schwach Gekoppelt',
            'High-Dimensional': 'Hochdimensional',
            'Strongly Coupled': 'Stark Gekoppelt',
            'Physically Constrained': 'Physikalisch Beschränkt',
            'Meta-Adaptive': 'Meta-Adaptiv'
          }[ft.description.split(':')[0]] || ft.description.split(':')[0];

      return {
        name: label,
        count: counts.get(ft.type) || 0,
        color: ft.color,
        range: `β ∈ [${ft.beta_range[0]}, ${ft.beta_range[1] === Infinity ? '∞' : ft.beta_range[1]}]`
      };
    });
  }, [activePresets, lang]);

  const maxCount = useMemo(
    () => Math.max(...distributionData.map(d => d.count), 1),
    [distributionData]
  );

  return (
    <div className="chart-wrapper">
      <h2 className="section-title">
        {lang === 'en' ? 'Field Type Distribution' : 'Feldtyp-Verteilung'}
      </h2>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart
          data={distributionData}
          margin={{ top: 10, right: 30, left: 20, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="4 4" stroke="rgba(99,102,241,0.35)" />
          <XAxis
            dataKey="name"
            stroke="rgba(209,213,255,0.65)"
            angle={-30}
            textAnchor="end"
            height={80}
          />
          <YAxis
            stroke="rgba(209,213,255,0.65)"
            domain={[0, maxCount + 1]}
            allowDecimals={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(14,10,35,0.95)',
              border: '1px solid rgba(99,102,241,0.5)',
              borderRadius: '8px',
              padding: '12px'
            }}
            labelStyle={{ color: 'rgba(226,232,255,0.95)' }}
            itemStyle={{ color: 'rgba(196,181,253,0.95)' }}
            formatter={(value: number, name: string, props: any) => {
              return [
                `${value} domain${value !== 1 ? 's' : ''}`,
                props.payload.range
              ];
            }}
          />
          <Legend />
          <Bar dataKey="count" name={lang === 'en' ? 'Domains' : 'Domänen'}>
            {distributionData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="meta-footnote">
        {lang === 'en'
          ? 'Distribution of active domains across five UTAC field types based on β values. Field type classification explains 73.5% of β variance across domains (η²=0.735).'
          : 'Verteilung der aktiven Domänen über fünf UTAC-Feldtypen basierend auf β-Werten. Feldtyp-Klassifikation erklärt 73,5% der β-Varianz über Domänen hinweg (η²=0,735).'}
      </p>
    </div>
  );
};
