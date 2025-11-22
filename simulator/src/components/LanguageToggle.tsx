import { FC } from 'react';
import { Globe } from 'lucide-react';
import { Language } from '../i18n/translations';

interface LanguageToggleProps {
  currentLang: Language;
  onToggle: (lang: Language) => void;
}

/**
 * Language Toggle Component
 *
 * Switches between English (en) and German (de)
 */
export const LanguageToggle: FC<LanguageToggleProps> = ({ currentLang, onToggle }) => {
  return (
    <button
      className="button ghost"
      onClick={() => onToggle(currentLang === 'en' ? 'de' : 'en')}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        minWidth: '80px'
      }}
    >
      <Globe size={16} />
      {currentLang === 'en' ? 'EN' : 'DE'}
    </button>
  );
};
